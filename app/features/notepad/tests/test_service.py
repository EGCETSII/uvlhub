import pytest

from app.features.auth.repositories import UserRepository
from app.features.notepad.services import NotepadService

pytestmark = pytest.mark.service


def test_get_all_by_user_only_returns_own_notepads(test_app):
    with test_app.app_context():
        service = NotepadService()
        mine = UserRepository().create(email="mine@example.com", password="secret")
        theirs = UserRepository().create(email="theirs@example.com", password="secret")

        service.create(title="Mine", body="...", user_id=mine.id)
        service.create(title="Theirs", body="...", user_id=theirs.id)

        notepads = service.get_all_by_user(mine.id)

        assert [n.title for n in notepads] == ["Mine"]


