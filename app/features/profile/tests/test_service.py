"""Service-level tests for profile — UserProfileService with a real DB."""

from datetime import datetime, timedelta

import pytest

from app import db
from app.features.auth.repositories import UserRepository
from app.features.dataset.models import DataSet, DSMetaData, PublicationType
from app.features.profile.forms import UserProfileForm
from app.features.profile.repositories import UserProfileRepository
from app.features.profile.services import UserProfileService

pytestmark = pytest.mark.service

BASE_TIME = datetime(2024, 1, 1, 12, 0, 0)


def make_user(email):
    return UserRepository().create(email=email, password="secret")


def make_dataset(user_id, title, created_at):
    meta = DSMetaData(
        title=title,
        description=f"Description for {title}",
        publication_type=PublicationType.NONE,
    )
    db.session.add(meta)
    db.session.flush()
    dataset = DataSet(user_id=user_id, ds_meta_data_id=meta.id, created_at=created_at)
    db.session.add(dataset)
    db.session.commit()
    return dataset


def test_summary_for_user_is_empty_without_datasets(test_app, test_client):
    with test_app.app_context():
        user = make_user("svc-empty@example.com")

        summary = UserProfileService().summary_for_user(user.id, page=1)

        assert summary["datasets"] == []
        assert summary["total_datasets"] == 0
        assert summary["pagination"].pages == 0


def test_summary_for_user_paginates_newest_first(test_app, test_client):
    with test_app.app_context():
        user = make_user("svc-paginate@example.com")
        for index in range(7):
            make_dataset(user.id, f"ds-{index}", BASE_TIME + timedelta(minutes=index))
        service = UserProfileService()

        first = service.summary_for_user(user.id, page=1)
        second = service.summary_for_user(user.id, page=2)

        assert first["total_datasets"] == 7
        assert first["pagination"].pages == 2
        # Newest first: ds-6 down to ds-2 on page one, the two oldest on page two.
        assert [d.ds_meta_data.title for d in first["datasets"]] == [
            "ds-6",
            "ds-5",
            "ds-4",
            "ds-3",
            "ds-2",
        ]
        assert [d.ds_meta_data.title for d in second["datasets"]] == ["ds-1", "ds-0"]
        assert second["pagination"].has_next is False


def test_summary_for_user_honours_custom_per_page(test_app, test_client):
    with test_app.app_context():
        user = make_user("svc-perpage@example.com")
        for index in range(5):
            make_dataset(user.id, f"ds-{index}", BASE_TIME + timedelta(minutes=index))

        summary = UserProfileService().summary_for_user(user.id, page=1, per_page=2)

        assert len(summary["datasets"]) == 2
        assert summary["pagination"].pages == 3
        assert summary["total_datasets"] == 5


def test_summary_for_user_excludes_other_users_datasets(test_app, test_client):
    with test_app.app_context():
        owner = make_user("svc-owner@example.com")
        stranger = make_user("svc-stranger@example.com")
        make_dataset(owner.id, "mine", BASE_TIME)
        make_dataset(stranger.id, "theirs", BASE_TIME)

        summary = UserProfileService().summary_for_user(owner.id, page=1)

        assert summary["total_datasets"] == 1
        assert [d.ds_meta_data.title for d in summary["datasets"]] == ["mine"]


def test_summary_for_user_past_last_page_returns_no_items(test_app, test_client):
    with test_app.app_context():
        user = make_user("svc-overflow@example.com")
        make_dataset(user.id, "only", BASE_TIME)

        summary = UserProfileService().summary_for_user(user.id, page=99)

        assert summary["datasets"] == []
        assert summary["total_datasets"] == 1


def test_update_profile_persists_valid_form(test_app, test_client):
    with test_app.app_context():
        user = make_user("svc-valid@example.com")
        profile = UserProfileRepository().create(user_id=user.id, name="Ada", surname="Lovelace")

        form_data = {
            "name": "Augusta",
            "surname": "King",
            "orcid": "0000-0001-2345-6789",
            "affiliation": "Analytical Engine Lab",
        }
        with test_app.test_request_context("/profile/edit", method="POST", data=form_data):
            updated, errors = UserProfileService().update_profile(profile.id, UserProfileForm())

        assert errors is None
        assert updated.name == "Augusta"
        # Form-only fields must not leak into the model instance via setattr.
        assert not hasattr(updated, "submit")
        assert not hasattr(updated, "csrf_token")

        reloaded = UserProfileRepository().get_by_id(profile.id)
        assert reloaded.surname == "King"
        assert reloaded.orcid == "0000-0001-2345-6789"
        assert reloaded.affiliation == "Analytical Engine Lab"


def test_update_profile_rejects_malformed_orcid(test_app, test_client):
    with test_app.app_context():
        user = make_user("svc-badorcid@example.com")
        profile = UserProfileRepository().create(user_id=user.id, name="Ada", surname="Lovelace")

        form_data = {"name": "Augusta", "surname": "King", "orcid": "not-an-orcid"}
        with test_app.test_request_context("/profile/edit", method="POST", data=form_data):
            updated, errors = UserProfileService().update_profile(profile.id, UserProfileForm())

        assert updated is None
        assert "orcid" in errors

        reloaded = UserProfileRepository().get_by_id(profile.id)
        assert reloaded.name == "Ada"
        assert reloaded.orcid is None


def test_update_profile_requires_name_and_surname(test_app, test_client):
    with test_app.app_context():
        user = make_user("svc-required@example.com")
        profile = UserProfileRepository().create(user_id=user.id, name="Ada", surname="Lovelace")

        with test_app.test_request_context("/profile/edit", method="POST", data={"name": "", "surname": ""}):
            updated, errors = UserProfileService().update_profile(profile.id, UserProfileForm())

        assert updated is None
        assert set(errors) == {"name", "surname"}
