from django import template

register = template.Library()

@register.filter
def status_color(status):
    """Map application status to Bootstrap color classes."""
    mapping = {
        'draft': 'secondary',
        'submitted': 'primary',
        'under_review': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'withdrawn': 'dark',
    }
    return mapping.get(status, 'secondary')

@register.filter
def document_status_color(status):
    """Map document status to Bootstrap color classes."""
    mapping = {
        'pending': 'warning',
        'validated': 'success',
        'rejected': 'danger',
        'resubmission_required': 'info',
    }
    return mapping.get(status, 'secondary')

@register.filter
def validation_status_color(status):
    """Map validation status to Bootstrap color classes."""
    mapping = {
        'pending': 'warning',
        'validated': 'success',
        'rejected': 'danger',
        'resubmission_required': 'info',
    }
    return mapping.get(status, 'secondary')
