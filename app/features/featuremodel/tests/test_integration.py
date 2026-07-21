"""HTTP integration tests for featuremodel via the Flask test client."""

import pytest

pytestmark = pytest.mark.integration


def test_featuremodel_page_renders_its_own_template(test_client):
    response = test_client.get("/featuremodel")
    assert response.status_code == 200
    # The feature's own script tag is the only markup the template contributes.
    assert b'<script src="/featuremodel/scripts/scripts.js"></script>' in response.data


def test_featuremodel_page_is_public(test_client):
    response = test_client.get("/featuremodel", follow_redirects=False)
    assert response.status_code == 200


def test_featuremodel_route_rejects_post(test_client):
    response = test_client.post("/featuremodel")
    assert response.status_code == 405
