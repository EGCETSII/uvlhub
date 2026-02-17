import hashlib
import logging
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

from flask import request

from app.modules.auth.services import AuthenticationService
from app.modules.dataset.fetchers.base import FetchError
from app.modules.dataset.fetchers.github import GithubFetcher
from app.modules.dataset.fetchers.registry import DataSourceManager
from app.modules.dataset.fetchers.zip import ZipFetcher
from app.modules.dataset.models import DataSet, DSMetaData, DSViewRecord
from app.modules.dataset.repositories import (
    AuthorRepository,
    DataSetRepository,
    DOIMappingRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
)
from app.modules.featuremodel.repositories import FeatureModelRepository, FMMetaDataRepository
from app.modules.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository,
)
from core.services.BaseService import BaseService

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

        # Initialize data source manager for GitHub/ZIP imports
        self.datasource_manager = DataSourceManager(
            providers=[
                GithubFetcher(),
                ZipFetcher(),
            ]
        )

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

    def get_uvlhub_doi(self, dataset: DataSet) -> str:
        domain = os.getenv("DOMAIN", "localhost")
        return f"http://{domain}/doi/{dataset.ds_meta_data.dataset_doi}"

    # ==================== IMPORT FROM GITHUB / ZIP ====================

    def _save_zip_to_temp(self, file_storage, current_user) -> Path:
        """
        Validates and saves the uploaded ZIP file to user's temp folder.
        Returns the path to the saved file.
        """
        if not file_storage or not file_storage.filename:
            raise FetchError("No ZIP file provided")

        filename = file_storage.filename
        if not filename.lower().endswith(".zip"):
            raise FetchError("Invalid file type. Only .zip allowed")

        user_temp = Path(current_user.temp_folder())
        user_temp.mkdir(parents=True, exist_ok=True)

        base_name = Path(filename).name
        target = user_temp / base_name

        # Avoid overwriting existing files
        i = 1
        while target.exists():
            stem = Path(base_name).stem
            suffix = Path(base_name).suffix
            target = user_temp / f"{stem} ({i}){suffix}"
            i += 1

        file_storage.save(str(target))
        return target

    def _collect_uvl_files_into_temp(self, source_root: Path, dest_dir: Path):
        """
        Copies all valid .uvl files from source_root to dest_dir.
        Also extracts and processes any ZIP files found inside.
        Returns list of copied file paths.
        """
        added = []

        for path in Path(source_root).rglob("*"):
            if not path.is_file():
                continue

            # Process nested ZIP files
            if path.suffix.lower() == ".zip":
                logger.info(f"Found nested ZIP file: {path.name}, extracting...")

                try:
                    with tempfile.TemporaryDirectory() as temp_extract_dir:
                        temp_extract_path = Path(temp_extract_dir)

                        with ZipFile(path, "r") as zip_ref:
                            for zip_info in zip_ref.infolist():
                                # Security: prevent path traversal attacks
                                if zip_info.filename.startswith("/") or ".." in zip_info.filename:
                                    logger.warning(f"Skipping dangerous path in ZIP: {zip_info.filename}")
                                    continue
                                zip_ref.extract(zip_info, temp_extract_path)

                        # Recursively search for UVL files inside extracted ZIP
                        zip_models = self._collect_uvl_files_into_temp(temp_extract_path, dest_dir)
                        added.extend(zip_models)

                        logger.info(f"Found {len(zip_models)} UVL files inside {path.name}")

                except Exception as e:
                    logger.warning(f"Could not process nested ZIP {path.name}: {e}")
                continue

            # Only process .uvl files (skip macOS metadata files starting with ._)
            if path.suffix.lower() != ".uvl":
                continue

            if path.name.startswith("._"):
                logger.debug(f"Skipping macOS metadata file: {path.name}")
                continue

            # Validate UVL file has content
            if path.stat().st_size == 0:
                logger.warning(f"Skipping empty file: {path.name}")
                continue

            # Copy to destination, avoiding name collisions
            dest_path = dest_dir / path.name
            counter = 1
            while dest_path.exists():
                stem = path.stem
                dest_path = dest_dir / f"{stem}_{counter}.uvl"
                counter += 1

            shutil.copy2(path, dest_path)
            added.append(dest_path)
            logger.info(f"Imported UVL file: {path.name}")

        return added

    def fetch_models_from_github(self, github_url: str, dest_dir: Path, current_user):
        """
        Clones/downloads GitHub repository to user's temp folder and copies .uvl files to dest_dir.
        """
        base_path = self.datasource_manager.fetch_to_user_temp(github_url, current_user)
        return self._collect_uvl_files_into_temp(base_path, dest_dir)

    def fetch_models_from_zip_upload(self, file_storage, dest_dir: Path, current_user):
        """
        Saves uploaded ZIP, extracts it, and copies .uvl files to dest_dir.
        """
        zip_path = self._save_zip_to_temp(file_storage, current_user)
        extracted_root = self.datasource_manager.fetch_to_user_temp(str(zip_path), current_user)
        return self._collect_uvl_files_into_temp(extracted_root, dest_dir)


class AuthorService(BaseService):
    def __init__(self):
        super().__init__(AuthorRepository())


class DSDownloadRecordService(BaseService):
    def __init__(self):
        super().__init__(DSDownloadRecordRepository())


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
