"""HTTP integration tests for team via the Flask test client."""

import pytest

pytestmark = pytest.mark.integration


def test_team_page_lists_the_partner_institutions(test_client):
    response = test_client.get("/team")
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    assert "University of Seville, Spain" in html
    assert "University of Malaga, Spain" in html
    assert "University of Ulm, Germany" in html
    assert "www.us.es" in html
    assert "www.uma.es" in html
    assert "www.uni-ulm.de" in html


def test_team_page_is_public_and_get_only(test_client):
    assert test_client.get("/team", follow_redirects=False).status_code == 200
    assert test_client.post("/team").status_code == 405
