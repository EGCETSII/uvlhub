"""Repository-level tests for webhook — WebhookRepository against the DB."""

import pytest

from app.features.webhook.repositories import WebhookRepository

pytestmark = pytest.mark.repository


def test_count_is_zero_on_empty_database(test_app, test_client):
    with test_app.app_context():
        assert WebhookRepository().count() == 0


def test_create_persists_row_with_generated_id(test_app, test_client):
    with test_app.app_context():
        repo = WebhookRepository()

        created = repo.create()

        assert created.id is not None
        assert repo.get_by_id(created.id) is not None
        assert repo.count() == 1


def test_delete_removes_row(test_app, test_client):
    with test_app.app_context():
        repo = WebhookRepository()
        created = repo.create()

        assert repo.delete(created.id) is True

        assert repo.get_by_id(created.id) is None
        assert repo.count() == 0


def test_delete_returns_false_for_unknown_id(test_app, test_client):
    with test_app.app_context():
        assert WebhookRepository().delete(999) is False
