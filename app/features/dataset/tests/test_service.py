"""Service-level tests for dataset — orchestration on top of a real database."""

import os
import shutil
from datetime import datetime, timezone
from io import BytesIO
from zipfile import ZipFile

import pytest
from werkzeug.datastructures import FileStorage

from app.features.auth.repositories import UserRepository
from app.features.dataset.models import PublicationType
from app.features.dataset.repositories import AuthorRepository, DataSetRepository, DSMetaDataRepository
from app.features.dataset.services import (
    DataSetService,
    DOIMappingService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
)

pytestmark = pytest.mark.service


def _make_user(email):
    return UserRepository().create(email=email, password="secret")


def _make_dataset(user, title="Sample dataset", doi=None):
    meta = DSMetaDataRepository().create(
        title=title,
        description=f"Description for {title}",
        publication_type=PublicationType.DATA_MANAGEMENT_PLAN,
        dataset_doi=doi,
        tags="tag1,tag2",
    )
    return DataSetRepository().create(
        user_id=user.id,
        ds_meta_data_id=meta.id,
        created_at=datetime.now(timezone.utc),
    )


def _uvl_upload(filename, content=b"features\n\tRoot\n"):
    return FileStorage(stream=BytesIO(content), filename=filename, content_type="text/plain")


def test_synchronized_lookups_are_delegated_and_scoped_to_the_user(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        other = _make_user("other@example.com")
        synced = _make_dataset(owner, title="Synced", doi="10.1234/synced")
        local = _make_dataset(owner, title="Local")
        theirs = _make_dataset(other, title="Theirs", doi="10.1234/theirs")

        service = DataSetService()
        assert [d.id for d in service.get_synchronized(owner.id)] == [synced.id]
        assert [d.id for d in service.get_unsynchronized(owner.id)] == [local.id]
        assert service.get_unsynchronized_dataset(owner.id, local.id).id == local.id
        assert service.count_synchronized_datasets() == 2
        assert {d.id for d in service.latest_synchronized()} == {synced.id, theirs.id}


def test_counts_reflect_the_rows_actually_persisted(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Counted")
        AuthorRepository().create(name="Ada Lovelace", ds_meta_data_id=dataset.ds_meta_data_id)
        AuthorRepository().create(name="Alan Turing", ds_meta_data_id=dataset.ds_meta_data_id)

        service = DataSetService()
        assert service.count_authors() == 2
        assert service.count_dsmetadata() == 1
        assert service.count() == 1


def test_get_uvlhub_doi_builds_a_url_from_the_configured_domain(test_app, clean_database, monkeypatch):
    monkeypatch.setenv("DOMAIN", "uvlhub.test")
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Published", doi="10.1234/published")

        assert DataSetService().get_uvlhub_doi(dataset) == "http://uvlhub.test/doi/10.1234/published"


def test_dsmetadata_service_updates_and_finds_by_doi(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Draft")

        service = DSMetaDataService()
        assert service.filter_by_doi("10.1234/minted") is None

        service.update(dataset.ds_meta_data_id, dataset_doi="10.1234/minted", deposition_id=99)

        found = service.filter_by_doi("10.1234/minted")
        assert found is not None
        assert found.id == dataset.ds_meta_data_id
        assert found.deposition_id == 99


def test_doi_mapping_service_unwraps_the_new_doi(test_app, clean_database):
    with test_app.app_context():
        service = DOIMappingService()
        service.create(dataset_doi_old="10.1234/old", dataset_doi_new="10.5678/new")

        assert service.get_new_doi("10.1234/old") == "10.5678/new"
        assert service.get_new_doi("10.1234/unknown") is None


def test_record_download_is_recorded_once_per_cookie(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Downloadable")

        service = DSDownloadRecordService()
        service.record_download(owner, dataset.id, "cookie-a")
        service.record_download(owner, dataset.id, "cookie-a")
        assert service.count() == 1

        service.record_download(owner, dataset.id, "cookie-b")
        assert service.count() == 2


def test_create_cookie_registers_a_single_view_per_cookie(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Viewable")

        service = DSViewRecordService()
        with test_app.test_request_context("/", headers={"Cookie": "view_cookie=abc-123"}):
            assert service.create_cookie(dataset) == "abc-123"
            assert service.count() == 1

            # Same visitor, same cookie: no duplicate row.
            assert service.create_cookie(dataset) == "abc-123"
            assert service.count() == 1

        with test_app.test_request_context("/", headers={"Cookie": "view_cookie=def-456"}):
            service.create_cookie(dataset)
            assert service.count() == 2


def test_save_temp_uvl_rejects_files_that_are_not_uvl(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        result = DataSetService().save_temp_uvl(_uvl_upload("notes.txt"), owner)

        assert result["status"] == "error"
        assert result["code"] == 400
        assert result["message"] == "No valid file"
        assert not os.path.isdir(owner.temp_folder())


def test_save_temp_uvl_disambiguates_repeated_filenames(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        service = DataSetService()

        first = service.save_temp_uvl(_uvl_upload("model.uvl"), owner)
        second = service.save_temp_uvl(_uvl_upload("model.uvl"), owner)
        third = service.save_temp_uvl(_uvl_upload("model.uvl"), owner)

        assert first["filename"] == "model.uvl"
        assert second["filename"] == "model (1).uvl"
        assert third["filename"] == "model (2).uvl"
        assert sorted(os.listdir(owner.temp_folder())) == ["model (1).uvl", "model (2).uvl", "model.uvl"]


def test_delete_temp_file_removes_an_uploaded_file(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        service = DataSetService()

        saved = service.save_temp_uvl(_uvl_upload("model.uvl"), owner)
        assert os.path.exists(os.path.join(owner.temp_folder(), saved["filename"]))

        deleted = service.delete_temp_file(saved["filename"], owner)
        assert deleted["code"] == 200
        assert not os.path.exists(os.path.join(owner.temp_folder(), saved["filename"]))

        # Deleting the same file twice, or passing no filename at all, is an error.
        assert service.delete_temp_file(saved["filename"], owner)["code"] == 404
        assert service.delete_temp_file("", owner)["code"] == 400


def test_build_download_archive_zips_the_dataset_upload_folder(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Zippable")
        source_dir = tmp_path / "uploads" / f"user_{owner.id}" / f"dataset_{dataset.id}"
        source_dir.mkdir(parents=True)
        (source_dir / "file1.uvl").write_text("features\n\tRoot\n")

        tmp_dir, zip_name = DataSetService().build_download_archive(dataset)

        assert zip_name == f"dataset_{dataset.id}.zip"
        with ZipFile(os.path.join(tmp_dir, zip_name)) as archive:
            assert archive.namelist() == [f"dataset_{dataset.id}/file1.uvl"]
            assert archive.read(f"dataset_{dataset.id}/file1.uvl") == b"features\n\tRoot\n"
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_build_download_archive_yields_an_empty_zip_when_nothing_was_uploaded(
    test_app, clean_database, monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Empty")

        tmp_dir, zip_name = DataSetService().build_download_archive(dataset)
        with ZipFile(os.path.join(tmp_dir, zip_name)) as archive:
            assert archive.namelist() == []
        shutil.rmtree(tmp_dir, ignore_errors=True)
