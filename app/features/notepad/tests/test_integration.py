import pytest

pytestmark = pytest.mark.integration


def test_notepad_index_requires_login(test_client):
    response = test_client.get("/notepad", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/login" in response.headers["Location"]
