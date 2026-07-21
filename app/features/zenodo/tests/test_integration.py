"""HTTP integration tests for zenodo via the Flask test client.

``/zenodo/test`` drives the real Zenodo REST API, so the ``requests`` module used
by the service is patched in every test — no network call is ever made.
"""

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.integration


def _response(status_code, payload=None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = {} if payload is None else payload
    response.content = b""
    return response


def test_index_page_renders(test_client):
    response = test_client.get("/zenodo")
    assert response.status_code == 200
    # The feature template is what rendered, not just some base page: it pulls
    # in the zenodo asset bundle served by the blueprint's assets route.
    assert b"/zenodo/js/scripts.js" in response.data


def test_test_endpoint_reports_success_when_the_full_round_trip_works(test_client, tmp_path, monkeypatch):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with patch("app.features.zenodo.services.requests") as requests_mock:
        requests_mock.post.side_effect = [_response(201, {"id": 123}), _response(201, {"id": 1})]
        requests_mock.delete.return_value = _response(204)
        response = test_client.get("/zenodo/test")

    assert response.status_code == 200
    assert response.get_json() == {"success": True, "messages": []}
    # The deposition created for the probe is removed again.
    assert requests_mock.delete.call_args[0][0].endswith("/123")


def test_test_endpoint_reports_failure_when_the_deposition_cannot_be_created(test_client, tmp_path, monkeypatch):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with patch("app.features.zenodo.services.requests") as requests_mock:
        requests_mock.post.return_value = _response(401)
        response = test_client.get("/zenodo/test")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is False
    assert "401" in body["messages"]
    requests_mock.delete.assert_not_called()


def test_test_endpoint_reports_failure_when_the_upload_is_rejected(test_client, tmp_path, monkeypatch):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with patch("app.features.zenodo.services.requests") as requests_mock:
        requests_mock.post.side_effect = [_response(201, {"id": 321}), _response(500)]
        requests_mock.delete.return_value = _response(204)
        response = test_client.get("/zenodo/test")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is False
    assert any("500" in message for message in body["messages"])
    assert requests_mock.delete.call_args[0][0].endswith("/321")
