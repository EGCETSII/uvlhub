"""HTTP integration tests for dataset via the Flask test client.

Covers the HTML routes (list / DOI landing page / unsynchronized view / temp
file endpoints) as well as the ``/api/v1/datasets`` REST resource.
"""

import io
from datetime import datetime, timezone

import pytest

from app.features.auth.repositories import UserRepository
from app.features.dataset.models import PublicationType
from app.features.dataset.repositories import DataSetRepository, DOIMappingRepository, DSMetaDataRepository
from app.features.featuremodel.repositories import FeatureModelRepository, FMMetaDataRepository
from app.features.hubfile.repositories import HubfileRepository

pytestmark = pytest.mark.integration


def _signup(test_client, email="owner@example.com", password="ownerpass"):
    """Register a user through the auth blueprint; the response leaves them logged in."""
    response = test_client.post(
        "/signup/",
        data={"email": email, "password": password, "name": "Olivia", "surname": "Owner"},
        follow_redirects=False,
    )
    assert response.status_code in (302, 303)
    with test_client.application.app_context():
        return UserRepository().get_by_email(email).id


def _make_dataset(user_id, title="Sample dataset", doi=None):
    meta = DSMetaDataRepository().create(
        title=title,
        description=f"Description for {title}",
        publication_type=PublicationType.DATA_MANAGEMENT_PLAN,
        dataset_doi=doi,
        deposition_id=7,
        tags="tag1,tag2",
    )
    return DataSetRepository().create(
        user_id=user_id,
        ds_meta_data_id=meta.id,
        created_at=datetime.now(timezone.utc),
    )


def _attach_file(dataset, name="file1.uvl", size=2048):
    fm_meta = FMMetaDataRepository().create(
        uvl_filename=name,
        title="Feature model",
        description="A feature model",
        publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
    )
    feature_model = FeatureModelRepository().create(data_set_id=dataset.id, fm_meta_data_id=fm_meta.id)
    return HubfileRepository().create(name=name, checksum="deadbeef", size=size, feature_model_id=feature_model.id)


def test_upload_page_redirects_anonymous_visitors_to_login(test_client):
    response = test_client.get("/dataset/upload", follow_redirects=False)

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_list_dataset_shows_only_the_logged_in_users_datasets(test_client):
    user_id = _signup(test_client)
    with test_client.application.app_context():
        stranger = UserRepository().create(email="stranger@example.com", password="pass")
        _make_dataset(user_id, title="My published dataset", doi="10.1234/mine")
        _make_dataset(user_id, title="My local dataset")
        _make_dataset(stranger.id, title="Somebody elses dataset", doi="10.1234/theirs")

    response = test_client.get("/dataset/list")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "My published dataset" in body
    assert "My local dataset" in body
    assert "Somebody elses dataset" not in body


def test_unsynchronized_dataset_page_renders_for_its_owner(test_client):
    user_id = _signup(test_client)
    with test_client.application.app_context():
        dataset_id = _make_dataset(user_id, title="Work in progress").id

    response = test_client.get(f"/dataset/unsynchronized/{dataset_id}/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Work in progress" in body
    assert "Data Management Plan" in body


def test_unsynchronized_dataset_page_404s_once_the_dataset_has_a_doi(test_client):
    user_id = _signup(test_client)
    with test_client.application.app_context():
        dataset_id = _make_dataset(user_id, title="Published", doi="10.1234/published").id

    assert test_client.get(f"/dataset/unsynchronized/{dataset_id}/").status_code == 404


def test_doi_landing_page_renders_the_dataset_and_sets_a_view_cookie(test_client):
    user_id = _signup(test_client)
    with test_client.application.app_context():
        _make_dataset(user_id, title="Findable dataset", doi="10.1234/findable")

    response = test_client.get("/doi/10.1234/findable/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Findable dataset" in body
    assert "view_cookie" in response.headers.get("Set-Cookie", "")


def test_doi_landing_page_redirects_a_superseded_doi(test_client):
    user_id = _signup(test_client)
    with test_client.application.app_context():
        _make_dataset(user_id, title="Findable dataset", doi="10.5678/new")
        DOIMappingRepository().create(dataset_doi_old="10.1234/old", dataset_doi_new="10.5678/new")

    response = test_client.get("/doi/10.1234/old/", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/doi/10.5678/new/")


def test_doi_landing_page_404s_for_an_unknown_doi(test_client):
    assert test_client.get("/doi/10.1234/does-not-exist/").status_code == 404


def test_upload_dataset_rejects_a_form_that_fails_validation(test_client):
    _signup(test_client)

    response = test_client.post("/dataset/upload", data={"title": "", "desc": ""})

    assert response.status_code == 400
    errors = response.get_json()["message"]
    assert "title" in errors
    assert "desc" in errors


def test_temp_file_upload_rejects_anything_that_is_not_uvl(test_client, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    _signup(test_client)

    response = test_client.post(
        "/dataset/file/upload",
        data={"file": (io.BytesIO(b"not a model"), "notes.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "No valid file"


def test_temp_uvl_file_can_be_uploaded_and_then_deleted(test_client, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    _signup(test_client)

    upload = test_client.post(
        "/dataset/file/upload",
        data={"file": (io.BytesIO(b"features\n\tRoot\n"), "model.uvl")},
        content_type="multipart/form-data",
    )
    assert upload.status_code == 200
    filename = upload.get_json()["filename"]
    assert filename == "model.uvl"

    deleted = test_client.post("/dataset/file/delete", json={"file": filename})
    assert deleted.status_code == 200
    assert deleted.get_json()["message"] == "File deleted successfully"

    # The file is gone, so a second delete reports it as missing.
    missing = test_client.post("/dataset/file/delete", json={"file": filename})
    assert missing.status_code == 404
    assert missing.get_json()["error"] == "Error: File not found"


def test_api_lists_every_dataset_with_its_files(test_client):
    user_id = _signup(test_client)
    with test_client.application.app_context():
        first = _make_dataset(user_id, title="First dataset", doi="10.1234/first")
        file_id = _attach_file(first, name="file1.uvl", size=2048).id
        _make_dataset(user_id, title="Second dataset")

    response = test_client.get("/api/v1/datasets/")
    payload = response.get_json()

    assert response.status_code == 200
    assert {item["name"] for item in payload["items"]} == {"First dataset", "Second dataset"}

    published = next(item for item in payload["items"] if item["name"] == "First dataset")
    assert published["doi"].endswith("/doi/10.1234/first")
    assert published["files"] == [{"file_id": file_id, "file_name": "file1.uvl", "size": "2.0 KB"}]
    assert "created" in published


def test_api_returns_a_single_dataset_or_404(test_client):
    user_id = _signup(test_client)
    with test_client.application.app_context():
        dataset_id = _make_dataset(user_id, title="Only dataset", doi="10.1234/only").id

    found = test_client.get(f"/api/v1/datasets/{dataset_id}")
    assert found.status_code == 200
    assert found.get_json()["dataset_id"] == dataset_id
    assert found.get_json()["name"] == "Only dataset"
    assert found.get_json()["files"] == []

    missing = test_client.get(f"/api/v1/datasets/{dataset_id + 999}")
    assert missing.status_code == 404
    assert missing.get_json()["message"] == "DataSet not found"
