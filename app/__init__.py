import importlib
import os
import pkgutil

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from splent_framework.configuration.configuration import get_app_version
from splent_framework.managers.config_manager import ConfigManager
from splent_framework.managers.error_handler_manager import ErrorHandlerManager
from splent_framework.managers.logging_manager import LoggingManager

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


def _register_features(app: Flask) -> None:
    import app.features as features_pkg

    for _, name, ispkg in pkgutil.iter_modules(features_pkg.__path__):
        if not ispkg:
            continue
        module = importlib.import_module(f"app.features.{name}")
        bp = getattr(module, f"{name}_bp", None)
        if bp is not None:
            app.register_blueprint(bp)


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    ConfigManager(app).load_config(config_name=config_name)

    db.init_app(app)
    migrate.init_app(app, db)

    _register_features(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.features.auth.models import User

        return User.query.get(int(user_id))

    LoggingManager(app).setup_logging()
    ErrorHandlerManager(app).register_error_handlers()

    @app.context_processor
    def inject_vars_into_jinja():
        return {
            "FLASK_APP_NAME": os.getenv("FLASK_APP_NAME"),
            "FLASK_ENV": os.getenv("FLASK_ENV"),
            "DOMAIN": os.getenv("DOMAIN", "localhost"),
            "APP_VERSION": get_app_version(),
        }

    return app


app = create_app()
