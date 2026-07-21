import random

from locust import HttpUser, TaskSet, between, task
from splent_framework.environment.host import get_host_for_locust_testing
from splent_framework.locust.common import get_csrf_token

# Seeded account. Only read traffic is issued on its behalf, it is never mutated.
SEEDED_EMAIL = "user1@example.com"
SEEDED_PASSWORD = "1234"

# Fallback used when the catalog cannot be discovered through the public API.
FALLBACK_DATASET_IDS = [1]
FALLBACK_DOIS = ["10.1234/dataset1"]


class DatasetBehavior(TaskSet):
    """Browsing traffic over the dataset feature.

    Covers the two public read paths (the DOI landing page and the REST API),
    the two authenticated pages (own dataset list and the upload form) and the
    archive download.

    Deliberately excluded, because they mutate state on a shared dev database:
    POST /dataset/upload (creates datasets), POST /dataset/file/upload and
    POST /dataset/file/delete (write and remove files in the user temp folder).
    """

    def on_start(self):
        self.dataset_ids = list(FALLBACK_DATASET_IDS)
        self.dois = list(FALLBACK_DOIS)
        self.login()
        self.discover_catalog()

    def login(self):
        response = self.client.get("/login", name="/login [GET]")
        try:
            csrf_token = get_csrf_token(response)
        except ValueError:
            print("Could not read the CSRF token from the login form")
            return

        response = self.client.post(
            "/login",
            name="/login [POST]",
            data={
                "email": SEEDED_EMAIL,
                "password": SEEDED_PASSWORD,
                "csrf_token": csrf_token,
            },
        )
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")

    def discover_catalog(self):
        """Read the seeded dataset ids and DOIs instead of hardcoding them."""
        response = self.client.get("/api/v1/datasets/", name="/api/v1/datasets/")
        if response.status_code != 200:
            print(f"Dataset API listing failed: {response.status_code}")
            return

        try:
            items = response.json().get("items", [])
        except ValueError:
            print("Dataset API listing did not return JSON")
            return

        dataset_ids = [item["dataset_id"] for item in items if item.get("dataset_id")]
        dois = [item["doi"].split("/doi/", 1)[1] for item in items if "/doi/" in (item.get("doi") or "")]

        if dataset_ids:
            self.dataset_ids = dataset_ids
        if dois:
            self.dois = dois

    @task(6)
    def view_dataset_by_doi(self):
        doi = random.choice(self.dois)
        response = self.client.get(f"/doi/{doi}/", name="/doi/[doi]/")
        if response.status_code != 200:
            print(f"Dataset DOI page failed: {response.status_code}")

    @task(4)
    def list_own_datasets(self):
        response = self.client.get("/dataset/list", name="/dataset/list")
        if response.status_code != 200:
            print(f"Dataset list failed: {response.status_code}")

    @task(3)
    def api_list_datasets(self):
        response = self.client.get("/api/v1/datasets/", name="/api/v1/datasets/")
        if response.status_code != 200:
            print(f"Dataset API listing failed: {response.status_code}")

    @task(3)
    def api_get_dataset(self):
        dataset_id = random.choice(self.dataset_ids)
        response = self.client.get(f"/api/v1/datasets/{dataset_id}", name="/api/v1/datasets/[id]")
        if response.status_code != 200:
            print(f"Dataset API detail failed: {response.status_code}")

    @task(2)
    def open_upload_form(self):
        response = self.client.get("/dataset/upload", name="/dataset/upload [GET]")
        if response.status_code != 200:
            print(f"Dataset upload form failed: {response.status_code}")

    @task(1)
    def download_dataset(self):
        """Heaviest read path: it zips the whole dataset directory on the fly."""
        dataset_id = random.choice(self.dataset_ids)
        response = self.client.get(f"/dataset/download/{dataset_id}", name="/dataset/download/[id]")
        if response.status_code != 200:
            print(f"Dataset download failed: {response.status_code}")


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
