"""Repository-level tests for zenodo — ZenodoRepository against the DB."""

import pytest

from app.features.zenodo.models import Zenodo
from app.features.zenodo.repositories import ZenodoRepository

pytestmark = pytest.mark.repository


def test_repository_is_bound_to_the_zenodo_model(test_app):
    with test_app.app_context():
        assert ZenodoRepository().model is Zenodo


def test_create_persists_a_row_with_an_id(test_app):
    with test_app.app_context():
        repo = ZenodoRepository()
        instance = repo.create()
        assert instance.id is not None
        assert repo.get_by_id(instance.id) is instance


def test_get_by_id_returns_none_when_absent(test_app):
    with test_app.app_context():
        assert ZenodoRepository().get_by_id(999999) is None


def test_count_reflects_created_rows(test_app, clean_database):
    with test_app.app_context():
        repo = ZenodoRepository()
        assert repo.count() == 0
        repo.create()
        repo.create()
        assert repo.count() == 2


def test_delete_removes_the_row(test_app, clean_database):
    with test_app.app_context():
        repo = ZenodoRepository()
        instance = repo.create()
        assert repo.delete(instance.id) is True
        assert repo.get_by_id(instance.id) is None
        assert repo.count() == 0


def test_delete_returns_false_for_unknown_id(test_app):
    with test_app.app_context():
        assert ZenodoRepository().delete(999999) is False
