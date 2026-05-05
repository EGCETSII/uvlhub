"""Unit tests for the auth feature — pure logic, no Flask app, no DB."""
import pytest

from app.features.auth.models import User

pytestmark = pytest.mark.unit


def test_set_password_hashes_value():
    user = User(email="alice@example.com")
    user.set_password("secret")
    assert user.password != "secret"
    assert user.check_password("secret") is True


def test_check_password_rejects_wrong_value():
    user = User(email="alice@example.com")
    user.set_password("secret")
    assert user.check_password("nope") is False
