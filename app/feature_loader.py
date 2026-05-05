"""Feature discovery and registration for uvlhub.

Replicates the useful contract of splent_framework's FeatureIntegrator without
the SPL machinery (no UVL constraint solving, refinement registry, namespaces).

For each package under ``app.features``:
  1. ``app.features.<name>.config.inject_config(app)`` — optional, runs first so
     features can mutate ``app.config`` before anything else touches it.
  2. Conventional submodules (routes / models / hooks / signals) are imported
     so that Blueprint definitions inside them become discoverable.
  3. ``app.features.<name>.init_feature(app)`` — optional hook for the feature
     to run setup work that needs the app instance (extension init, etc.).
  4. Every Flask ``Blueprint`` instance found in the feature root or any of
     its submodules is registered. Names are deduplicated.
"""
import importlib
import pkgutil
import sys

from flask import Blueprint, Flask

_SUBMODULES = ("routes", "models", "hooks", "signals")


def register_features(app: Flask) -> None:
    import app.features as features_pkg

    for _, name, ispkg in pkgutil.iter_modules(features_pkg.__path__):
        if not ispkg:
            continue
        _inject_config(name, app)
        feature_module = importlib.import_module(f"app.features.{name}")
        _import_submodules(name)
        _call_init(feature_module, app)
        _register_blueprints(name, feature_module, app)


def _inject_config(name: str, app: Flask) -> None:
    try:
        config_mod = importlib.import_module(f"app.features.{name}.config")
    except ModuleNotFoundError:
        return
    fn = getattr(config_mod, "inject_config", None)
    if callable(fn):
        fn(app)


def _import_submodules(name: str) -> None:
    for sub in _SUBMODULES:
        try:
            importlib.import_module(f"app.features.{name}.{sub}")
        except ModuleNotFoundError:
            pass


def _call_init(feature_module, app: Flask) -> None:
    fn = getattr(feature_module, "init_feature", None)
    if callable(fn):
        fn(app)


def _register_blueprints(name: str, feature_module, app: Flask) -> None:
    candidates = [feature_module]
    for sub in _SUBMODULES:
        mod = sys.modules.get(f"app.features.{name}.{sub}")
        if mod is not None:
            candidates.append(mod)

    seen = set()
    for mod in candidates:
        for attr in dir(mod):
            obj = getattr(mod, attr, None)
            if isinstance(obj, Blueprint) and obj.name not in seen:
                app.register_blueprint(obj)
                seen.add(obj.name)
