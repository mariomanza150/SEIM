"""
Merge reusable step templates into FormType schema / steps / ui_schema.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError

from .models import FormStepTemplate, FormType


def apply_step_template_to_form_type(
    form_type: FormType,
    template: FormStepTemplate,
    *,
    step_key: str | None = None,
) -> FormType:
    """
    Append template fields to form_type.schema.properties, merge ui_schema,
    and append a step_definitions entry.

    Raises ValidationError on field key collisions, duplicate step keys, or invalid template data.
    """
    if not template.is_active:
        raise ValidationError("This step template is not active.")

    props = template.schema_properties or {}
    if not isinstance(props, dict) or not props:
        raise ValidationError("Template schema_properties must be a non-empty object.")

    schema = dict(form_type.schema or {})
    existing_props = dict(schema.get("properties") or {})
    overlap = set(existing_props.keys()) & set(props.keys())
    if overlap:
        raise ValidationError(
            "Form already defines field(s): " + ", ".join(sorted(overlap))
        )

    schema.setdefault("type", "object")
    merged_props = {**existing_props, **props}
    schema["properties"] = merged_props

    req = list(schema.get("required") or [])
    req_set = set(req)
    for name in template.required_field_names or []:
        if name not in props:
            raise ValidationError(
                f'required_field_names entry "{name}" is not in schema_properties.'
            )
        if name not in req_set:
            req.append(name)
            req_set.add(name)
    schema["required"] = req
    form_type.schema = schema

    ui = dict(form_type.ui_schema or {})
    frag = template.ui_schema_fragment or {}
    if not isinstance(frag, dict):
        raise ValidationError("ui_schema_fragment must be an object.")
    for k, v in frag.items():
        if k in ui and isinstance(ui[k], dict) and isinstance(v, dict):
            ui[k] = {**ui[k], **v}
        else:
            ui[k] = v
    form_type.ui_schema = ui

    steps = list(form_type.step_definitions or [])
    used_keys = {str(s.get("key", "")) for s in steps}
    final_key = (step_key or template.default_step_key or "").strip()
    if not final_key:
        raise ValidationError("Provide step_key or set default_step_key on the template.")
    if final_key in used_keys:
        raise ValidationError(f'Step key "{final_key}" already exists on this form.')

    doc_ids = []
    raw_docs = template.required_document_type_ids or []
    if raw_docs is not None and not isinstance(raw_docs, list):
        raise ValidationError("required_document_type_ids must be a list.")
    for x in raw_docs or []:
        try:
            doc_ids.append(int(x))
        except (TypeError, ValueError):
            raise ValidationError("required_document_type_ids must contain integers.") from None

    field_names = list(props.keys())
    step_row = {
        "key": final_key,
        "title": (template.step_title or final_key).strip() or final_key,
        "field_names": field_names,
    }
    if doc_ids:
        step_row["required_document_type_ids"] = doc_ids

    steps.append(step_row)
    form_type.step_definitions = steps

    form_type.full_clean()
    form_type.save()
    return form_type
