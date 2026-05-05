from app.modules.zenodo.models import Zenodo
from splent_framework.repositories.BaseRepository import BaseRepository


class ZenodoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Zenodo)
