"""HTTP integration tests for profile via the Flask test client."""

from datetime import datetime, timedelta

import pytest

from app import db
from app.features.dataset.models import DataSet, DSMetaData, PublicationType
from app.features.profile.repositories import UserProfileRepository

pytestmark = pytest.mark.integration

BASE_TIME = datetime(2024, 1, 1, 12, 0, 0)


def signup(test_client, email="profile-user@example.com", name="Ada", surname="Lovelace"):
    """Register and log in a user, returning the response of the signup POST."""
    return test_client.post(
        "/signup/",
        data={"email": email, "password": "profilepass", "name": name, "surname": surname},
        follow_redirects=False,
    )


def make_dataset(user_id, title, created_at):
    meta = DSMetaData(
        title=title,
        description=f"Description for {title}",
        publication_type=PublicationType.NONE,
    )
    db.session.add(meta)
    db.session.flush()
    db.session.add(DataSet(user_id=user_id, ds_meta_data_id=meta.id, created_at=created_at))
    db.session.commit()


def test_summary_requires_login(test_client):
    response = test_client.get("/profile/summary", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/login" in response.headers["Location"]


def test_edit_requires_login(test_client):
    response = test_client.get("/profile/edit", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/login" in response.headers["Location"]


def test_summary_renders_profile_details(test_app, test_client):
    signup(test_client, email="summary@example.com", name="Ada", surname="Lovelace")

    response = test_client.get("/profile/summary")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Ada" in body
    assert "Lovelace" in body
    assert "summary@example.com" in body
    assert "0 datasets" in body


def test_summary_lists_owned_datasets_and_paginates(test_app, test_client):
    signup(test_client, email="datasets@example.com")
    with test_app.app_context():
        profile = UserProfileRepository().get_by_column("user_id", 1)[0]
        for index in range(7):
            make_dataset(profile.user_id, f"dataset-{index}", BASE_TIME + timedelta(minutes=index))

    first = test_client.get("/profile/summary")
    second = test_client.get("/profile/summary?page=2")

    first_body = first.get_data(as_text=True)
    second_body = second.get_data(as_text=True)
    assert "7 datasets" in first_body
    # Default page size is 5, newest first.
    assert "dataset-6" in first_body
    assert "dataset-0" not in first_body
    assert "dataset-0" in second_body
    assert "dataset-1" in second_body
    assert "dataset-6" not in second_body


def test_edit_page_renders_form_fields(test_client):
    signup(test_client, email="editpage@example.com")

    response = test_client.get("/profile/edit")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert 'name="name"' in body
    assert 'name="surname"' in body
    assert 'name="orcid"' in body


def test_edit_post_updates_profile_and_redirects(test_app, test_client):
    signup(test_client, email="editpost@example.com", name="Ada", surname="Lovelace")

    response = test_client.post(
        "/profile/edit",
        data={
            "name": "Augusta",
            "surname": "King",
            "orcid": "0000-0001-2345-6789",
            "affiliation": "Analytical Engine Lab",
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert "/profile/edit" in response.headers["Location"]
    with test_app.app_context():
        profile = UserProfileRepository().get_by_column("user_id", 1)[0]
        assert profile.name == "Augusta"
        assert profile.surname == "King"
        assert profile.orcid == "0000-0001-2345-6789"


def test_edit_post_with_invalid_orcid_rerenders_with_error(test_app, test_client):
    signup(test_client, email="editbad@example.com", name="Ada", surname="Lovelace")

    response = test_client.post(
        "/profile/edit",
        data={"name": "Augusta", "surname": "King", "orcid": "123"},
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert "orcid" in response.get_data(as_text=True).lower()
    with test_app.app_context():
        profile = UserProfileRepository().get_by_column("user_id", 1)[0]
        assert profile.name == "Ada"
        assert profile.orcid is None
