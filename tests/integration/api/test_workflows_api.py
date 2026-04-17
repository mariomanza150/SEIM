"""
Integration tests for workflow configuration + runtime APIs.
"""

import pytest
from django.urls import reverse
from rest_framework import status

from tests.utils import APITestCase
from workflows.models import WorkflowDefinition, WorkflowVersion


def _simple_bpmn_with_manual_task(task_name: str = "submitted") -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
  id="Definitions_1"
  targetNamespace="http://seim.local/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Start" />
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="UserTask_1" />
    <bpmn:userTask id="UserTask_1" name="{task_name}" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1">
        <dc:Bounds x="180" y="100" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="UserTask_1_di" bpmnElement="UserTask_1">
        <dc:Bounds x="260" y="78" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <dc:Bounds x="0" y="0" width="0" height="0" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
"""


@pytest.mark.integration
@pytest.mark.api
class TestWorkflowsAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.workflows_url = reverse("api:workflow-definition-list")

    def test_workflows_requires_admin_role(self):
        student = self.create_user(role="student")
        self.authenticate_user(student)
        resp = self.client.get(self.workflows_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_workflow_and_versions_and_publish(self):
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        resp = self.client.post(
            self.workflows_url,
            {"name": "App Workflow", "description": "Test", "is_active": True},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        wf_id = resp.data["id"]

        versions_url = reverse("api:workflow-definition-versions", args=[wf_id])
        vresp = self.client.post(
            versions_url, {"bpmn_xml": _simple_bpmn_with_manual_task("submitted")}, format="json"
        )
        self.assertEqual(vresp.status_code, status.HTTP_201_CREATED)
        version_id = vresp.data["id"]

        validate_url = reverse("api:workflow-version-validate-bpmn", args=[version_id])
        presp = self.client.post(validate_url, format="json")
        self.assertEqual(presp.status_code, status.HTTP_200_OK)
        self.assertEqual(presp.data["valid"], True)

        publish_url = reverse("api:workflow-version-publish", args=[version_id])
        pubresp = self.client.post(publish_url, format="json")
        self.assertEqual(pubresp.status_code, status.HTTP_200_OK)
        self.assertEqual(pubresp.data["status"], WorkflowVersion.Status.PUBLISHED)

    def test_application_workflow_snapshot_and_action(self):
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        wf = WorkflowDefinition.objects.create(name="WF", slug="wf", is_active=True)
        wv = WorkflowVersion.objects.create(
            definition=wf,
            version=1,
            status=WorkflowVersion.Status.PUBLISHED,
            bpmn_xml=_simple_bpmn_with_manual_task("submitted"),
            created_by=admin,
        )

        program = self.create_program(name="Program WF", workflow_version=wv)
        app = self.create_application(program=program, status_name="draft")

        snap_url = reverse("api:application-workflow-snapshot", args=[app.id])
        snap = self.client.get(snap_url)
        self.assertEqual(snap.status_code, status.HTTP_200_OK)
        self.assertIn("instance", snap.data)
        self.assertIn("available_actions", snap.data)

        actions = snap.data["available_actions"]
        # Expect a manual task surfaced as an action
        self.assertTrue(isinstance(actions, list))
        self.assertTrue(actions)

        action_url = reverse("api:application-workflow-action", args=[app.id])
        act = self.client.post(action_url, {"action": actions[0]["id"], "payload": {}}, format="json")
        self.assertEqual(act.status_code, status.HTTP_200_OK)

