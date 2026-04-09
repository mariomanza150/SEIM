"""Evaluate ``x-seim-visibleWhen`` / ``visible_when`` rules (answers + optional program/coordinator context)."""

from __future__ import annotations

from typing import Any, Mapping

VISIBLE_WHEN_KEY = "x-seim-visibleWhen"


def _context_constraints_pass(rule: Mapping[str, Any], context: Mapping[str, Any] | None) -> bool:
    """Program / coordinator predicates. Missing context fails checks that need it."""
    ctx = context or {}

    if "program_id" in rule:
        try:
            want = int(rule["program_id"])
        except (TypeError, ValueError):
            return False
        cur = ctx.get("program_id")
        if cur is None:
            return False
        try:
            if int(cur) != want:
                return False
        except (TypeError, ValueError):
            return False

    if "program_id_in" in rule:
        raw = rule["program_id_in"]
        if not isinstance(raw, list):
            return False
        allowed: list[int] = []
        for x in raw:
            try:
                allowed.append(int(x))
            except (TypeError, ValueError):
                continue
        cur = ctx.get("program_id")
        if cur is None:
            return False
        try:
            if int(cur) not in allowed:
                return False
        except (TypeError, ValueError):
            return False

    if rule.get("has_assigned_coordinator") is True:
        if not ctx.get("has_assigned_coordinator"):
            return False
    if rule.get("has_assigned_coordinator") is False:
        if ctx.get("has_assigned_coordinator"):
            return False

    if rule.get("staff_only") is True:
        vr = set(ctx.get("viewer_roles") or [])
        if not (("coordinator" in vr) or ("admin" in vr)):
            return False

    if "roles_any" in rule:
        need = rule["roles_any"]
        if not isinstance(need, list) or not need:
            return False
        vr = {str(x) for x in (ctx.get("viewer_roles") or [])}
        allowed = {str(x) for x in need}
        if not vr.intersection(allowed):
            return False

    return True


def visible_when_satisfied(
    rule: Any,
    responses: Mapping[str, Any],
    context: Mapping[str, Any] | None = None,
) -> bool:
    """
    Rule may combine optional **context** keys (application/program state) with optional **field** keys.

    Context (all optional on the rule object):
      - ``program_id`` — int, must match ``context["program_id"]``
      - ``program_id_in`` — list of ints, program id must be listed
      - ``has_assigned_coordinator`` — ``true`` / ``false`` requires matching ``context["has_assigned_coordinator"]``
      - ``staff_only`` — ``true`` requires ``coordinator`` or ``admin`` in ``context["viewer_roles"]``
      - ``roles_any`` — non-empty list of role name strings overlapping ``viewer_roles``

    Field-based (requires string ``field`` when used):
      - ``equals``, ``notEquals``, ``in``, ``truthy`` — same as before
    """
    if not rule or not isinstance(rule, dict):
        return True
    if not _context_constraints_pass(rule, context):
        return False

    field_name = rule.get("field")
    if not field_name or not isinstance(field_name, str):
        return True
    key = field_name.strip()
    value = responses.get(key)

    if "equals" in rule:
        return value == rule["equals"]
    if "notEquals" in rule:
        return value != rule["notEquals"]
    if "in" in rule:
        choices = rule["in"]
        if not isinstance(choices, list):
            return False
        return value in choices
    if rule.get("truthy") is True:
        return _is_truthy(value)
    if rule.get("truthy") is False:
        return not _is_truthy(value)
    return True


def iter_visible_steps_from_form_type(
    form_type: Any,
    responses: Mapping[str, Any],
    context: Mapping[str, Any] | None = None,
):
    """Yield step layout rows that pass ``visible_when``."""
    if not form_type or not form_type.is_multi_step():
        return
    for step in form_type.get_multi_step_layout():
        rule = step.get("visible_when") or step.get("visibleWhen")
        if visible_when_satisfied(rule, responses, context):
            yield step


def field_effective_visible(
    form_type: Any,
    field_name: str,
    responses: Mapping[str, Any],
    context: Mapping[str, Any] | None = None,
) -> bool:
    """
    Field is shown and validated when its property-level rule passes and (for multi-step)
    it belongs to at least one visible step.
    """
    schema = getattr(form_type, "schema", None) or {}
    properties = schema.get("properties") or {}
    cfg = properties.get(field_name)
    if cfg is None:
        return False
    if not field_is_visible(cfg, responses, context):
        return False
    if not form_type.is_multi_step():
        return True
    for step in iter_visible_steps_from_form_type(form_type, responses, context):
        if field_name in (step.get("field_names") or []):
            return True
    return False


def field_is_visible(
    field_config: Mapping[str, Any],
    responses: Mapping[str, Any],
    context: Mapping[str, Any] | None = None,
) -> bool:
    if not field_config or not isinstance(field_config, dict):
        return True
    rule = field_config.get(VISIBLE_WHEN_KEY) or field_config.get("x_seim_visibleWhen")
    return visible_when_satisfied(rule, responses, context)


def _is_truthy(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, list):
        return len(value) > 0
    return True
