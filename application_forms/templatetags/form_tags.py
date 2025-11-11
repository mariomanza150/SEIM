"""
Template tags for application forms rendering.
"""

import json

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary."""
    if not dictionary:
        return None
    return dictionary.get(key, '')


@register.filter
def in_list(value, list_string):
    """Check if value is in a list."""
    if not list_string:
        return False
    if isinstance(list_string, list):
        return value in list_string
    return False


@register.filter
def default_dict(value):
    """Return empty dict if value is None."""
    return value if value is not None else {}


@register.filter
def jsonify(value):
    """Convert Python object to JSON string."""
    if value is None:
        return '{}'
    try:
        return json.dumps(value)
    except (TypeError, ValueError):
        return '{}'


@register.inclusion_tag('includes/dynamic_form_field.html')
def render_dynamic_field(field_name, field_config, required_fields, form_data=None):
    """
    Render a single dynamic form field.

    Args:
        field_name: Name of the field
        field_config: Field configuration from schema
        required_fields: List of required field names
        form_data: Existing form data (optional)

    Returns:
        Template context dict
    """
    if form_data is None:
        form_data = {}

    return {
        'field_name': field_name,
        'field_config': field_config,
        'is_required': field_name in required_fields,
        'field_value': form_data.get(field_name, ''),
        'field_type': field_config.get('type', 'string'),
        'field_format': field_config.get('format', ''),
        'field_title': field_config.get('title', field_name),
        'field_description': field_config.get('description', ''),
        'field_placeholder': field_config.get('placeholder', ''),
        'field_enum': field_config.get('enum', []),
        'field_min': field_config.get('minimum'),
        'field_max': field_config.get('maximum'),
        'field_maxlength': field_config.get('maxLength', 200),
    }


@register.simple_tag
def get_form_field_value(form_data, field_name, default=''):
    """
    Get value from form data dict safely.

    Args:
        form_data: Dict containing form data
        field_name: Name of the field to get
        default: Default value if not found

    Returns:
        Field value or default
    """
    if not form_data:
        return default
    return form_data.get(field_name, default)


@register.filter
def is_in(value, container):
    """Check if value is in container."""
    if not container:
        return False
    try:
        return value in container
    except (TypeError, ValueError):
        return False

