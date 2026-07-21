from locust import HttpUser, TaskSet, between, task
from splent_framework.environment.host import get_host_for_locust_testing


class TeamBehavior(TaskSet):
    """Static informational page about the institutions behind the project.

    The team feature exposes a single GET endpoint, so a single task covers it.
    """

    @task
    def index(self):
        response = self.client.get("/team", name="/team")
        if response.status_code != 200:
            print(f"Team index failed: {response.status_code}")


class TeamUser(HttpUser):
    tasks = [TeamBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
