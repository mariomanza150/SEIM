"""Minimal Locust smoke load against the running Django app (CI performance job)."""

from locust import HttpUser, between, task


class SeimSmokeUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(3)
    def health(self):
        self.client.get("/health/", name="health")

    @task(1)
    def home(self):
        self.client.get("/", name="home")
