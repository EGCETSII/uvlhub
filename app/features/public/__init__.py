from flask import Flask
from splent_framework.assets.asset_registry import register_asset
from splent_framework.blueprints.base_blueprint import BaseBlueprint
from splent_framework.nav.nav_registry import register_nav_item

public_bp = BaseBlueprint("public", __name__, template_folder="templates")


def init_feature(app: Flask) -> None:
    """Declare this feature's javascript with the framework asset registry."""
    register_asset("js", "public.assets", subfolder="js", filename="scripts.js")
    register_nav_item("home", "Home", "/", order=10, icon="home")
