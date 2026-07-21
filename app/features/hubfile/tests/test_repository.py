"""Repository-level tests for hubfile — hubfile repositories against the DB."""

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet, DSMetaData, PublicationType
from app.features.featuremodel.models import FeatureModel
from app.features.hubfile.models import Hubfile
from app.features.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository,
)

pytestmark = pytest.mark.repository


def _make_hubfile(email="owner@example.com", name="model.uvl", size=1024):
    """Build the User -> DataSet -> FeatureModel -> Hubfile chain the repositories join over."""
    user = User(email=email, password="ownerpass")
    db.session.add(user)
    db.session.flush()

    meta = DSMetaData(
        title="Sample dataset",
        description="A dataset used by the hubfile tests",
        publication_type=PublicationType.OTHER,
    )
    db.session.add(meta)
    db.session.flush()

    dataset = DataSet(user_id=user.id, ds_meta_data_id=meta.id)
    db.session.add(dataset)
    db.session.flush()

    feature_model = FeatureModel(data_set_id=dataset.id)
    db.session.add(feature_model)
    db.session.flush()

    hubfile = Hubfile(name=name, checksum="checksum-1", size=size, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    return user, dataset, hubfile


def test_get_owner_user_by_hubfile_walks_the_join_chain(test_app, clean_database):
    with test_app.app_context():
        user, _, hubfile = _make_hubfile(email="alice@example.com")

        owner = HubfileRepository().get_owner_user_by_hubfile(hubfile)

        assert owner is not None
        assert owner.id == user.id
        assert owner.email == "alice@example.com"


def test_get_dataset_by_hubfile_returns_the_owning_dataset(test_app, clean_database):
    with test_app.app_context():
        _, dataset, hubfile = _make_hubfile(email="bob@example.com")

        found = HubfileRepository().get_dataset_by_hubfile(hubfile)

        assert found is not None
        assert found.id == dataset.id


def test_get_owner_user_picks_the_right_owner_among_several(test_app, clean_database):
    with test_app.app_context():
        _, _, first = _make_hubfile(email="first@example.com", name="first.uvl")
        second_user, _, second = _make_hubfile(email="second@example.com", name="second.uvl")

        owner = HubfileRepository().get_owner_user_by_hubfile(second)

        assert owner.id == second_user.id
        assert owner.id != HubfileRepository().get_owner_user_by_hubfile(first).id


def test_total_hubfile_views_is_zero_on_an_empty_database(test_app, clean_database):
    with test_app.app_context():
        assert HubfileViewRecordRepository().total_hubfile_views() == 0


def test_total_hubfile_views_counts_stored_records(test_app, clean_database):
    with test_app.app_context():
        user, _, hubfile = _make_hubfile()
        repo = HubfileViewRecordRepository()
        for cookie in ("c1", "c2", "c3"):
            repo.create(user_id=user.id, file_id=hubfile.id, view_cookie=cookie)

        assert repo.total_hubfile_views() == 3


def test_view_record_lookup_matches_on_user_file_and_cookie(test_app, clean_database):
    with test_app.app_context():
        user, _, hubfile = _make_hubfile()
        repo = HubfileViewRecordRepository()
        created = repo.create(user_id=user.id, file_id=hubfile.id, view_cookie="cookie-a")

        assert repo.find_by_user_file_cookie(user.id, hubfile.id, "cookie-a").id == created.id
        assert repo.find_by_user_file_cookie(user.id, hubfile.id, "other-cookie") is None
        assert repo.find_by_user_file_cookie(None, hubfile.id, "cookie-a") is None


def test_download_record_lookup_distinguishes_anonymous_records(test_app, clean_database):
    with test_app.app_context():
        user, _, hubfile = _make_hubfile()
        repo = HubfileDownloadRecordRepository()
        repo.create(user_id=user.id, file_id=hubfile.id, download_cookie="shared-cookie")
        anonymous = repo.create(user_id=None, file_id=hubfile.id, download_cookie="shared-cookie")

        found = repo.find_by_user_file_cookie(None, hubfile.id, "shared-cookie")

        assert found is not None
        assert found.id == anonymous.id
        assert found.user_id is None
        assert repo.total_hubfile_downloads() == 2
