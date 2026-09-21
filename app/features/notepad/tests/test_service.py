"""Service-level tests for the notepad feature.

These exercise services and repositories against a real database, without
going through the HTTP layer. Use the ``test_app`` fixture (provides an app
context + reset DB) from splent_framework.
"""

import pytest

pytestmark = pytest.mark.service


def test_notepad_service_placeholder(test_app):
    with test_app.app_context():
        assert True
