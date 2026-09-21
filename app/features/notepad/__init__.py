from flask import Flask
from splent_framework.assets.asset_registry import register_asset
from splent_framework.blueprints.base_blueprint import BaseBlueprint

notepad_bp = BaseBlueprint("notepad", __name__, template_folder="templates")


def init_feature(app: Flask) -> None:
    """Declare this feature's javascript with the framework asset registry.

    The shell renders every declared asset from one place, so do not add a
    <script> tag to this feature's template. One consequence: the script is
    then served on every page, so guard any DOM wiring with a check for an
    element that only exists on this feature's page.

    To add an entry to the main navigation, also call:

        from splent_framework.nav.nav_registry import register_nav_item
        register_nav_item("notepad", "notepad", "/notepad", order=100, icon="box")
    """
    register_asset("js", "notepad.assets", subfolder="js", filename="scripts.js")
