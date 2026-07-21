from splent_framework.repositories.BaseRepository import BaseRepository
from sqlalchemy import func

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet
from app.features.featuremodel.models import FeatureModel
from app.features.hubfile.models import Hubfile, HubfileDownloadRecord, HubfileViewRecord


class HubfileRepository(BaseRepository):
    def __init__(self):
        super().__init__(Hubfile)

    def get_owner_user_by_hubfile(self, hubfile: Hubfile) -> User:
        return (
            db.session.query(User)
            .join(DataSet)
            .join(FeatureModel)
            .join(Hubfile)
            .filter(Hubfile.id == hubfile.id)
            .first()
        )

    def get_dataset_by_hubfile(self, hubfile: Hubfile) -> DataSet:
        return db.session.query(DataSet).join(FeatureModel).join(Hubfile).filter(Hubfile.id == hubfile.id).first()


class HubfileViewRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(HubfileViewRecord)

    def total_hubfile_views(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

    def find_by_user_file_cookie(self, user_id, file_id: int, cookie: str):
        return self.model.query.filter_by(user_id=user_id, file_id=file_id, view_cookie=cookie).first()


class HubfileDownloadRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(HubfileDownloadRecord)

    def total_hubfile_downloads(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

    def find_by_user_file_cookie(self, user_id, file_id: int, cookie: str):
        return self.model.query.filter_by(user_id=user_id, file_id=file_id, download_cookie=cookie).first()
