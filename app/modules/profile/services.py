import re
from app.modules.profile.repositories import UserProfileRepository
from core.services.BaseService import BaseService


class UserProfileService(BaseService):
    def __init__(self):
        super().__init__(UserProfileRepository())

    def update_profile(self, user_profile_id, form):

        try:
            name = form.name.data
            surname = form.surname.data
            affiliation = form.affiliation.data
            orcid = form.orcid.data

            if not name:
                raise ValueError("Name is required.")
            if len(name) > 100:
                raise ValueError("Name is too long.")
            if not surname:
                raise ValueError("Surname is required.")
            if len(surname) > 100:
                raise ValueError("Surname is too long.")
            if len(orcid) != 19 and len(orcid) != 0:
                raise ValueError("ORCID must have 16 numbers separated by dashes.")
            if orcid and not re.match(r'^\d{4}-\d{4}-\d{4}-\d{4}$', orcid):
                raise ValueError("Invalid ORCID format.")
            if affiliation and (len(affiliation) > 100 or len(affiliation) < 5):
                raise ValueError("Invalid affiliation length.")

            profile_data = {
                "name": name,
                "surname": surname,
                "affiliation": affiliation,
                "orcid": orcid
            }

            updated_instance = self.update(user_profile_id, **profile_data)

            self.repository.session.commit()

        except Exception as exc:
            self.repository.session.rollback()
            raise exc

        return updated_instance
