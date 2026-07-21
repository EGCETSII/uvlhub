"""Repository-level tests for auth — UserRepository against the DB."""
import pytest

from app.features.auth.repositories import UserRepository

pytestmark = pytest.mark.repository


def test_get_by_email_returns_none_when_absent(test_app):
    with test_app.app_context():
        assert UserRepository().get_by_email("ghost@example.com") is None


def test_create_then_get_by_email(test_app):
    with test_app.app_context():
        repo = UserRepository()
        repo.create(email="dave@example.com", password="davepass")
        found = repo.get_by_email("dave@example.com")
        assert found is not None
        assert found.email == "dave@example.com"
        assert found.check_password("davepass") is True
