"""HTTP integration tests for explore via the Flask test client."""

from datetime import datetime

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import Author, DataSet, DSMetaData, PublicationType
from app.features.featuremodel.models import FeatureModel, FMMetaData

pytestmark = pytest.mark.integration


def _owner():
    user = User.query.filter_by(email="owner@example.com").first()
    if user is None:
        user = User(email="owner@example.com")
        user.set_password("ownerpass")
        db.session.add(user)
        db.session.flush()
    return user


def _make_dataset(title, description, author_name, tags, created_at, publication_type):
    ds_meta_data = DSMetaData(
        title=title,
        description=description,
        publication_type=publication_type,
        dataset_doi="10.1234/default",
        tags=tags,
    )
    db.session.add(ds_meta_data)
    db.session.flush()
    db.session.add(Author(name=author_name, affiliation="Some University", ds_meta_data_id=ds_meta_data.id))
    dataset = DataSet(user_id=_owner().id, ds_meta_data_id=ds_meta_data.id, created_at=created_at)
    fm_meta_data = FMMetaData(
        uvl_filename=f"{title.lower().replace(' ', '_')}.uvl",
        title=title,
        description=description,
        publication_type=publication_type,
        tags=tags,
    )
    db.session.add_all([dataset, fm_meta_data])
    db.session.flush()
    db.session.add(FeatureModel(data_set_id=dataset.id, fm_meta_data_id=fm_meta_data.id))
    db.session.commit()
    return dataset


def _seed_corpus(test_app):
    with test_app.app_context():
        _make_dataset(
            "Smart Home",
            "home automation product line",
            "Alice Doe",
            "iot,home",
            datetime(2024, 1, 1),
            PublicationType.JOURNAL_ARTICLE,
        )
        _make_dataset(
            "Car Configurator",
            "vehicle variability",
            "Bob Roe",
            "automotive",
            datetime(2024, 2, 1),
            PublicationType.BOOK,
        )
        _make_dataset(
            "Home Banking",
            "finance product line",
            "Carol Poe",
            "finance",
            datetime(2024, 3, 1),
            PublicationType.JOURNAL_ARTICLE,
        )


def test_explore_page_renders_the_search_form(test_client):
    response = test_client.get("/explore")
    assert response.status_code == 200
    assert b"<b>Explore</b>" in response.data
    assert b'name="query"' in response.data
    assert b'name="publication_type"' in response.data


def test_search_returns_only_the_matching_datasets(test_app, test_client):
    _seed_corpus(test_app)
    response = test_client.post("/explore", json={"query": "alice"})
    assert response.status_code == 200
    payload = response.get_json()
    assert [dataset["title"] for dataset in payload] == ["Smart Home"]
    assert [author["name"] for author in payload[0]["authors"]] == ["Alice Doe"]
    assert payload[0]["tags"] == ["iot", "home"]


def test_search_with_an_empty_payload_returns_every_dataset_newest_first(test_app, test_client):
    _seed_corpus(test_app)
    response = test_client.post("/explore", json={})
    assert response.status_code == 200
    assert [dataset["title"] for dataset in response.get_json()] == [
        "Home Banking",
        "Car Configurator",
        "Smart Home",
    ]


def test_search_honours_sorting_and_publication_type(test_app, test_client):
    _seed_corpus(test_app)

    oldest = test_client.post("/explore", json={"query": "home", "sorting": "oldest"})
    assert [dataset["title"] for dataset in oldest.get_json()] == ["Smart Home", "Home Banking"]

    books = test_client.post("/explore", json={"query": "", "publication_type": "book"})
    assert [dataset["title"] for dataset in books.get_json()] == ["Car Configurator"]


def test_search_returns_an_empty_list_when_nothing_matches(test_app, test_client):
    _seed_corpus(test_app)
    response = test_client.post("/explore", json={"query": "nothingmatchesthis"})
    assert response.status_code == 200
    assert response.get_json() == []


def test_search_without_a_json_body_behaves_like_an_unfiltered_search(test_app, test_client):
    _seed_corpus(test_app)
    response = test_client.post("/explore")
    assert response.status_code == 200
    assert [dataset["title"] for dataset in response.get_json()] == [
        "Home Banking",
        "Car Configurator",
        "Smart Home",
    ]
