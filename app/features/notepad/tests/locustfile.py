from locust import HttpUser, TaskSet, between, task

from splent_framework.environment.host import get_host_for_locust_testing


class NotepadBehavior(TaskSet):
    @task
    def index(self):
        response = self.client.get("/notepad")
        if response.status_code != 200:
            print(f"Notepad index failed: {response.status_code}")


class NotepadUser(HttpUser):
    tasks = [NotepadBehavior]
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
