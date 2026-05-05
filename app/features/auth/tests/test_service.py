"""Service-level tests for auth — exercise services + repos with a real DB."""
import pytest

from app.features.auth.services import AuthenticationService

pytestmark = pytest.mark.service


def test_email_available_for_unused_address(test_app):
    with test_app.app_context():
        service = AuthenticationService()
        assert service.is_email_available("ghost@example.com") is True


def test_create_with_profile_persists_user(test_app):
    with test_app.app_context():
        service = AuthenticationService()
        user = service.create_with_profile(
            email="bob@example.com",
            password="bobpass",
            name="Bob",
            surname="Smith",
        )
        assert user.id is not None
        assert service.is_email_available("bob@example.com") is False
