"""Service-level tests for featuremodel — services + repos with a real DB."""

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet, DSMetaData, PublicationType
from app.features.featuremodel.models import FeatureModel, FMMetaData
from app.features.featuremodel.services import FeatureModelService, FMMetaDataService
from app.features.hubfile.models import Hubfile, HubfileDownloadRecord, HubfileViewRecord

pytestmark = pytest.mark.service


def _make_feature_model(title="Smart Home"):
    user = User(email=f"{title.lower().replace(' ', '_')}@example.com")
    user.set_password("ownerpass")
    ds_meta_data = DSMetaData(
        title=f"{title} dataset",
        description="Host dataset",
        publication_type=PublicationType.JOURNAL_ARTICLE,
        dataset_doi="10.1234/host",
    )
    db.session.add_all([user, ds_meta_data])
    db.session.flush()
    dataset = DataSet(user_id=user.id, ds_meta_data_id=ds_meta_data.id)
    fm_meta_data = FMMetaData(
        uvl_filename=f"{title.lower().replace(' ', '_')}.uvl",
        title=title,
        description=f"{title} description",
        publication_type=PublicationType.JOURNAL_ARTICLE,
    )
    db.session.add_all([dataset, fm_meta_data])
    db.session.flush()
    feature_model = FeatureModel(data_set_id=dataset.id, fm_meta_data_id=fm_meta_data.id)
    db.session.add(feature_model)
    db.session.commit()
    return feature_model


def _make_hubfile(feature_model):
    hubfile = Hubfile(name="model.uvl", checksum="abc123", size=42, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()
    return hubfile


def test_counts_and_totals_are_zero_on_an_empty_database(test_app, clean_database):
    with test_app.app_context():
        service = FeatureModelService()
        assert service.count_feature_models() == 0
        assert service.total_feature_model_views() == 0
        assert service.total_feature_model_downloads() == 0


def test_count_feature_models_reflects_the_repository(test_app, clean_database):
    with test_app.app_context():
        _make_feature_model("Smart Home")
        _make_feature_model("Car Configurator")
        assert FeatureModelService().count_feature_models() == 2


def test_fm_meta_data_service_is_importable_at_module_level(test_app, clean_database):
    with test_app.app_context():
        service = FMMetaDataService()
        assert service.count() == 0
        _make_feature_model("Smart Home")
        assert service.count() == 1


def test_total_views_aggregates_hubfile_view_records(test_app, clean_database):
    with test_app.app_context():
        hubfile = _make_hubfile(_make_feature_model())
        db.session.add_all(
            [
                HubfileViewRecord(file_id=hubfile.id, view_cookie="cookie-1"),
                HubfileViewRecord(file_id=hubfile.id, view_cookie="cookie-2"),
            ]
        )
        db.session.commit()

        service = FeatureModelService()
        assert service.total_feature_model_views() == 2
        # Downloads are counted independently of views.
        assert service.total_feature_model_downloads() == 0


def test_total_downloads_aggregates_hubfile_download_records(test_app, clean_database):
    with test_app.app_context():
        hubfile = _make_hubfile(_make_feature_model())
        db.session.add(HubfileDownloadRecord(file_id=hubfile.id, download_cookie="cookie-1"))
        db.session.commit()

        service = FeatureModelService()
        assert service.total_feature_model_downloads() == 1
        assert service.total_feature_model_views() == 0
