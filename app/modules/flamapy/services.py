from app.modules.flamapy.repositories import FlamapyRepository
from splent_framework.services.BaseService import BaseService


class FlamapyService(BaseService):
    def __init__(self):
        super().__init__(FlamapyRepository())
