"""Top-level pytest config for uvlhub.

- Sets ``SPLENT_APP=app`` so splent_framework's ``app_loader`` can resolve
  ``create_app("testing")`` without relying on the user's shell environment.
  Done before the fixtures import so the loader sees it on first call.
- Re-exports the test fixtures shipped by splent_framework so every collected
  test in the project picks them up. Per-feature fixtures belong in
  ``app/features/<feature>/tests/conftest.py``.
"""
import os

os.environ.setdefault("SPLENT_APP", "app")

from splent_framework.fixtures.fixtures import (  # noqa: E402, F401
    clean_database,
    test_app,
    test_client,
    test_client_module,
)
