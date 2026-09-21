"""``MARIADB_PORT`` reaches the SQLAlchemy URI, and only where it makes sense."""

import pytest
from flask import Flask

from app import _apply_database_port

pytestmark = pytest.mark.unit

MYSQL = "mysql+pymysql://uvlhubdb_user:uvlhubdb_password@db.example:3306/uvlhubdb"


def _app_with(uri):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    return app


def test_port_from_environment_replaces_the_hardcoded_one(monkeypatch):
    monkeypatch.setenv("MARIADB_PORT", "3307")
    app = _app_with(MYSQL)
    _apply_database_port(app)
    assert app.config["SQLALCHEMY_DATABASE_URI"] == MYSQL.replace(":3306/", ":3307/")


def test_password_survives_the_rewrite(monkeypatch):
    monkeypatch.setenv("MARIADB_PORT", "3307")
    app = _app_with("mysql+pymysql://u:p%40ss%25@db.example:3306/uvlhubdb")
    _apply_database_port(app)
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "mysql+pymysql://u:p%40ss%25@db.example:3307/uvlhubdb"


@pytest.mark.parametrize("port", [None, ""])
def test_unset_or_empty_port_leaves_the_uri_alone(monkeypatch, port):
    if port is None:
        monkeypatch.delenv("MARIADB_PORT", raising=False)
    else:
        monkeypatch.setenv("MARIADB_PORT", port)
    app = _app_with(MYSQL)
    _apply_database_port(app)
    assert app.config["SQLALCHEMY_DATABASE_URI"] == MYSQL


def test_sqlite_is_not_a_mariadb(monkeypatch):
    monkeypatch.setenv("MARIADB_PORT", "3307")
    app = _app_with("sqlite:///:memory:")
    _apply_database_port(app)
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_non_numeric_port_is_reported(monkeypatch):
    monkeypatch.setenv("MARIADB_PORT", "three")
    with pytest.raises(RuntimeError, match="MARIADB_PORT"):
        _apply_database_port(_app_with(MYSQL))
