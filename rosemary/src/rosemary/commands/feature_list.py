"""``rosemary feature:list`` — show the features this product loads.

Resolution goes through ``app.feature_loader``, the same code path the
application itself uses at startup, so the listing cannot drift from reality.

It deliberately does not use splent_framework's ``FeatureManager``. That reads
``<WORKING_DIR>/<SPLENT_APP>/pyproject.toml``, which assumes the SPL workspace
layout where every product is a directory carrying its own pyproject. uvlhub
keeps a single pyproject at the repository root, so the manager looked for
``app/pyproject.toml`` and raised ``FeatureError`` whatever SPLENT_APP was set
to.
"""

import os

import click

from app.feature_loader import declared_features

FEATURES_PACKAGE = "app/features"


@click.command("feature:list", help="Lists the features this product loads.")
@click.option(
    "--env",
    default=lambda: os.getenv("SPLENT_ENV", "dev"),
    help="Environment whose feature list to resolve (dev or prod).",
)
def feature_list(env):
    declared = declared_features(env)
    on_disk = _features_on_disk()

    if not declared:
        # An empty declaration means "load whatever is on disk", which is the
        # documented fallback in app/feature_loader.py.
        click.echo(click.style(f"No feature list declared, loading all {len(on_disk)} found on disk:", fg="yellow"))
        for name in sorted(on_disk):
            click.echo(f"- {name}")
        return

    loaded = sorted(declared & on_disk)
    click.echo(click.style(f"Features loaded in '{env}' ({len(loaded)}):", fg="green"))
    for name in loaded:
        click.echo(f"- {name}")

    _report(declared - on_disk, "declared but missing from app/features", "red")
    _report(on_disk - declared, "present on disk but not declared, so not loaded", "yellow")


def _features_on_disk():
    features_dir = os.path.join(os.getenv("WORKING_DIR", ""), FEATURES_PACKAGE)
    if not os.path.isdir(features_dir):
        return set()
    return {
        entry
        for entry in os.listdir(features_dir)
        if not entry.startswith("__") and os.path.isdir(os.path.join(features_dir, entry))
    }


def _report(names, description, colour):
    if not names:
        return
    click.echo(click.style(f"\n{len(names)} {description}:", fg=colour))
    for name in sorted(names):
        click.echo(f"- {name}")
