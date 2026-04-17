from __future__ import annotations

import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.utils import timezone

from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.parser import BpmnParser
from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer, DEFAULT_CONFIG
from SpiffWorkflow.task import TaskState

from exchange.models import Application, ApplicationStatus

from .models import WorkflowEvent, WorkflowInstance, WorkflowVersion


_SERIALIZER_REGISTRY = BpmnWorkflowSerializer.configure(DEFAULT_CONFIG)
_SERIALIZER = BpmnWorkflowSerializer(_SERIALIZER_REGISTRY)


def _extract_primary_process_id(bpmn_xml: str) -> str:
    root = ET.fromstring(bpmn_xml)
    # Find first <process id="..."> regardless of namespace
    for el in root.iter():
        if el.tag.lower().endswith("process") and el.attrib.get("id"):
            return el.attrib["id"]
    raise ValueError("BPMN XML must include a <process id=\"...\"> element.")


def _build_workflow_from_bpmn_xml(bpmn_xml: str) -> BpmnWorkflow:
    process_id = _extract_primary_process_id(bpmn_xml)
    with tempfile.NamedTemporaryFile(suffix=".bpmn", delete=False) as fp:
        fp.write(bpmn_xml.encode("utf-8"))
        path = fp.name
    parser = BpmnParser()
    parser.add_bpmn_files([path])
    spec = parser.get_spec(process_id)
    subprocess_specs = parser.get_subprocess_specs(process_id)
    return BpmnWorkflow(spec, subprocess_specs)


def _run_automatic_tasks(workflow: BpmnWorkflow) -> None:
    task = workflow.get_next_task(state=TaskState.READY, manual=False)
    while task is not None:
        task.run()
        task = workflow.get_next_task(state=TaskState.READY, manual=False)


def _ready_manual_tasks(workflow: BpmnWorkflow) -> list[dict]:
    out = []
    for t in workflow.get_tasks(state=TaskState.READY):
        if getattr(t.task_spec, "manual", False):
            out.append(
                {
                    "id": t.id,
                    "name": t.task_spec.name or "",
                    "spec_id": t.task_spec.id,
                }
            )
    return out


def _derive_application_status_from_tasks(
    application: Application, tasks: list[dict]
) -> Optional[ApplicationStatus]:
    """
    Convention: if any READY manual task has a name matching an ApplicationStatus.name,
    that status becomes the application's authoritative state.
    """
    if not tasks:
        return None
    names = [str(t.get("name") or "").strip() for t in tasks]
    for name in names:
        if not name:
            continue
        st = ApplicationStatus.objects.filter(name=name).first()
        if st:
            return st
    return None


@dataclass(frozen=True)
class WorkflowSnapshot:
    instance: WorkflowInstance
    available_actions: list[dict]


class WorkflowRuntimeService:
    """
    Runtime enforcement for application workflows.

    This MVP implementation:
    - Executes BPMN via SpiffWorkflow
    - Persists workflow state as JSON
    - Exposes READY manual tasks as available actions
    - Derives Application.status when task names match ApplicationStatus names
    """

    @staticmethod
    @transaction.atomic
    def ensure_instance(application: Application, user=None) -> WorkflowInstance:
        program = application.program
        wv: WorkflowVersion | None = getattr(program, "workflow_version", None)
        if not wv:
            raise ValueError("Program has no workflow_version configured.")

        inst = WorkflowInstance.objects.select_for_update().filter(application=application).first()
        if inst:
            return inst

        workflow = _build_workflow_from_bpmn_xml(wv.bpmn_xml)
        _run_automatic_tasks(workflow)
        tasks = _ready_manual_tasks(workflow)
        payload = {"spiff_json": _SERIALIZER.serialize_json(workflow)}

        inst = WorkflowInstance.objects.create(
            workflow_version=wv,
            application=application,
            engine_state=payload,
            current_tasks=tasks,
            status="running",
            last_event_at=timezone.now(),
        )
        WorkflowEvent.objects.create(
            instance=inst,
            event_type="instance_created",
            payload={"workflow_version": str(wv.id), "tasks": tasks},
            actor=user if getattr(user, "is_authenticated", False) else None,
        )
        st = _derive_application_status_from_tasks(application, tasks)
        if st and application.status_id != st.id:
            application.status = st
            application.save(update_fields=["status", "updated_at"])
        return inst

    @staticmethod
    def _load_workflow(instance: WorkflowInstance) -> BpmnWorkflow:
        if not instance.engine_state:
            # fall back to rebuild
            return _build_workflow_from_bpmn_xml(instance.workflow_version.bpmn_xml)
        raw = instance.engine_state.get("spiff_json") if isinstance(instance.engine_state, dict) else None
        if not raw:
            return _build_workflow_from_bpmn_xml(instance.workflow_version.bpmn_xml)
        return _SERIALIZER.deserialize_json(raw)

    @staticmethod
    @transaction.atomic
    def get_snapshot(application: Application, user=None) -> WorkflowSnapshot:
        inst = WorkflowRuntimeService.ensure_instance(application, user=user)
        return WorkflowSnapshot(instance=inst, available_actions=list(inst.current_tasks or []))

    @staticmethod
    @transaction.atomic
    def trigger_action(application: Application, action: str, user=None, payload: Optional[dict] = None) -> WorkflowSnapshot:
        inst = WorkflowRuntimeService.ensure_instance(application, user=user)
        workflow = WorkflowRuntimeService._load_workflow(inst)

        _run_automatic_tasks(workflow)
        ready = [t for t in workflow.get_tasks(state=TaskState.READY) if getattr(t.task_spec, "manual", False)]
        action = str(action or "").strip()
        if not action:
            raise ValueError("Action is required.")

        target = None
        for t in ready:
            if str(t.id) == action or str(t.task_spec.id) == action or str(t.task_spec.name) == action:
                target = t
                break

        if target is None:
            available = [{"id": t.id, "name": t.task_spec.name, "spec_id": t.task_spec.id} for t in ready]
            raise ValueError(f"Action not available: {action}. Available: {available}")

        if payload:
            try:
                target.set_data(payload)
            except Exception:
                # ignore payload mapping in MVP
                pass

        target.complete()
        _run_automatic_tasks(workflow)

        tasks = _ready_manual_tasks(workflow)
        inst.engine_state = {"spiff_json": _SERIALIZER.serialize_json(workflow)}
        inst.current_tasks = tasks
        inst.last_event_at = timezone.now()
        inst.save(update_fields=["engine_state", "current_tasks", "last_event_at", "updated_at"])

        WorkflowEvent.objects.create(
            instance=inst,
            event_type="action",
            payload={"action": action, "data": payload or {}, "tasks": tasks},
            actor=user if getattr(user, "is_authenticated", False) else None,
        )

        st = _derive_application_status_from_tasks(application, tasks)
        if st and application.status_id != st.id:
            application.status = st
            application.save(update_fields=["status", "updated_at"])

        return WorkflowSnapshot(instance=inst, available_actions=tasks)

