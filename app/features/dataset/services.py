import hashlib
import logging
import os
import shutil
import uuid
from typing import Optional

from flask import request

from app.features.auth.services import AuthenticationService
from app.features.dataset.models import DataSet, DSMetaData, DSViewRecord
from app.features.dataset.repositories import (
    AuthorRepository,
    DataSetRepository,
    DOIMappingRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
)
from app.features.featuremodel.repositories import FeatureModelRepository, FMMetaDataRepository
from app.features.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository,
)
from splent_framework.services.BaseService import BaseService

logger = logging.getLogger(__name__)


def calculate_checksum_and_size(file_path):
    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as file:
        content = file.read()
        hash_md5 = hashlib.md5(content).hexdigest()
        return hash_md5, file_size


class DataSetService(BaseService):
    def __init__(self):
        super().__init__(DataSetRepository())
        self.feature_model_repository = FeatureModelRepository()
        self.author_repository = AuthorRepository()
        self.dsmetadata_repository = DSMetaDataRepository()
        self.fmmetadata_repository = FMMetaDataRepository()
        self.dsdownloadrecord_repository = DSDownloadRecordRepository()
        self.hubfiledownloadrecord_repository = HubfileDownloadRecordRepository()
        self.hubfilerepository = HubfileRepository()
        self.dsviewrecord_repostory = DSViewRecordRepository()
        self.hubfileviewrecord_repository = HubfileViewRecordRepository()

    def move_feature_models(self, dataset: DataSet):
        current_user = AuthenticationService().get_authenticated_user()
        source_dir = current_user.temp_folder()

        working_dir = os.getenv("WORKING_DIR", "")
        dest_dir = os.path.join(working_dir, "uploads", f"user_{current_user.id}", f"dataset_{dataset.id}")

        os.makedirs(dest_dir, exist_ok=True)

        for feature_model in dataset.feature_models:
            uvl_filename = feature_model.fm_meta_data.uvl_filename
            shutil.move(os.path.join(source_dir, uvl_filename), dest_dir)

    def get_synchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_synchronized(current_user_id)

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_unsynchronized(current_user_id)

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return self.repository.get_unsynchronized_dataset(current_user_id, dataset_id)

    def latest_synchronized(self):
        return self.repository.latest_synchronized()

    def count_synchronized_datasets(self):
        return self.repository.count_synchronized_datasets()

    def count_feature_models(self):
        return self.feature_model_service.count_feature_models()

    def count_authors(self) -> int:
        return self.author_repository.count()

    def count_dsmetadata(self) -> int:
        return self.dsmetadata_repository.count()

    def total_dataset_downloads(self) -> int:
        return self.dsdownloadrecord_repository.total_dataset_downloads()

    def total_dataset_views(self) -> int:
        return self.dsviewrecord_repostory.total_dataset_views()

    def create_from_form(self, form, current_user) -> DataSet:
        main_author = {
            "name": f"{current_user.profile.surname}, {current_user.profile.name}",
            "affiliation": current_user.profile.affiliation,
            "orcid": current_user.profile.orcid,
        }
        try:
            logger.info(f"Creating dsmetadata...: {form.get_dsmetadata()}")
            dsmetadata = self.dsmetadata_repository.create(**form.get_dsmetadata())
            for author_data in [main_author] + form.get_authors():
                author = self.author_repository.create(commit=False, ds_meta_data_id=dsmetadata.id, **author_data)
                dsmetadata.authors.append(author)

            dataset = self.create(commit=False, user_id=current_user.id, ds_meta_data_id=dsmetadata.id)

            for feature_model in form.feature_models:
                uvl_filename = feature_model.uvl_filename.data
                fmmetadata = self.fmmetadata_repository.create(commit=False, **feature_model.get_fmmetadata())
                for author_data in feature_model.get_authors():
                    author = self.author_repository.create(commit=False, fm_meta_data_id=fmmetadata.id, **author_data)
                    fmmetadata.authors.append(author)

                fm = self.feature_model_repository.create(
                    commit=False, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
                )

                # associated files in feature model
                file_path = os.path.join(current_user.temp_folder(), uvl_filename)
                checksum, size = calculate_checksum_and_size(file_path)

                file = self.hubfilerepository.create(
                    commit=False, name=uvl_filename, checksum=checksum, size=size, feature_model_id=fm.id
                )
                fm.files.append(file)
            self.repository.session.commit()
        except Exception as exc:
            logger.info(f"Exception creating dataset from form...: {exc}")
            self.repository.session.rollback()
            raise exc
        return dataset

    def update_dsmetadata(self, id, **kwargs):
        return self.dsmetadata_repository.update(id, **kwargs)

    def save_temp_uvl(self, file, current_user) -> dict:
        """Persist an uploaded UVL file under the current user's temp folder.

        Disambiguates collisions by appending ``" (n)"`` until the name is
        free. Returns a result dict the route turns into JSON.
        """
        if not file or not file.filename.endswith(".uvl"):
            return {"status": "error", "code": 400, "message": "No valid file"}

        temp_folder = current_user.temp_folder()
        os.makedirs(temp_folder, exist_ok=True)

        filename = file.filename
        target = os.path.join(temp_folder, filename)
        if os.path.exists(target):
            base, ext = os.path.splitext(filename)
            i = 1
            while os.path.exists(os.path.join(temp_folder, f"{base} ({i}){ext}")):
                i += 1
            filename = f"{base} ({i}){ext}"
            target = os.path.join(temp_folder, filename)

        try:
            file.save(target)
        except Exception as exc:
            return {"status": "error", "code": 500, "message": str(exc)}

        return {
            "status": "ok",
            "code": 200,
            "message": "UVL uploaded and validated successfully",
            "filename": filename,
        }

    def delete_temp_file(self, filename: str, current_user) -> dict:
        """Remove a previously-uploaded UVL from the user's temp folder."""
        if not filename:
            return {"status": "error", "code": 400, "error": "Error: filename missing"}
        target = os.path.join(current_user.temp_folder(), filename)
        if not os.path.exists(target):
            return {"status": "error", "code": 404, "error": "Error: File not found"}
        os.remove(target)
        return {"status": "ok", "code": 200, "message": "File deleted successfully"}

    def upload_dataset(self, form, current_user) -> dict:
        """End-to-end dataset upload: persist locally, push to Zenodo, clean up.

        Returns a result dict with ``status`` ("ok" | "partial" | "error") and a
        ``message`` summarising what happened. The route layer only needs to
        translate that into a JSON response — none of this orchestration
        belongs in a request handler.
        """
        # ── Persist locally ─────────────────────────────────────────────
        try:
            dataset = self.create_from_form(form=form, current_user=current_user)
            logger.info("Created dataset: %s", dataset)
            self.move_feature_models(dataset)
        except Exception as exc:
            logger.exception("Exception while creating dataset locally: %s", exc)
            return {"status": "error", "code": 400, "message": str(exc)}

        # ── Push to Zenodo (best-effort: failure here is "partial") ─────
        # Imported inside the method to avoid a circular import at module load.
        from app.features.zenodo.services import ZenodoService

        zenodo = ZenodoService()
        zenodo_data = {}
        try:
            zenodo_data = zenodo.create_new_deposition(dataset) or {}
        except Exception as exc:
            logger.exception("Exception while creating deposition in Zenodo: %s", exc)

        if zenodo_data.get("conceptrecid"):
            deposition_id = zenodo_data.get("id")
            self.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)
            try:
                for feature_model in dataset.feature_models:
                    zenodo.upload_file(dataset, deposition_id, feature_model)
                zenodo.publish_deposition(deposition_id)
                deposition_doi = zenodo.get_doi(deposition_id)
                self.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi)
            except Exception as exc:
                msg = f"could not upload feature models to Zenodo and update DOI: {exc}"
                # The local dataset already exists; surface a 200 with a warning.
                return {"status": "partial", "code": 200, "message": msg}

        # ── Clean up the user's temp folder ─────────────────────────────
        temp_path = current_user.temp_folder()
        if os.path.isdir(temp_path):
            shutil.rmtree(temp_path)

        return {"status": "ok", "code": 200, "message": "Everything works!"}

    def build_download_archive(self, dataset: DataSet) -> tuple[str, str]:
        """Zip the dataset's uploaded files and return ``(zip_path, filename)``.

        ``zip_path`` lives under a fresh tempdir; the caller is responsible for
        sending it (usually via ``send_from_directory``) — Linux keeps the
        inode alive until the response stream drains, so the tempdir can be
        left to OS cleanup.
        """
        import tempfile
        from zipfile import ZipFile

        source_dir = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"
        tmp_dir = tempfile.mkdtemp()
        zip_name = f"dataset_{dataset.id}.zip"
        zip_path = os.path.join(tmp_dir, zip_name)

        with ZipFile(zip_path, "w") as zipf:
            for subdir, _dirs, files in os.walk(source_dir):
                for filename in files:
                    full_path = os.path.join(subdir, filename)
                    relative_path = os.path.relpath(full_path, source_dir)
                    zipf.write(full_path, arcname=os.path.join(zip_name[:-4], relative_path))

        return tmp_dir, zip_name

    def get_uvlhub_doi(self, dataset: DataSet) -> str:
        domain = os.getenv("DOMAIN", "localhost")
        return f"http://{domain}/doi/{dataset.ds_meta_data.dataset_doi}"


class AuthorService(BaseService):
    def __init__(self):
        super().__init__(AuthorRepository())


class DSDownloadRecordService(BaseService):
    def __init__(self):
        super().__init__(DSDownloadRecordRepository())

    def record_download(self, user, dataset_id: int, cookie: str) -> None:
        """Record a download once per (user/anonymous, dataset, cookie) tuple."""
        from datetime import datetime, timezone

        from app.features.dataset.models import DSDownloadRecord

        user_id = user.id if user.is_authenticated else None
        already = DSDownloadRecord.query.filter_by(
            user_id=user_id, dataset_id=dataset_id, download_cookie=cookie
        ).first()
        if already:
            return
        self.create(
            user_id=user_id,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=cookie,
        )


class DSMetaDataService(BaseService):
    def __init__(self):
        super().__init__(DSMetaDataRepository())

    def update(self, id, **kwargs):
        return self.repository.update(id, **kwargs)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.repository.filter_by_doi(doi)


class DSViewRecordService(BaseService):
    def __init__(self):
        super().__init__(DSViewRecordRepository())

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.repository.the_record_exists(dataset, user_cookie)

    def create_new_record(self, dataset: DataSet, user_cookie: str) -> DSViewRecord:
        return self.repository.create_new_record(dataset, user_cookie)

    def create_cookie(self, dataset: DataSet) -> str:

        user_cookie = request.cookies.get("view_cookie")
        if not user_cookie:
            user_cookie = str(uuid.uuid4())

        existing_record = self.the_record_exists(dataset=dataset, user_cookie=user_cookie)

        if not existing_record:
            self.create_new_record(dataset=dataset, user_cookie=user_cookie)

        return user_cookie


class DOIMappingService(BaseService):
    def __init__(self):
        super().__init__(DOIMappingRepository())

    def get_new_doi(self, old_doi: str) -> str:
        doi_mapping = self.repository.get_new_doi(old_doi)
        if doi_mapping:
            return doi_mapping.dataset_doi_new
        else:
            return None


class SizeService:

    def __init__(self):
        pass

    def get_human_readable_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024**2:
            return f"{round(size / 1024, 2)} KB"
        elif size < 1024**3:
            return f"{round(size / (1024 ** 2), 2)} MB"
        else:
            return f"{round(size / (1024 ** 3), 2)} GB"
