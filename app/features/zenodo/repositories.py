from splent_framework.repositories.BaseRepository import BaseRepository

from app.features.zenodo.models import Zenodo


class ZenodoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Zenodo)
