from app.features.notepad.repositories import NotepadRepository


class NotepadService:
    def __init__(self):
        self.repository = NotepadRepository()

    def get_all_by_user(self, user_id):
        return self.repository.get_all_by_user(user_id)

    def create(self, title, body, user_id):
        return self.repository.create(title=title, body=body, user_id=user_id)

    def delete(self, notepad_id, user_id):
        notepad = self.repository.get_by_id(notepad_id)
        if notepad and notepad.user_id == user_id:
            return self.repository.delete(notepad_id)
        return False
