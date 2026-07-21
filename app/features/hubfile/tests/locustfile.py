import random

from locust import HttpUser, TaskSet, between, task
from splent_framework.environment.host import get_host_for_locust_testing

# Used only if the seeded catalog cannot be discovered through the public API.
FALLBACK_FILE_IDS = [1]


class HubfileBehavior(TaskSet):
    """Traffic over the two hubfile endpoints.

    Viewing is what the dataset page does on every expand, so it is by far the
    most frequent operation; downloading a single UVL file is rarer. Both write
    an access record row, which is exactly what they do in production, and
    neither of them alters the stored files.
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

    @task(8)
    def view_file(self):
        file_id = random.choice(self.file_ids)
        response = self.client.get(f"/file/view/{file_id}", name="/file/view/[id]")
        if response.status_code != 200:
            print(f"File view failed: {response.status_code}")
            return

        try:
            payload = response.json()
        except ValueError:
            print("File view did not return JSON")
            return

        if not payload.get("success"):
            print(f"File view reported an error: {payload.get('error')}")

    @task(2)
    def download_file(self):
        file_id = random.choice(self.file_ids)
        response = self.client.get(f"/file/download/{file_id}", name="/file/download/[id]")
        if response.status_code != 200:
            print(f"File download failed: {response.status_code}")


class HubfileUser(HttpUser):
    tasks = [HubfileBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
