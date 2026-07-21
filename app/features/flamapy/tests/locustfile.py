import random

from locust import HttpUser, TaskSet, between, task
from splent_framework.environment.host import get_host_for_locust_testing

# Used only if the seeded catalog cannot be discovered through the public API.
FALLBACK_FILE_IDS = [1]


class FlamapyBehavior(TaskSet):
    """CPU bound traffic over the UVL analysis and export endpoints.

    Every task here parses the UVL file from disk with ANTLR, so this is the
    most expensive feature of the application per request. The three export
    formats each add a transformation on top of the parse, and the CNF one also
    runs the SAT conversion, so it is the heaviest of the three.

    All endpoints are read-only: they write their output to a temporary file
    that the route removes right after the response is sent.
    """

    def on_start(self):
        self.file_ids = list(FALLBACK_FILE_IDS)
        self.discover_files()

    def discover_files(self):
        """Read the seeded hubfile ids instead of hardcoding them."""
        response = self.client.get("/api/v1/datasets/", name="/api/v1/datasets/")
        if response.status_code != 200:
            print(f"Dataset API listing failed: {response.status_code}")
            return

        try:
            items = response.json().get("items", [])
        except ValueError:
            print("Dataset API listing did not return JSON")
            return

        file_ids = [file["file_id"] for item in items for file in item.get("files", []) if file.get("file_id")]
        if file_ids:
            self.file_ids = file_ids

    def random_file_id(self):
        return random.choice(self.file_ids)

    @task(6)
    def check_uvl(self):
        """Syntax validation, triggered by the UI whenever a model is opened."""
        response = self.client.get(f"/flamapy/check_uvl/{self.random_file_id()}", name="/flamapy/check_uvl/[id]")
        if response.status_code != 200:
            print(f"UVL check failed: {response.status_code}")

    @task(3)
    def valid(self):
        response = self.client.get(f"/flamapy/valid/{self.random_file_id()}", name="/flamapy/valid/[id]")
        if response.status_code != 200:
            print(f"UVL valid endpoint failed: {response.status_code}")

    @task(2)
    def export_to_glencoe(self):
        response = self.client.get(f"/flamapy/to_glencoe/{self.random_file_id()}", name="/flamapy/to_glencoe/[id]")
        if response.status_code != 200:
            print(f"Glencoe export failed: {response.status_code}")

    @task(2)
    def export_to_splot(self):
        response = self.client.get(f"/flamapy/to_splot/{self.random_file_id()}", name="/flamapy/to_splot/[id]")
        if response.status_code != 200:
            print(f"SPLOT export failed: {response.status_code}")

    @task(1)
    def export_to_cnf(self):
        response = self.client.get(f"/flamapy/to_cnf/{self.random_file_id()}", name="/flamapy/to_cnf/[id]")
        if response.status_code != 200:
            print(f"CNF export failed: {response.status_code}")


class FlamapyUser(HttpUser):
    tasks = [FlamapyBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
