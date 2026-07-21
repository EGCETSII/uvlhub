from locust import HttpUser, TaskSet, between, task
from splent_framework.environment.host import get_host_for_locust_testing


class PublicIndexBehavior(TaskSet):
    """Landing page traffic.

    The public feature exposes a single endpoint, so a single task is all there
    is to load. It is however the heaviest page of the application: rendering it
    aggregates the latest synchronized datasets plus six independent counters
    (dataset count, feature model count, downloads and views for both).
    """

    @task
    def index(self):
        response = self.client.get("/", name="/")
        if response.status_code != 200:
            print(f"Public index failed: {response.status_code}")


class PublicUser(HttpUser):
    tasks = [PublicIndexBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
