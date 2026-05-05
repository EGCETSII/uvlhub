import logging

from flask import render_template

from app.features.dataset.services import DataSetService
from app.features.featuremodel.services import FeatureModelService
from app.features.public import public_bp

logger = logging.getLogger(__name__)

dataset_service = DataSetService()
feature_model_service = FeatureModelService()


@public_bp.route("/")
def index():
    logger.info("Access index")
    return render_template(
        "public/index.html",
        datasets=dataset_service.latest_synchronized(),
        datasets_counter=dataset_service.count_synchronized_datasets(),
        feature_models_counter=feature_model_service.count_feature_models(),
        total_dataset_downloads=dataset_service.total_dataset_downloads(),
        total_feature_model_downloads=feature_model_service.total_feature_model_downloads(),
        total_dataset_views=dataset_service.total_dataset_views(),
        total_feature_model_views=feature_model_service.total_feature_model_views(),
    )
