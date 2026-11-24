"""Print outgoing email quota usage and deferred outbox counts."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from core.email.quota import remaining_headroom
from core.models import DeferredEmail


class Command(BaseCommand):
    help = (
        "Show today's email send count, remaining normal/priority headroom, "
        "month total, and pending deferred counts by priority."
    )

    def handle(self, *args, **options):
        snap = remaining_headroom()
        pending = DeferredEmail.objects.filter(status=DeferredEmail.STATUS_PENDING)
        pending_high = pending.filter(priority=DeferredEmail.PRIORITY_HIGH).count()
        pending_normal = pending.filter(priority=DeferredEmail.PRIORITY_NORMAL).count()
        failed = DeferredEmail.objects.filter(
            status=DeferredEmail.STATUS_FAILED
        ).count()

        lines = [
            f"Quota timezone: {snap['timezone']}",
            f"Usage date: {snap['usage_date']}",
            f"Sent today: {snap['sent_today']}",
            f"Daily limit: {snap['daily_limit']}",
            f"Priority reserve: {snap['priority_reserve']}",
            f"Normal daily cap: {snap['normal_daily_cap']}",
            f"Normal remaining: {snap['normal_remaining']}",
            f"Priority remaining: {snap['priority_remaining']}",
            f"Daily remaining: {snap['daily_remaining']}",
            f"Month total: {snap['month_total']}",
            f"Monthly limit: {snap['monthly_limit']}",
            f"Monthly remaining: {snap['monthly_remaining']}",
            f"Pending deferred (high): {pending_high}",
            f"Pending deferred (normal): {pending_normal}",
            f"Failed deferred: {failed}",
        ]
        self.stdout.write("\n".join(lines) + "\n")
