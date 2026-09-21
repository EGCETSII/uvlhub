
from app.features.notepad.repositories import NotepadRepository
from splent_framework.services.BaseService import BaseService


class NotepadService(BaseService):
    def __init__(self):
        super().__init__(NotepadRepository())

    def get_all_by_user(self, user_id):
        return self.repository.get_all_by_user(user_id)