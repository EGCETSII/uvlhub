"""HTTP integration tests for auth via the Flask test client."""
import pytest

pytestmark = pytest.mark.integration


def test_login_page_renders(test_client):
    response = test_client.get("/login")
    assert response.status_code == 200


def test_signup_page_renders(test_client):
    response = test_client.get("/signup/")
    assert response.status_code == 200


def test_signup_then_login_round_trip(test_client):
    signup = test_client.post(
        "/signup/",
        data={
            "email": "carol@example.com",
            "password": "carolpass",
            "name": "Carol",
            "surname": "Smith",
        },
        follow_redirects=False,
    )
    assert signup.status_code in (302, 303)

    # Logout to clear the session, then log back in with the new credentials.
    test_client.get("/logout", follow_redirects=False)
    login = test_client.post(
        "/login",
        data={"email": "carol@example.com", "password": "carolpass"},
        follow_redirects=False,
    )
    assert login.status_code in (302, 303)


def test_login_with_invalid_credentials_keeps_form(test_client):
    response = test_client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "wrong"},
        follow_redirects=False,
    )
    assert response.status_code == 200
