"""HTTP integration tests for the notepad feature.

Drive the application through the Flask test client. The ``test_client``
fixture from splent_framework rebuilds a clean DB per test for full isolation.
"""

import pytest

pytestmark = pytest.mark.integration


def test_notepad_index_responds(test_client):
    response = test_client.get("/notepad")
    assert response.status_code == 200, "/notepad did not return 200"
