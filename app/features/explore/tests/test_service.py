"""Service-level tests for explore — ExploreService orchestration with a real DB."""

from datetime import datetime

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import Author, DataSet, DSMetaData, PublicationType
from app.features.explore.services import ExploreService
from app.features.featuremodel.models import FeatureModel, FMMetaData

pytestmark = pytest.mark.service


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


def _seed_corpus():
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


def _titles(datasets):
    return [dataset.ds_meta_data.title for dataset in datasets]


def test_filter_without_arguments_returns_every_dataset(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        assert _titles(ExploreService().filter()) == ["Home Banking", "Car Configurator", "Smart Home"]


def test_filter_returns_nothing_when_the_database_is_empty(test_app, clean_database):
    with test_app.app_context():
        assert ExploreService().filter(query="home") == []


def test_filter_passes_the_query_through_to_the_repository(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        assert _titles(ExploreService().filter(query="alice")) == ["Smart Home"]


def test_filter_forwards_sorting_to_the_repository(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        service = ExploreService()
        assert _titles(service.filter(query="home", sorting="oldest")) == ["Smart Home", "Home Banking"]
        assert _titles(service.filter(query="home", sorting="newest")) == ["Home Banking", "Smart Home"]


def test_filter_forwards_publication_type_to_the_repository(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        assert _titles(ExploreService().filter(publication_type="book")) == ["Car Configurator"]
