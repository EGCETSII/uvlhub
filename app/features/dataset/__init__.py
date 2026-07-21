from flask import Flask
from flask_restful import Api
from splent_framework.assets.asset_registry import register_asset
from splent_framework.blueprints.base_blueprint import BaseBlueprint

from app.features.dataset.api import init_blueprint_api

dataset_bp = BaseBlueprint("dataset", __name__, template_folder="templates")


api = Api(dataset_bp)
init_blueprint_api(api)


def init_feature(app: Flask) -> None:
    """Declare this feature's javascript with the framework asset registry."""
    register_asset("js", "dataset.assets", subfolder="js", filename="scripts.js")
