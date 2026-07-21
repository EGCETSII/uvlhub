from flask import Flask
from splent_framework.assets.asset_registry import register_asset
from splent_framework.blueprints.base_blueprint import BaseBlueprint

hubfile_bp = BaseBlueprint("hubfile", __name__, template_folder="templates")


def init_feature(app: Flask) -> None:
    """Declare this feature's javascript with the framework asset registry."""
    register_asset("js", "hubfile.assets", subfolder="js", filename="scripts.js")
