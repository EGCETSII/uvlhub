"""Service-level tests for hubfile — services + repositories against a real DB."""

import os

import pytest
from flask_login import AnonymousUserMixin

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet, DSMetaData, PublicationType
from app.features.featuremodel.models import FeatureModel
from app.features.hubfile.models import Hubfile
from app.features.hubfile.services import (
    HubfileDownloadRecordService,
    HubfileService,
    HubfileViewRecordService,
)

pytestmark = pytest.mark.service


def _make_hubfile(email="owner@example.com", name="model.uvl", size=2048):
    """Build the User -> DataSet -> FeatureModel -> Hubfile chain the services resolve paths from."""
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


def _write_upload(root, user_id, dataset_id, name, content):
    directory = os.path.join(str(root), "uploads", f"user_{user_id}", f"dataset_{dataset_id}")
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name)
    with open(path, "w") as f:
        f.write(content)
    return path


def test_get_path_by_hubfile_uses_working_dir_user_and_dataset(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_app.app_context():
        user, dataset, hubfile = _make_hubfile(name="model.uvl")

        path = HubfileService().get_path_by_hubfile(hubfile)

        assert path == os.path.join(str(tmp_path), "uploads", f"user_{user.id}", f"dataset_{dataset.id}", "model.uvl")


def test_directory_for_strips_the_filename(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_app.app_context():
        user, dataset, hubfile = _make_hubfile(name="model.uvl")

        directory = HubfileService().directory_for(hubfile)

        assert directory == os.path.join(str(tmp_path), "uploads", f"user_{user.id}", f"dataset_{dataset.id}")
        assert not directory.endswith("model.uvl")


def test_read_text_returns_none_when_the_file_is_absent(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_app.app_context():
        _, _, hubfile = _make_hubfile(name="missing.uvl")

        assert HubfileService().read_text(hubfile) is None


def test_read_text_returns_the_file_contents(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_app.app_context():
        user, dataset, hubfile = _make_hubfile(name="model.uvl")
        _write_upload(tmp_path, user.id, dataset.id, "model.uvl", "features\n    Root\n")

        assert HubfileService().read_text(hubfile) == "features\n    Root\n"


def test_owner_and_dataset_lookups_are_exposed_on_the_model(test_app, clean_database):
    with test_app.app_context():
        user, dataset, hubfile = _make_hubfile(email="carol@example.com")

        assert hubfile.get_owner_user().id == user.id
        assert hubfile.get_dataset().id == dataset.id


def test_record_download_is_idempotent_per_cookie(test_app, clean_database):
    with test_app.app_context():
        user, _, hubfile = _make_hubfile()
        service = HubfileDownloadRecordService()

        service.record_download(user, hubfile.id, "cookie-a")
        service.record_download(user, hubfile.id, "cookie-a")
        assert service.count() == 1

        service.record_download(user, hubfile.id, "cookie-b")
        assert service.count() == 2


def test_record_download_stores_anonymous_users_without_an_id(test_app, clean_database):
    with test_app.app_context():
        _, _, hubfile = _make_hubfile()
        service = HubfileDownloadRecordService()

        service.record_download(AnonymousUserMixin(), hubfile.id, "anon-cookie")
        service.record_download(AnonymousUserMixin(), hubfile.id, "anon-cookie")

        record = service.repository.find_by_user_file_cookie(None, hubfile.id, "anon-cookie")
        assert record is not None
        assert record.user_id is None
        assert record.download_date is not None
        assert service.count() == 1


def test_record_view_is_idempotent_per_cookie_and_separate_per_user(test_app, clean_database):
    with test_app.app_context():
        user, _, hubfile = _make_hubfile(email="dave@example.com")
        service = HubfileViewRecordService()

        service.record_view(user, hubfile.id, "cookie-a")
        service.record_view(user, hubfile.id, "cookie-a")
        assert service.count() == 1

        service.record_view(AnonymousUserMixin(), hubfile.id, "cookie-a")
        assert service.count() == 2


def test_totals_reflect_recorded_views_and_downloads(test_app, clean_database):
    with test_app.app_context():
        user, _, hubfile = _make_hubfile()
        hubfile_service = HubfileService()
        assert hubfile_service.total_hubfile_views() == 0
        assert hubfile_service.total_hubfile_downloads() == 0

        HubfileViewRecordService().record_view(user, hubfile.id, "view-1")
        HubfileViewRecordService().record_view(user, hubfile.id, "view-2")
        HubfileDownloadRecordService().record_download(user, hubfile.id, "dl-1")

        assert hubfile_service.total_hubfile_views() == 2
        assert hubfile_service.total_hubfile_downloads() == 1
