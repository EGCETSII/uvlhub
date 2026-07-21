"""Repository-level tests for profile — UserProfileRepository against the DB."""

import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.features.auth.repositories import UserRepository
from app.features.profile.repositories import UserProfileRepository

pytestmark = pytest.mark.repository


def make_user(email):
    return UserRepository().create(email=email, password="secret")


def test_get_by_id_returns_none_when_absent(test_app, test_client):
    with test_app.app_context():
        assert UserProfileRepository().get_by_id(12345) is None


def test_create_then_read_back_profile(test_app, test_client):
    with test_app.app_context():
        user = make_user("repo-create@example.com")
        repo = UserProfileRepository()

        created = repo.create(
            user_id=user.id,
            name="Ada",
            surname="Lovelace",
            orcid="0000-0001-2345-6789",
            affiliation="Analytical Engine Lab",
        )

        found = repo.get_by_id(created.id)
        assert found is not None
        assert found.user_id == user.id
        assert found.name == "Ada"
        assert found.orcid == "0000-0001-2345-6789"
        assert found.affiliation == "Analytical Engine Lab"


def test_get_by_column_filters_on_user_id(test_app, test_client):
    with test_app.app_context():
        owner = make_user("repo-owner@example.com")
        other = make_user("repo-other@example.com")
        repo = UserProfileRepository()
        repo.create(user_id=owner.id, name="Ada", surname="Lovelace")
        repo.create(user_id=other.id, name="Grace", surname="Hopper")

        matches = repo.get_by_column("user_id", owner.id)

        assert len(matches) == 1
        assert matches[0].name == "Ada"


def test_update_persists_changed_fields(test_app, test_client):
    with test_app.app_context():
        user = make_user("repo-update@example.com")
        repo = UserProfileRepository()
        profile = repo.create(user_id=user.id, name="Ada", surname="Lovelace")

        repo.update(profile.id, affiliation="Cambridge", orcid="1111-2222-3333-4444")

        reloaded = repo.get_by_id(profile.id)
        assert reloaded.affiliation == "Cambridge"
        assert reloaded.orcid == "1111-2222-3333-4444"
        assert reloaded.name == "Ada"


def test_delete_removes_profile_and_updates_count(test_app, test_client):
    with test_app.app_context():
        user = make_user("repo-delete@example.com")
        repo = UserProfileRepository()
        profile = repo.create(user_id=user.id, name="Ada", surname="Lovelace")
        assert repo.count() == 1

        assert repo.delete(profile.id) is True

        assert repo.count() == 0
        assert repo.get_by_id(profile.id) is None


def test_delete_returns_false_for_unknown_id(test_app, test_client):
    with test_app.app_context():
        assert UserProfileRepository().delete(4242) is False


def test_user_id_is_unique_across_profiles(test_app, test_client):
    with test_app.app_context():
        user = make_user("repo-unique@example.com")
        repo = UserProfileRepository()
        repo.create(user_id=user.id, name="Ada", surname="Lovelace")

        with pytest.raises(IntegrityError):
            repo.create(user_id=user.id, name="Duplicate", surname="Profile")

        db.session.rollback()
