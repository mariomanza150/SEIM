"""Minimal Locust smoke load against the running Django app (CI performance job)."""

from locust import HttpUser, between, task


class SeimSmokeUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(3)
    def health(self):
        # Liveness probe: no Postgres/Redis round-trips per request.
        self.client.get("/health/live/", name="health_live")

    @task(1)
    def home(self):
        self.client.get("/", name="home")
