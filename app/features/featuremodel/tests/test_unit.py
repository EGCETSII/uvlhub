"""Unit tests for the featuremodel feature — pure logic, no Flask app, no DB."""

import pytest

from app.features.dataset.models import PublicationType
from app.features.featuremodel.models import FeatureModel, FMMetaData, FMMetrics

pytestmark = pytest.mark.unit


def test_feature_model_repr_uses_its_id():
    feature_model = FeatureModel(id=7, data_set_id=1)
    assert repr(feature_model) == "FeatureModel<7>"


def test_fm_meta_data_repr_uses_its_title():
    meta_data = FMMetaData(
        uvl_filename="smart_home.uvl",
        title="Smart Home",
        description="A smart home feature model",
        publication_type=PublicationType.JOURNAL_ARTICLE,
    )
    # NOTE: the model's __repr__ never closes the angle bracket; pinned as-is.
    assert repr(meta_data) == "FMMetaData<Smart Home"


def test_fm_metrics_repr_reports_both_solver_counts():
    metrics = FMMetrics(solver="12", not_solver="3")
    assert repr(metrics) == "FMMetrics<solver=12, not_solver=3>"


def test_fm_meta_data_keeps_the_publication_type_enum_member():
    meta_data = FMMetaData(
        uvl_filename="car.uvl",
        title="Car",
        description="A car feature model",
        publication_type=PublicationType.BOOK,
    )
    assert meta_data.publication_type is PublicationType.BOOK
    assert meta_data.publication_type.value == "book"
