import os

from splent_framework.services.BaseService import BaseService

from app.features.auth.models import User
from app.features.dataset.models import DataSet
from app.features.hubfile.models import Hubfile
from app.features.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository,
)


class HubfileService(BaseService):
    def __init__(self):
        super().__init__(HubfileRepository())
        self.hubfile_view_record_repository = HubfileViewRecordRepository()
        self.hubfile_download_record_repository = HubfileDownloadRecordRepository()

    def get_owner_user_by_hubfile(self, hubfile: Hubfile) -> User:
        return self.repository.get_owner_user_by_hubfile(hubfile)

    def get_dataset_by_hubfile(self, hubfile: Hubfile) -> DataSet:
        return self.repository.get_dataset_by_hubfile(hubfile)

    def get_path_by_hubfile(self, hubfile: Hubfile) -> str:

        hubfile_user = self.get_owner_user_by_hubfile(hubfile)
        hubfile_dataset = self.get_dataset_by_hubfile(hubfile)
        working_dir = os.getenv("WORKING_DIR", "")

        path = os.path.join(
            working_dir, "uploads", f"user_{hubfile_user.id}", f"dataset_{hubfile_dataset.id}", hubfile.name
        )

        return path

    def total_hubfile_views(self) -> int:
        return self.hubfile_view_record_repository.total_hubfile_views()

    def total_hubfile_downloads(self) -> int:
        hubfile_download_record_repository = HubfileDownloadRecordRepository()
        return hubfile_download_record_repository.total_hubfile_downloads()

    def directory_for(self, hubfile: Hubfile) -> str:
        """Absolute filesystem directory holding the hubfile, for send_from_directory."""
        return os.path.dirname(self.get_path_by_hubfile(hubfile))

    def read_text(self, hubfile: Hubfile) -> str | None:
        """Read the hubfile's UVL content. Returns ``None`` if the file is missing."""
        path = self.get_path_by_hubfile(hubfile)
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return f.read()


class HubfileDownloadRecordService(BaseService):
    def __init__(self):
        super().__init__(HubfileDownloadRecordRepository())

    def record_download(self, user, file_id: int, cookie: str) -> None:
        """Record a download once per (user/anonymous, file, cookie) tuple."""
        from datetime import datetime, timezone

        user_id = user.id if user.is_authenticated else None
        if self.repository.find_by_user_file_cookie(user_id, file_id, cookie):
            return
        self.create(
            user_id=user_id,
            file_id=file_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=cookie,
        )


class HubfileViewRecordService(BaseService):
    def __init__(self):
        super().__init__(HubfileViewRecordRepository())

    def record_view(self, user, file_id: int, cookie: str) -> None:
        """Record a view once per (user/anonymous, file, cookie) tuple."""
        from datetime import datetime, timezone

        user_id = user.id if user.is_authenticated else None
        if self.repository.find_by_user_file_cookie(user_id, file_id, cookie):
            return
        self.create(
            user_id=user_id,
            file_id=file_id,
            view_date=datetime.now(timezone.utc),
            view_cookie=cookie,
        )
