"""Service-level tests for zenodo — orchestration with the HTTP layer mocked.

``ZenodoService`` is a client for the Zenodo REST API. Every test here patches
``app.features.zenodo.services.requests`` so no network call is ever made; the
assertions target the service's own logic: the payloads and URLs it builds, how
it discriminates success from failure status codes, and how it parses responses.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import Author, DataSet, DSMetaData, PublicationType
from app.features.featuremodel.models import FeatureModel, FMMetaData
from app.features.zenodo.services import ZenodoService

pytestmark = pytest.mark.service


def _response(status_code, payload=None):
    """A stand-in for a ``requests.Response``."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = {} if payload is None else payload
    response.content = b""
    return response


def _create_dataset(email, publication_type=PublicationType.NONE, tags=None, authors=None):
    """Persist a minimal DataSet graph the service can read metadata from."""
    user = User(email=email, password="ownerpass")
    db.session.add(user)
    db.session.commit()

    meta_data = DSMetaData(
        title="Sample dataset",
        description="A sample dataset description",
        publication_type=publication_type,
        tags=tags,
    )
    db.session.add(meta_data)
    db.session.commit()

    for author in authors or [Author(name="Jane Doe")]:
        author.ds_meta_data_id = meta_data.id
        db.session.add(author)
    db.session.commit()

    dataset = DataSet(user_id=user.id, ds_meta_data_id=meta_data.id)
    db.session.add(dataset)
    db.session.commit()
    return dataset


def _create_feature_model(dataset, uvl_filename):
    fm_meta_data = FMMetaData(
        uvl_filename=uvl_filename,
        title="Sample model",
        description="A sample feature model",
        publication_type=PublicationType.NONE,
    )
    db.session.add(fm_meta_data)
    db.session.commit()

    feature_model = FeatureModel(data_set_id=dataset.id, fm_meta_data_id=fm_meta_data.id)
    db.session.add(feature_model)
    db.session.commit()
    return feature_model


# --------------------------------------------------------------------------
# test_connection / get_all_depositions
# --------------------------------------------------------------------------


def test_test_connection_is_true_on_200_and_targets_the_api_url(test_app):
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.get.return_value = _response(200)
            assert service.test_connection() is True

        requests_mock.get.assert_called_once_with(
            service.ZENODO_API_URL,
            params=service.params,
            headers=service.headers,
        )


def test_test_connection_is_false_on_error_status(test_app):
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.get.return_value = _response(401)
            assert service.test_connection() is False


def test_get_all_depositions_returns_the_parsed_body(test_app):
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.get.return_value = _response(200, [{"id": 1}, {"id": 2}])
            assert service.get_all_depositions() == [{"id": 1}, {"id": 2}]


def test_get_all_depositions_raises_on_error_status(test_app):
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.get.return_value = _response(500)
            with pytest.raises(Exception, match="Failed to get depositions"):
                service.get_all_depositions()


# --------------------------------------------------------------------------
# create_new_deposition
# --------------------------------------------------------------------------


def test_create_new_deposition_builds_a_dataset_payload(test_app, clean_database):
    with test_app.app_context():
        dataset = _create_dataset("dataset-payload@example.com")
        service = ZenodoService()

        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.post.return_value = _response(201, {"id": 42})
            assert service.create_new_deposition(dataset) == {"id": 42}

        url, kwargs = requests_mock.post.call_args[0][0], requests_mock.post.call_args[1]
        assert url == service.ZENODO_API_URL
        assert kwargs["params"] == service.params
        assert kwargs["headers"] == service.headers

        metadata = kwargs["json"]["metadata"]
        assert metadata["title"] == "Sample dataset"
        assert metadata["description"] == "A sample dataset description"
        # publication_type "none" means the deposition is a plain dataset.
        assert metadata["upload_type"] == "dataset"
        assert metadata["publication_type"] is None
        assert metadata["keywords"] == ["uvlhub"]
        assert metadata["access_right"] == "open"
        assert metadata["license"] == "CC-BY-4.0"
        assert metadata["creators"] == [{"name": "Jane Doe"}]


def test_create_new_deposition_builds_a_publication_payload_with_tags_and_authors(test_app, clean_database):
    with test_app.app_context():
        dataset = _create_dataset(
            "publication-payload@example.com",
            publication_type=PublicationType.JOURNAL_ARTICLE,
            tags="spl, uvl",
            authors=[
                Author(name="Jane Doe", affiliation="Uni", orcid="0000-0001"),
                Author(name="John Roe"),
            ],
        )
        service = ZenodoService()

        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.post.return_value = _response(201, {"id": 7})
            service.create_new_deposition(dataset)

        metadata = requests_mock.post.call_args[1]["json"]["metadata"]
        assert metadata["upload_type"] == "publication"
        assert metadata["publication_type"] == "article"
        assert metadata["keywords"] == ["spl", "uvl", "uvlhub"]
        # affiliation/orcid are only emitted when the author actually has them.
        assert metadata["creators"] == [
            {"name": "Jane Doe", "affiliation": "Uni", "orcid": "0000-0001"},
            {"name": "John Roe"},
        ]


def test_create_new_deposition_raises_when_zenodo_rejects_it(test_app, clean_database):
    with test_app.app_context():
        dataset = _create_dataset("rejected@example.com")
        service = ZenodoService()

        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.post.return_value = _response(400, {"message": "bad metadata"})
            with pytest.raises(Exception, match="Failed to create deposition"):
                service.create_new_deposition(dataset)


# --------------------------------------------------------------------------
# upload_file
# --------------------------------------------------------------------------


def test_upload_file_posts_the_uvl_file_to_the_deposition(test_app, clean_database, tmp_path, monkeypatch):
    with test_app.app_context():
        dataset = _create_dataset("upload@example.com")
        feature_model = _create_feature_model(dataset, "model.uvl")
        user = db.session.get(User, dataset.user_id)

        file_dir = tmp_path / f"user_{user.id}" / f"dataset_{dataset.id}"
        file_dir.mkdir(parents=True)
        (file_dir / "model.uvl").write_text("features\n    Root\n")

        monkeypatch.setattr("app.features.zenodo.services.uploads_folder_name", lambda: str(tmp_path))
        service = ZenodoService()

        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.post.return_value = _response(201, {"id": 99, "filename": "model.uvl"})
            result = service.upload_file(dataset, 42, feature_model, user=user)

        assert result == {"id": 99, "filename": "model.uvl"}
        url, kwargs = requests_mock.post.call_args[0][0], requests_mock.post.call_args[1]
        assert url == f"{service.ZENODO_API_URL}/42/files"
        assert kwargs["params"] == service.params
        assert kwargs["data"] == {"name": "model.uvl"}
        assert kwargs["files"]["file"].read() == b"features\n    Root\n"
        kwargs["files"]["file"].close()


def test_upload_file_raises_when_zenodo_rejects_the_upload(test_app, clean_database, tmp_path, monkeypatch):
    with test_app.app_context():
        dataset = _create_dataset("upload-fail@example.com")
        feature_model = _create_feature_model(dataset, "model.uvl")
        user = db.session.get(User, dataset.user_id)

        file_dir = tmp_path / f"user_{user.id}" / f"dataset_{dataset.id}"
        file_dir.mkdir(parents=True)
        (file_dir / "model.uvl").write_text("features\n")

        monkeypatch.setattr("app.features.zenodo.services.uploads_folder_name", lambda: str(tmp_path))
        service = ZenodoService()

        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.post.return_value = _response(413, {"message": "too large"})
            with pytest.raises(Exception, match="Failed to upload files"):
                service.upload_file(dataset, 42, feature_model, user=user)


# --------------------------------------------------------------------------
# publish_deposition / get_deposition / get_doi
# --------------------------------------------------------------------------


def test_publish_deposition_calls_the_publish_action(test_app):
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.post.return_value = _response(202, {"state": "done"})
            assert service.publish_deposition(11) == {"state": "done"}

        requests_mock.post.assert_called_once_with(
            f"{service.ZENODO_API_URL}/11/actions/publish",
            params=service.params,
            headers=service.headers,
        )


def test_publish_deposition_raises_on_unexpected_status(test_app):
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            # 201 is a success code elsewhere but publishing must answer 202.
            requests_mock.post.return_value = _response(201)
            with pytest.raises(Exception, match="Failed to publish deposition"):
                service.publish_deposition(11)


def test_get_deposition_requests_the_deposition_url(test_app):
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.get.return_value = _response(200, {"id": 11, "doi": "10.5281/zenodo.11"})
            assert service.get_deposition(11) == {"id": 11, "doi": "10.5281/zenodo.11"}

        requests_mock.get.assert_called_once_with(
            f"{service.ZENODO_API_URL}/11",
            params=service.params,
            headers=service.headers,
        )


def test_get_deposition_raises_on_error_status(test_app):
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.get.return_value = _response(404)
            with pytest.raises(Exception, match="Failed to get deposition"):
                service.get_deposition(11)


def test_get_doi_extracts_the_doi_from_the_deposition(test_app):
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.get.return_value = _response(200, {"id": 11, "doi": "10.5281/zenodo.11"})
            assert service.get_doi(11) == "10.5281/zenodo.11"


def test_get_doi_is_none_when_the_deposition_has_no_doi(test_app):
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.get.return_value = _response(200, {"id": 11})
            assert service.get_doi(11) is None


# --------------------------------------------------------------------------
# test_full_connection
# --------------------------------------------------------------------------


def test_full_connection_creates_uploads_and_deletes_the_deposition(test_app, tmp_path, monkeypatch):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.post.side_effect = [_response(201, {"id": 55}), _response(201, {"id": 1})]
            requests_mock.delete.return_value = _response(204)
            response = service.test_full_connection()

        assert response.get_json() == {"success": True, "messages": []}

        create_call, upload_call = requests_mock.post.call_args_list
        assert create_call[0][0] == service.ZENODO_API_URL
        assert create_call[1]["json"]["metadata"]["title"] == "Test Deposition"
        assert create_call[1]["json"]["metadata"]["upload_type"] == "dataset"
        assert upload_call[0][0] == f"{service.ZENODO_API_URL}/55/files"
        assert upload_call[1]["data"] == {"name": "test_file.txt"}
        requests_mock.delete.assert_called_once_with(
            f"{service.ZENODO_API_URL}/55",
            params=service.params,
        )
        # The temporary probe file is cleaned up on the happy path.
        assert not os.path.exists(str(tmp_path / "test_file.txt"))


def test_full_connection_reports_failure_when_the_deposition_cannot_be_created(test_app, tmp_path, monkeypatch):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.post.return_value = _response(403)
            response = service.test_full_connection()

        body = response.get_json()
        assert body["success"] is False
        assert "403" in body["messages"]
        # Nothing was created, so nothing may be uploaded or deleted.
        assert requests_mock.post.call_count == 1
        requests_mock.delete.assert_not_called()


def test_full_connection_reports_a_failed_upload_but_still_deletes_the_deposition(test_app, tmp_path, monkeypatch):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_app.app_context():
        service = ZenodoService()
        with patch("app.features.zenodo.services.requests") as requests_mock:
            requests_mock.post.side_effect = [_response(201, {"id": 66}), _response(400)]
            requests_mock.delete.return_value = _response(204)
            response = service.test_full_connection()

        body = response.get_json()
        assert body["success"] is False
        assert any("400" in message for message in body["messages"])
        requests_mock.delete.assert_called_once_with(
            f"{service.ZENODO_API_URL}/66",
            params=service.params,
        )
