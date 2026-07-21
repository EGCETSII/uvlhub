import os
import subprocess
import sys

import click


@click.command("linter", help="Runs flake8 linter on the 'app' and 'rosemary' directories.")
def linter():

    # Define the directories to be checked with flake8
    working_dir = os.getenv("WORKING_DIR", "")
    directories = [
        os.path.join(working_dir, "app"),
        os.path.join(working_dir, "rosemary"),
    ]

    # No --config: flake8 reads INI with configparser, so pointing it at a TOML
    # file made it die with "Source contains parsing errors: 'pyproject.toml'".
    # flake8-pyproject already discovers [tool.flake8] there on its own.
    failed = False
    for directory in directories:
        click.echo(f"Running flake8 on {directory}...")
        result = subprocess.run(["flake8", directory])

        # Check if flake8 encountered problems
        if result.returncode != 0:
            failed = True
            click.echo(click.style(f"flake8 found issues in {directory}.", fg="red"))
        else:
            click.echo(click.style(f"No issues found in {directory}.", fg="green"))

    # Exit non-zero so the command is usable as a gate in a script or hook.
    if failed:
        sys.exit(1)


@click.command(
    "linter:fix",
    help="Automatically formats and cleans code in 'app' and 'rosemary' directories.",
)
def linter_fix():
    working_dir = os.getenv("WORKING_DIR", "")
    directories = [
        os.path.join(working_dir, "app"),
        os.path.join(working_dir, "rosemary"),
    ]

    for directory in directories:
        click.echo(click.style(f"\nProcessing {directory}...", fg="cyan"))

        # 1. Remove unused imports & variables
        subprocess.run(
            [
                "autoflake",
                "--in-place",
                "--remove-unused-variables",
                "--remove-all-unused-imports",
                "--recursive",
                directory,
            ]
        )

        # 2. Sort imports
        subprocess.run(["isort", directory])

        # 3. Format code with Black
        result = subprocess.run(["black", "--line-length=120", directory])

        if result.returncode != 0:
            click.echo(click.style(f"Failed on {directory}", fg="red"))
        else:
            click.echo(click.style(f"{directory} cleaned and formatted", fg="green"))
