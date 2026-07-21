from flask import Flask
from flask_login import LoginManager
from splent_framework.assets.asset_registry import register_asset
from splent_framework.blueprints.base_blueprint import BaseBlueprint

auth_bp = BaseBlueprint("auth", __name__, template_folder="templates")


def init_feature(app: Flask) -> None:
    """Configure Flask-Login when the auth feature is registered.

    Lives here (not in app/__init__.py) so the central app factory stays
    feature-agnostic — login is an auth concern, not a product concern.
    """
    register_asset("js", "auth.assets", subfolder="js", filename="scripts.js")

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.features.auth.models import User

        return User.query.get(int(user_id))
