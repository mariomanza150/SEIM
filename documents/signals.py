"""Signals for document-type prefill active-filter auto-inclusion."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from accounts.models import Profile

from .prefill_filters import apply_prefill_active_filters_for_user

User = get_user_model()


def _schedule_prefill_auto_include(user_id) -> None:
    if user_id is None:
        return

    def _run():
        apply_prefill_active_filters_for_user(user_id)

    transaction.on_commit(_run)


@receiver(post_save, sender=User)
def prefill_auto_include_on_user_save(sender, instance, **kwargs):
    """Re-evaluate active filters when email / active flag may have changed."""
    _schedule_prefill_auto_include(instance.pk)


@receiver(post_save, sender=Profile)
def prefill_auto_include_on_profile_save(sender, instance, **kwargs):
    """Re-evaluate when unidad / school (or other profile attrs) change."""
    _schedule_prefill_auto_include(getattr(instance, "user_id", None))


@receiver(m2m_changed, sender=User.roles.through)  # type: ignore[attr-defined]
def prefill_auto_include_on_role_change(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    """Include newly assigned students when they gain the student role."""
    if action not in ("post_add",):
        return
    if reverse:
        # Role.users.add(...) — pk_set are user ids
        for user_id in pk_set or ():
            _schedule_prefill_auto_include(user_id)
        return
    # User.roles.add(...) — only care when student role was added
    from accounts.models import Role

    student_ids = set(
        Role.objects.filter(name="student", pk__in=(pk_set or ())).values_list(
            "id", flat=True
        )
    )
    if not student_ids:
        return
    _schedule_prefill_auto_include(instance.pk)
