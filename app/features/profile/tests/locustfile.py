from locust import HttpUser, TaskSet, between, task
from splent_framework.environment.host import get_host_for_locust_testing
from splent_framework.locust.common import get_csrf_token

# Seeded account. Only read traffic is issued on its behalf, it is never mutated.
SEEDED_EMAIL = "user1@example.com"
SEEDED_PASSWORD = "1234"


class ProfileBehavior(TaskSet):
    """Authenticated traffic over the profile pages.

    Both endpoints are behind login_required, so the session is established once
    in on_start and reused, which is what a real browsing session does.

    POST /profile/edit is deliberately excluded: it would overwrite the profile
    of the seeded user on a shared development database.
    """

    def on_start(self):
        self.login()

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

    @task(5)
    def view_summary(self):
        """Landing page of the profile: paginated list of the user datasets."""
        response = self.client.get("/profile/summary", name="/profile/summary")
        if response.status_code != 200:
            print(f"Profile summary failed: {response.status_code}")

    @task(2)
    def browse_summary_pages(self):
        for page in (2, 3):
            response = self.client.get(
                "/profile/summary",
                params={"page": page},
                name="/profile/summary?page=[n]",
            )
            if response.status_code != 200:
                print(f"Profile summary page {page} failed: {response.status_code}")

    @task(3)
    def open_edit_form(self):
        response = self.client.get("/profile/edit", name="/profile/edit [GET]")
        if response.status_code != 200:
            print(f"Profile edit form failed: {response.status_code}")


class ProfileUser(HttpUser):
    tasks = [ProfileBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
