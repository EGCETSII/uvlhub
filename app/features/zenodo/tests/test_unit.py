"""Unit tests for the zenodo feature — pure logic, no Flask app, no DB.

Covers how ``ZenodoService`` resolves its API URL from the environment and how
it wires the access token into the request parameters. No HTTP is performed:
these tests only exercise configuration logic.
"""

import pytest

from app.features.zenodo.services import ZenodoService

pytestmark = pytest.mark.unit

SANDBOX_URL = "https://sandbox.zenodo.org/api/deposit/depositions"
PRODUCTION_URL = "https://zenodo.org/api/deposit/depositions"


def _service(monkeypatch, **env):
    """Build a ZenodoService with a controlled environment."""
    for key in ("FLASK_ENV", "ZENODO_API_URL", "ZENODO_ACCESS_TOKEN"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return ZenodoService()


def test_development_environment_uses_sandbox_url(monkeypatch):
    service = _service(monkeypatch, FLASK_ENV="development")
    assert service.ZENODO_API_URL == SANDBOX_URL


def test_production_environment_uses_live_url(monkeypatch):
    service = _service(monkeypatch, FLASK_ENV="production")
    assert service.ZENODO_API_URL == PRODUCTION_URL


def test_unknown_environment_falls_back_to_sandbox_url(monkeypatch):
    service = _service(monkeypatch, FLASK_ENV="staging")
    assert service.ZENODO_API_URL == SANDBOX_URL


def test_missing_flask_env_defaults_to_sandbox_url(monkeypatch):
    service = _service(monkeypatch)
    assert service.ZENODO_API_URL == SANDBOX_URL


def test_explicit_api_url_overrides_the_environment_default(monkeypatch):
    service = _service(
        monkeypatch,
        FLASK_ENV="production",
        ZENODO_API_URL="https://example.test/api/deposit/depositions",
    )
    assert service.ZENODO_API_URL == "https://example.test/api/deposit/depositions"


def test_access_token_is_read_from_the_environment(monkeypatch):
    service = _service(monkeypatch, FLASK_ENV="development", ZENODO_ACCESS_TOKEN="s3cr3t")
    assert service.ZENODO_ACCESS_TOKEN == "s3cr3t"
    assert service.params == {"access_token": "s3cr3t"}
    assert service.headers == {"Content-Type": "application/json"}


def test_missing_access_token_leaves_the_param_empty(monkeypatch):
    service = _service(monkeypatch, FLASK_ENV="development")
    assert service.ZENODO_ACCESS_TOKEN is None
    assert service.params == {"access_token": None}
