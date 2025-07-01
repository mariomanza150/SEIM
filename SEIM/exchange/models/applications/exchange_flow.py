from viewflow import flow, this
from viewflow.base import Flow
from viewflow.contrib import django as django_nodes
from .exchange_process import ExchangeProcess

class ExchangeFlow(Flow):
    process_class = ExchangeProcess

    start = flow.Start(
        django_nodes.CreateProcessView,
        fields=["exchange"]
    ).Next(this.submit)

    submit = flow.View(
        django_nodes.UpdateProcessView,
        fields=["exchange"]
    ).Next(this.review)

    review = flow.If(lambda activation: activation.process.exchange.has_required_documents()) \
        .Then(this.approve) \
        .Else(this.reject)

    approve = flow.View(
        django_nodes.UpdateProcessView,
        fields=[]
    ).Next(this.complete)

    reject = flow.View(
        django_nodes.UpdateProcessView,
        fields=["exchange"]
    ).Next(this.end)

    complete = flow.Handler(
        this.on_complete
    ).Next(this.end)

    end = flow.End()

    def on_complete(self, activation):
        exchange = activation.process.exchange
        exchange.status = 'COMPLETED'
        exchange.completion_date = activation.process.finished
        exchange.save()

    # Optionally add on_reject, on_approve, etc. for notifications or side effects
