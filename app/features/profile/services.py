from splent_framework.services.BaseService import BaseService

from app.features.dataset.repositories import DataSetRepository
from app.features.profile.repositories import UserProfileRepository


class UserProfileService(BaseService):
    #: Form fields that do not exist on the UserProfile model.
    NON_MODEL_FIELDS = ("submit", "csrf_token")

    def __init__(self):
        super().__init__(UserProfileRepository())
        self._datasets = DataSetRepository()

    def update_profile(self, user_profile_id, form):
        if form.validate():
            updates = {key: value for key, value in form.data.items() if key not in self.NON_MODEL_FIELDS}
            updated_instance = self.update(user_profile_id, **updates)
            return updated_instance, None

        return None, form.errors

    def summary_for_user(self, user_id: int, page: int, per_page: int = 5) -> dict:
        """Build the data needed by ``profile/summary.html`` for *user_id*."""
        pagination = self._datasets.paginate_for_user(user_id, page, per_page)
        return {
            "datasets": pagination.items,
            "pagination": pagination,
            "total_datasets": self._datasets.count_for_user(user_id),
        }
