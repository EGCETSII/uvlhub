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
from sqlalchemy.engine import make_url

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
    _apply_database_port(app)
    db.init_app(app)
    migrate.init_app(app, db)

    env = "prod" if config_name == "production" else "dev"
    register_features(app, env=env)
    LoggingManager(app).setup_logging()
    ErrorHandlerManager(app).register_error_handlers()
    _setup_jinja_globals(app)

    return app


def _apply_database_port(app: Flask) -> None:
    """Honour ``MARIADB_PORT`` in the SQLAlchemy URI.

    splent_framework's default configuration builds ``SQLALCHEMY_DATABASE_URI``
    from the ``MARIADB_*`` variables but hardcodes port 3306. A database that
    listens elsewhere, such as the one filess.io provides for the Render
    deployment, is then reachable by ``scripts/wait-for-db.sh`` and the
    entrypoints, which pass ``-P $MARIADB_PORT``, and unreachable by the
    application, which fails at ``flask db upgrade`` with ``Can't connect to
    MySQL server on '<host>' ([Errno 111] Connection refused)``. Rewrite the
    port here so every command reads the same variable. Only a MySQL/MariaDB
    URI with a host is touched: the variable means nothing to SQLite.
    """
    port = os.getenv("MARIADB_PORT")
    uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not port or not uri:
        return
    url = make_url(uri)
    if not url.host or not url.drivername.startswith("mysql"):
        return
    try:
        port_number = int(port)
    except ValueError as exc:
        raise RuntimeError(f"MARIADB_PORT must be an integer, got {port!r}") from exc
    app.config["SQLALCHEMY_DATABASE_URI"] = url.set(port=port_number).render_as_string(hide_password=False)


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
