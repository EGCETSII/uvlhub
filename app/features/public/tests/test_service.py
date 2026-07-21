"""Service-level tests for public — the statistics the landing page aggregates.

The public feature owns no models of its own: its only route builds the
homepage out of ``DataSetService`` and ``FeatureModelService`` calls. These
tests pin that aggregation contract against a real database.
"""

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet, DSDownloadRecord, DSMetaData, DSViewRecord, PublicationType
from app.features.dataset.services import DataSetService
from app.features.featuremodel.models import FeatureModel
from app.features.featuremodel.services import FeatureModelService
from app.features.hubfile.models import Hubfile, HubfileDownloadRecord, HubfileViewRecord

pytestmark = pytest.mark.service


def _create_user(email="owner@example.com"):
    user = User(email=email, password="ownerpass")
    db.session.add(user)
    db.session.commit()
    return user


def _create_dataset(user, title, dataset_doi="10.1234/dataset"):
    meta = DSMetaData(
        title=title,
        description=f"Description of {title}",
        publication_type=PublicationType.JOURNAL_ARTICLE,
        dataset_doi=dataset_doi,
        tags="uvl,test",
    )
    db.session.add(meta)
    db.session.commit()

    dataset = DataSet(user_id=user.id, ds_meta_data_id=meta.id)
    db.session.add(dataset)
    db.session.commit()
    return dataset


def _create_feature_model_with_file(dataset):
    feature_model = FeatureModel(data_set_id=dataset.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="model.uvl", checksum="abc123", size=42, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()
    return feature_model, hubfile


def test_homepage_statistics_are_zero_on_empty_database(test_app, clean_database):
    with test_app.app_context():
        dataset_service = DataSetService()
        feature_model_service = FeatureModelService()

        assert dataset_service.latest_synchronized() == []
        assert dataset_service.count_synchronized_datasets() == 0
        assert feature_model_service.count_feature_models() == 0
        assert dataset_service.total_dataset_downloads() == 0
        assert dataset_service.total_dataset_views() == 0
        assert feature_model_service.total_feature_model_downloads() == 0
        assert feature_model_service.total_feature_model_views() == 0


def test_counters_reflect_persisted_rows(test_app, clean_database):
    with test_app.app_context():
        user = _create_user()
        synced = _create_dataset(user, "Synced dataset", dataset_doi="10.1234/synced")
        _create_dataset(user, "Draft dataset", dataset_doi=None)

        _, hubfile = _create_feature_model_with_file(synced)
        _create_feature_model_with_file(synced)

        db.session.add(DSViewRecord(dataset_id=synced.id, view_cookie="view-cookie"))
        db.session.add_all([DSDownloadRecord(dataset_id=synced.id, download_cookie=f"dl-{i}") for i in range(2)])
        db.session.add_all([HubfileViewRecord(file_id=hubfile.id, view_cookie=f"fview-{i}") for i in range(3)])
        db.session.add_all([HubfileDownloadRecord(file_id=hubfile.id, download_cookie=f"fdl-{i}") for i in range(4)])
        db.session.commit()

        dataset_service = DataSetService()
        feature_model_service = FeatureModelService()

        # Only the dataset carrying a DOI counts as synchronized.
        assert dataset_service.count_synchronized_datasets() == 1
        assert feature_model_service.count_feature_models() == 2
        assert dataset_service.total_dataset_views() == 1
        assert dataset_service.total_dataset_downloads() == 2
        assert feature_model_service.total_feature_model_views() == 3
        assert feature_model_service.total_feature_model_downloads() == 4


def test_latest_synchronized_returns_five_newest_synchronized_datasets(test_app, clean_database):
    with test_app.app_context():
        user = _create_user()
        for index in range(6):
            _create_dataset(user, f"Synced {index}", dataset_doi=f"10.1234/synced-{index}")
        _create_dataset(user, "Draft dataset", dataset_doi=None)

        latest = DataSetService().latest_synchronized()

        assert len(latest) == 5
        titles = [dataset.ds_meta_data.title for dataset in latest]
        # Newest first, and the oldest synchronized one falls off the list.
        assert titles == ["Synced 5", "Synced 4", "Synced 3", "Synced 2", "Synced 1"]
        assert "Draft dataset" not in titles
