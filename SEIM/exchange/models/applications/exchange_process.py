from django.db import models
from viewflow.models import Process
from .exchange import Exchange

class ExchangeProcess(Process):
    exchange = models.OneToOneField(Exchange, on_delete=models.CASCADE, related_name='flow_process')
    # Add process-level fields if needed, e.g. started_by, started_at, etc.
