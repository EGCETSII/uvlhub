"""HTTP integration tests for hubfile via the Flask test client."""

import os

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet, DSMetaData, PublicationType
from app.features.featuremodel.models import FeatureModel
from app.features.hubfile.models import Hubfile
from app.features.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileViewRecordRepository,
)

pytestmark = pytest.mark.integration

UVL_CONTENT = "features\n    Root\n        mandatory\n            Wheels\n"


def _make_hubfile(email="owner@example.com", name="model.uvl", size=2048):
    """Build the User -> DataSet -> FeatureModel -> Hubfile chain the routes resolve paths from."""
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

    return user.id, dataset.id, hubfile.id


def _write_upload(root, user_id, dataset_id, name, content):
    directory = os.path.join(str(root), "uploads", f"user_{user_id}", f"dataset_{dataset_id}")
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, name), "w") as f:
        f.write(content)


def test_view_file_returns_the_uvl_content_as_json(test_client, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_client.application.app_context():
        user_id, dataset_id, file_id = _make_hubfile()
        _write_upload(tmp_path, user_id, dataset_id, "model.uvl", UVL_CONTENT)

    response = test_client.get(f"/file/view/{file_id}")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["content"] == UVL_CONTENT


def test_view_file_sets_a_view_cookie_and_records_the_view(test_client, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_client.application.app_context():
        user_id, dataset_id, file_id = _make_hubfile()
        _write_upload(tmp_path, user_id, dataset_id, "model.uvl", UVL_CONTENT)

    response = test_client.get(f"/file/view/{file_id}")

    assert "view_cookie" in response.headers.get("Set-Cookie", "")
    with test_client.application.app_context():
        records = HubfileViewRecordRepository().get_by_column("file_id", file_id)
        assert len(records) == 1
        # Nobody is logged in, so the view is attributed to an anonymous visitor.
        assert records[0].user_id is None
        assert records[0].view_cookie


def test_repeated_views_with_the_same_cookie_record_only_once(test_client, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_client.application.app_context():
        user_id, dataset_id, file_id = _make_hubfile()
        _write_upload(tmp_path, user_id, dataset_id, "model.uvl", UVL_CONTENT)

    # The test client keeps the cookie jar between requests, so the second call reuses view_cookie.
    test_client.get(f"/file/view/{file_id}")
    second = test_client.get(f"/file/view/{file_id}")

    assert second.status_code == 200
    with test_client.application.app_context():
        assert len(HubfileViewRecordRepository().get_by_column("file_id", file_id)) == 1


def test_view_file_reports_404_when_the_file_is_not_on_disk(test_client, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_client.application.app_context():
        _, _, file_id = _make_hubfile(name="never_written.uvl")

    response = test_client.get(f"/file/view/{file_id}")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["error"] == "File not found"
    with test_client.application.app_context():
        assert HubfileViewRecordRepository().get_by_column("file_id", file_id) == []


def test_view_file_returns_404_for_an_unknown_id(test_client, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    response = test_client.get("/file/view/999999")
    assert response.status_code == 404


def test_download_file_serves_the_file_as_an_attachment(test_client, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_client.application.app_context():
        user_id, dataset_id, file_id = _make_hubfile()
        _write_upload(tmp_path, user_id, dataset_id, "model.uvl", UVL_CONTENT)

    response = test_client.get(f"/file/download/{file_id}")

    assert response.status_code == 200
    assert response.data.decode() == UVL_CONTENT
    assert "attachment" in response.headers["Content-Disposition"]
    assert "model.uvl" in response.headers["Content-Disposition"]
    set_cookie = response.headers.get("Set-Cookie", "")
    assert "file_download_cookie" in set_cookie
    # The download cookie persists for two years, matching the view cookie's lifetime.
    assert "Max-Age=63072000" in set_cookie


def test_download_file_records_the_download_once_per_cookie(test_client, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_client.application.app_context():
        user_id, dataset_id, file_id = _make_hubfile()
        _write_upload(tmp_path, user_id, dataset_id, "model.uvl", UVL_CONTENT)

    test_client.get(f"/file/download/{file_id}")
    test_client.get(f"/file/download/{file_id}")

    with test_client.application.app_context():
        records = HubfileDownloadRecordRepository().get_by_column("file_id", file_id)
        assert len(records) == 1
        assert records[0].user_id is None


def test_download_file_returns_404_for_an_unknown_id(test_client, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    response = test_client.get("/file/download/999999")
    assert response.status_code == 404


def test_download_missing_from_disk_is_404_and_records_nothing(test_client, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_client.application.app_context():
        _, _, file_id = _make_hubfile(name="never_written.uvl")

    response = test_client.get(f"/file/download/{file_id}")

    assert response.status_code == 404
    with test_client.application.app_context():
        assert HubfileDownloadRecordRepository().get_by_column("file_id", file_id) == []


def test_download_attributes_the_record_to_the_logged_in_user(test_client, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_client.application.app_context():
        user_id, dataset_id, file_id = _make_hubfile(email="reader@example.com")
        _write_upload(tmp_path, user_id, dataset_id, "model.uvl", UVL_CONTENT)

    login = test_client.post(
        "/login",
        data={"email": "reader@example.com", "password": "ownerpass"},
        follow_redirects=False,
    )
    assert login.status_code in (302, 303)

    response = test_client.get(f"/file/download/{file_id}")

    assert response.status_code == 200
    with test_client.application.app_context():
        records = HubfileDownloadRecordRepository().get_by_column("file_id", file_id)
        assert len(records) == 1
        assert records[0].user_id == user_id
