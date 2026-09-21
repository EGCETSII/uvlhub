from app import db
from app.features.notepad.models import Notepad


class NotepadRepository:
    def get_all_by_user(self, user_id):
        return Notepad.query.filter_by(user_id=user_id).all()

    def get_by_id(self, notepad_id):
        return Notepad.query.get(notepad_id)

    def create(self, title, body, user_id):
        notepad = Notepad(title=title, body=body, user_id=user_id)
        db.session.add(notepad)
        db.session.commit()
        return notepad

    def delete(self, notepad_id):
        notepad = Notepad.query.get(notepad_id)
        if notepad:
            db.session.delete(notepad)
            db.session.commit()
            return True
        return False
