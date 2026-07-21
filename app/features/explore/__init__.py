from flask import Flask
from splent_framework.assets.asset_registry import register_asset
from splent_framework.blueprints.base_blueprint import BaseBlueprint
from splent_framework.nav.nav_registry import register_nav_item

explore_bp = BaseBlueprint("explore", __name__, template_folder="templates")


def init_feature(app: Flask) -> None:
    """Declare this feature's javascript with the framework asset registry."""
    register_asset("js", "explore.assets", subfolder="js", filename="scripts.js")
    register_nav_item("explore", "Explore", "/explore", order=20, icon="search")
