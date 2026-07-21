import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from splent_framework.configuration.configuration import get_app_version
from splent_framework.db import db
from splent_framework.managers.config_manager import ConfigManager
from splent_framework.managers.error_handler_manager import ErrorHandlerManager
from splent_framework.managers.jinja_manager import JinjaManager
from splent_framework.managers.logging_manager import LoggingManager
from splent_framework.nav.nav_registry import get_nav_items

from app.feature_loader import register_features

load_dotenv()

# Re-export the framework's SQLAlchemy singleton so feature modules can keep
# doing ``from app import db`` and end up bound to the same instance that
# splent_framework's BaseSeeder / BaseRepository operate on. Two separate
# SQLAlchemy() objects would break ``init_app`` registration in ways that
# only show up at first query time ("app not registered with this instance").
__all__ = ["db", "create_app"]

migrate = Migrate()


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    ConfigManager(app).load_config(config_name=config_name)
    db.init_app(app)
    migrate.init_app(app, db)

    env = "prod" if config_name == "production" else "dev"
    register_features(app, env=env)
    LoggingManager(app).setup_logging()
    ErrorHandlerManager(app).register_error_handlers()
    _setup_jinja_globals(app)

    return app


def _setup_jinja_globals(app: Flask) -> None:
    """Wire the framework's Jinja layer, plus the product-level context.

    JinjaManager installs ``get_assets`` and ``get_template_hooks`` as globals
    and runs the base context through ``build_jinja_context``, so any feature
    that appends a context processor gets merged in for free.

    ``get_nav_items`` is registered here rather than by the framework: the
    nav registry is written for a theme to consume, and this application is
    its own theme.
    """
    JinjaManager(
        app,
        context={
            "FLASK_APP_NAME": os.getenv("FLASK_APP_NAME"),
            "FLASK_ENV": os.getenv("FLASK_ENV"),
            "DOMAIN": os.getenv("DOMAIN", "localhost"),
            "APP_VERSION": get_app_version(),
        },
    )
    app.jinja_env.globals["get_nav_items"] = get_nav_items


app = create_app(os.getenv("FLASK_ENV", "development"))
