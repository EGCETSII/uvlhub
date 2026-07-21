from locust import HttpUser, TaskSet, between, task
from splent_framework.environment.host import get_host_for_locust_testing
from splent_framework.locust.common import fake, get_csrf_token

# Seeded account used by the read-only login traffic. Never mutated by these tasks.
SEEDED_EMAIL = "user1@example.com"
SEEDED_PASSWORD = "1234"


class AuthBehavior(TaskSet):
    """Anonymous traffic against the authentication endpoints.

    Every task starts from a guaranteed logged-out state because both /login and
    /signup/ redirect authenticated users to the landing page, which would leave
    the response without a CSRF token.
    """

    def on_start(self):
        self.logout()

    def logout(self):
        response = self.client.get("/logout", name="/logout")
        if response.status_code != 200:
            print(f"Logout failed: {response.status_code}")

    def csrf_token_from(self, response):
        try:
            return get_csrf_token(response)
        except ValueError:
            print("CSRF token not present in the response")
            return None

    @task(4)
    def view_login_form(self):
        self.logout()
        response = self.client.get("/login", name="/login [GET]")
        if response.status_code != 200:
            print(f"Login form failed: {response.status_code}")

    @task(2)
    def view_signup_form(self):
        self.logout()
        response = self.client.get("/signup/", name="/signup/ [GET]")
        if response.status_code != 200:
            print(f"Signup form failed: {response.status_code}")

    @task(4)
    def login_with_seeded_user(self):
        self.logout()
        response = self.client.get("/login", name="/login [GET]")
        csrf_token = self.csrf_token_from(response)
        if csrf_token is None:
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

        self.logout()

    @task(2)
    def login_with_invalid_credentials(self):
        """Exercise the failed-credentials branch, which re-renders the form."""
        self.logout()
        response = self.client.get("/login", name="/login [GET]")
        csrf_token = self.csrf_token_from(response)
        if csrf_token is None:
            return

        response = self.client.post(
            "/login",
            name="/login [POST] invalid credentials",
            data={
                "email": fake.email(),
                "password": fake.password(),
                "csrf_token": csrf_token,
            },
        )
        if response.status_code != 200:
            print(f"Invalid login attempt returned an unexpected status: {response.status_code}")

    @task(1)
    def signup_new_account(self):
        """Register a brand new account with generated data.

        Only additive: it never touches the seeded users.
        """
        self.logout()
        response = self.client.get("/signup/", name="/signup/ [GET]")
        csrf_token = self.csrf_token_from(response)
        if csrf_token is None:
            return

        response = self.client.post(
            "/signup/",
            name="/signup/ [POST]",
            data={
                "name": fake.first_name(),
                "surname": fake.last_name(),
                "email": fake.unique.email(),
                "password": fake.password(length=12),
                "csrf_token": csrf_token,
            },
        )
        if response.status_code != 200:
            print(f"Signup failed: {response.status_code}")

        self.logout()


class AuthUser(HttpUser):
    tasks = [AuthBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
