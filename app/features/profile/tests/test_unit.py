"""Unit tests for the profile feature — pure logic, no Flask app, no DB."""

from unittest.mock import MagicMock

import pytest

from app.features.profile.models import UserProfile
from app.features.profile.services import UserProfileService

pytestmark = pytest.mark.unit


class StubForm:
    """Minimal stand-in for ``UserProfileForm`` (no app context required)."""

    def __init__(self, valid, data=None, errors=None):
        self._valid = valid
        self.data = data or {}
        self.errors = errors or {}

    def validate(self):
        return self._valid


def make_service():
    """Build a service whose repositories are replaced by mocks."""
    service = UserProfileService()
    service.repository = MagicMock()
    service._datasets = MagicMock()
    return service


def test_optional_profile_fields_default_to_none():
    profile = UserProfile(user_id=1, name="Ada", surname="Lovelace")
    assert profile.name == "Ada"
    assert profile.surname == "Lovelace"
    assert profile.orcid is None
    assert profile.affiliation is None


def test_update_profile_delegates_only_model_fields_to_repository():
    service = make_service()
    updated = object()
    service.repository.update.return_value = updated
    form = StubForm(
        valid=True,
        data={"name": "Ada", "surname": "Lovelace", "submit": True, "csrf_token": "token"},
    )

    instance, errors = service.update_profile(42, form)

    assert instance is updated
    assert errors is None
    # submit and csrf_token are form-only fields and must never reach the model.
    service.repository.update.assert_called_once_with(42, name="Ada", surname="Lovelace")


def test_update_profile_returns_errors_and_skips_repository_when_invalid():
    service = make_service()
    form = StubForm(valid=False, errors={"orcid": ["Invalid ORCID format"]})

    instance, errors = service.update_profile(42, form)

    assert instance is None
    assert errors == {"orcid": ["Invalid ORCID format"]}
    service.repository.update.assert_not_called()


def test_summary_for_user_assembles_pagination_payload():
    service = make_service()
    pagination = MagicMock()
    pagination.items = ["ds-1", "ds-2"]
    service._datasets.paginate_for_user.return_value = pagination
    service._datasets.count_for_user.return_value = 7

    summary = service.summary_for_user(9, page=2, per_page=3)

    assert summary == {
        "datasets": ["ds-1", "ds-2"],
        "pagination": pagination,
        "total_datasets": 7,
    }
    service._datasets.paginate_for_user.assert_called_once_with(9, 2, 3)
    service._datasets.count_for_user.assert_called_once_with(9)


def test_summary_for_user_uses_five_items_per_page_by_default():
    service = make_service()
    service._datasets.count_for_user.return_value = 0

    service.summary_for_user(9, page=1)

    service._datasets.paginate_for_user.assert_called_once_with(9, 1, 5)
