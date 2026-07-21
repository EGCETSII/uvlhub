"""HTTP integration tests for webhook via the Flask test client.

``WebhookService.deploy`` is always replaced by a recorder — the endpoint is
exercised for its authorization logic only, never for a real deployment.
"""

import pytest

from app.features.webhook import routes as webhook_routes

pytestmark = pytest.mark.integration

TOKEN = "test-webhook-token"


@pytest.fixture
def deploy_calls(monkeypatch):
    """Neutralise the deploy side effect and record how often it is invoked."""
    calls = []
    monkeypatch.setattr(webhook_routes, "WEBHOOK_TOKEN", TOKEN)
    monkeypatch.setattr(webhook_routes.webhook_service, "deploy", lambda: calls.append(True))
    return calls


def test_deploy_without_authorization_header_is_forbidden(test_client, deploy_calls):
    response = test_client.post("/webhook/deploy")

    assert response.status_code == 403
    assert deploy_calls == []


def test_deploy_with_wrong_token_is_forbidden(test_client, deploy_calls):
    response = test_client.post("/webhook/deploy", headers={"Authorization": "Bearer wrong-token"})

    assert response.status_code == 403
    assert deploy_calls == []


def test_deploy_with_raw_token_and_no_bearer_prefix_is_forbidden(test_client, deploy_calls):
    response = test_client.post("/webhook/deploy", headers={"Authorization": TOKEN})

    assert response.status_code == 403
    assert deploy_calls == []


def test_deploy_with_valid_token_runs_deployment(test_client, deploy_calls):
    response = test_client.post("/webhook/deploy", headers={"Authorization": f"Bearer {TOKEN}"})

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Deployment successful"
    assert deploy_calls == [True]


def test_deploy_rejects_get_requests(test_client, deploy_calls):
    response = test_client.get("/webhook/deploy", headers={"Authorization": f"Bearer {TOKEN}"})

    assert response.status_code == 405
    assert deploy_calls == []


def test_deploy_failure_surfaces_as_error_response(test_client, monkeypatch):
    def boom():
        from flask import abort

        abort(500, description="Container command failed")

    monkeypatch.setattr(webhook_routes, "WEBHOOK_TOKEN", TOKEN)
    monkeypatch.setattr(webhook_routes.webhook_service, "deploy", boom)

    response = test_client.post("/webhook/deploy", headers={"Authorization": f"Bearer {TOKEN}"})

    assert response.status_code == 500
