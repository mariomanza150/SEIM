import logging

from celery import shared_task
from django.core.cache import cache
from django.core.management import call_command

logger = logging.getLogger(__name__)
RESET_LOCK_KEY = "qa:reset_demo_data:running"


@shared_task(bind=True, soft_time_limit=900)
def reset_demo_data_task(self):
    try:
        call_command("reset_demo_data", verbosity=0)
        logger.info("Demo data reset finished")
        return "ok"
    finally:
        cache.delete(RESET_LOCK_KEY)
