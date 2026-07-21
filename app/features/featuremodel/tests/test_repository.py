"""Repository-level tests for featuremodel — repositories against the DB."""

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet, DSMetaData, PublicationType
from app.features.featuremodel.repositories import FeatureModelRepository, FMMetaDataRepository

pytestmark = pytest.mark.repository


def _make_dataset():
    """Create the DataSet a FeatureModel needs, since data_set_id is NOT NULL."""
    user = User(email="owner@example.com")
    user.set_password("ownerpass")
    ds_meta_data = DSMetaData(
        title="Host dataset",
        description="Holds the feature models under test",
        publication_type=PublicationType.JOURNAL_ARTICLE,
        dataset_doi="10.1234/host",
    )
    db.session.add_all([user, ds_meta_data])
    db.session.flush()
    dataset = DataSet(user_id=user.id, ds_meta_data_id=ds_meta_data.id)
    db.session.add(dataset)
    db.session.commit()
    return dataset


def _make_feature_model(dataset, title):
    meta_data = FMMetaDataRepository().create(
        uvl_filename=f"{title.lower().replace(' ', '_')}.uvl",
        title=title,
        description=f"{title} description",
        publication_type=PublicationType.JOURNAL_ARTICLE,
    )
    return FeatureModelRepository().create(data_set_id=dataset.id, fm_meta_data_id=meta_data.id)


def test_count_feature_models_is_zero_on_an_empty_database(test_app, clean_database):
    with test_app.app_context():
        assert FeatureModelRepository().count_feature_models() == 0


def test_count_feature_models_grows_with_each_created_model(test_app, clean_database):
    with test_app.app_context():
        dataset = _make_dataset()
        _make_feature_model(dataset, "Smart Home")
        assert FeatureModelRepository().count_feature_models() == 1
        _make_feature_model(dataset, "Car Configurator")
        assert FeatureModelRepository().count_feature_models() == 2


def test_count_feature_models_drops_when_a_model_is_deleted(test_app, clean_database):
    with test_app.app_context():
        dataset = _make_dataset()
        first = _make_feature_model(dataset, "Smart Home")
        _make_feature_model(dataset, "Car Configurator")

        repository = FeatureModelRepository()
        assert repository.delete(first.id) is True
        assert repository.count() == 1
        assert repository.count_feature_models() == 1


def test_created_feature_model_is_linked_to_its_dataset_and_metadata(test_app, clean_database):
    with test_app.app_context():
        dataset = _make_dataset()
        feature_model = _make_feature_model(dataset, "Smart Home")

        stored = FeatureModelRepository().get_by_id(feature_model.id)
        assert stored is not None
        assert stored.data_set_id == dataset.id
        assert stored.fm_meta_data.title == "Smart Home"
        assert stored.fm_meta_data.uvl_filename == "smart_home.uvl"
        assert stored.data_set.ds_meta_data.title == "Host dataset"


def test_fm_meta_data_repository_finds_metadata_by_column(test_app, clean_database):
    with test_app.app_context():
        dataset = _make_dataset()
        _make_feature_model(dataset, "Smart Home")
        _make_feature_model(dataset, "Car Configurator")

        found = FMMetaDataRepository().get_by_column("title", "Car Configurator")
        assert [meta_data.uvl_filename for meta_data in found] == ["car_configurator.uvl"]
