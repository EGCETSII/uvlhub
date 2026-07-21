import logging
from datetime import datetime, timezone
from typing import Optional

from flask_login import current_user
from splent_framework.repositories.BaseRepository import BaseRepository
from sqlalchemy import desc

from app.features.dataset.models import Author, DataSet, DOIMapping, DSDownloadRecord, DSMetaData, DSViewRecord

logger = logging.getLogger(__name__)


class AuthorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Author)


class DSDownloadRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSDownloadRecord)

    def total_dataset_downloads(self) -> int:
        return self.model.query.count()

    def find_by_user_dataset_cookie(self, user_id, dataset_id: int, cookie: str):
        return self.model.query.filter_by(user_id=user_id, dataset_id=dataset_id, download_cookie=cookie).first()


class DSMetaDataRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSMetaData)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.model.query.filter_by(dataset_doi=doi).first()


class DSViewRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSViewRecord)

    def total_dataset_views(self) -> int:
        return self.model.query.count()

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.model.query.filter_by(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_cookie=user_cookie,
        ).first()

    def create_new_record(self, dataset: DataSet, user_cookie: str) -> DSViewRecord:
        return self.create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_date=datetime.now(timezone.utc),
            view_cookie=user_cookie,
        )


class DataSetRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def get_synchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.isnot(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.is_(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DataSet.id == dataset_id, DSMetaData.dataset_doi.is_(None))
            .first()
        )

    def count_synchronized_datasets(self):
        return self.model.query.join(DSMetaData).filter(DSMetaData.dataset_doi.isnot(None)).count()

    def count_unsynchronized_datasets(self):
        return self.model.query.join(DSMetaData).filter(DSMetaData.dataset_doi.is_(None)).count()

    def paginate_for_user(self, user_id: int, page: int, per_page: int):
        return (
            self.model.query.filter(DataSet.user_id == user_id)
            .order_by(DataSet.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    def count_for_user(self, user_id: int) -> int:
        return self.model.query.filter(DataSet.user_id == user_id).count()

    def latest_synchronized(self):
        return (
            self.model.query.join(DSMetaData)
            .filter(DSMetaData.dataset_doi.isnot(None))
            .order_by(desc(self.model.id))
            .limit(5)
            .all()
        )


class DOIMappingRepository(BaseRepository):
    def __init__(self):
        super().__init__(DOIMapping)

    def get_new_doi(self, old_doi: str) -> str:
        return self.model.query.filter_by(dataset_doi_old=old_doi).first()
