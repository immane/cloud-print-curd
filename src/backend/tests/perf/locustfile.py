from locust import HttpUser, between, task


class SmokeUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def health(self):
        self.client.get("/health")

    @task
    def prices(self):
        self.client.get("/v1/prices")
