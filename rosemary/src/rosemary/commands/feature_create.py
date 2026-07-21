import os
import stat

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")


def _pascalcase(s: str) -> str:
    return "".join(word.capitalize() for word in s.split("_"))


def _setup_jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(searchpath=_TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml", "j2"]),
    )
    env.filters["pascalcase"] = _pascalcase
    return env


def _render(env: Environment, template_name: str, dest: str, context: dict) -> None:
    content = env.get_template(template_name).render(context) + "\n"
    with open(dest, "w") as f:
        f.write(content)


@click.command("feature:create", help="Creates a new feature with a given name.")
@click.argument("name")
def feature_create(name: str) -> None:
    features_root = os.path.join(os.getenv("WORKING_DIR", ""), "app/features")
    feature_path = os.path.join(features_root, name)

    if os.path.exists(feature_path):
        click.echo(click.style(f"The feature '{name}' already exists.", fg="red"))
        return

    env = _setup_jinja_env()

    files_and_templates = {
        "__init__.py": "feature_init.py.j2",
        "routes.py": "feature_routes.py.j2",
        "models.py": "feature_models.py.j2",
        "repositories.py": "feature_repositories.py.j2",
        "services.py": "feature_services.py.j2",
        "forms.py": "feature_forms.py.j2",
        "seeders.py": "feature_seeders.py.j2",
        os.path.join("templates", name, "index.html"): "feature_templates_index.html.j2",
        "assets/scripts/scripts.js": "feature_scripts.js.j2",
        "tests/test_unit.py": "feature_tests_test_unit.py.j2",
        "tests/test_repository.py": "feature_tests_test_repository.py.j2",
        "tests/test_service.py": "feature_tests_test_service.py.j2",
        "tests/test_integration.py": "feature_tests_test_integration.py.j2",
        "tests/test_selenium.py": "feature_tests_test_selenium.py.j2",
        "tests/locustfile.py": "feature_tests_locustfile.py.j2",
    }

    os.makedirs(os.path.join(feature_path, "templates", name), exist_ok=True)
    os.makedirs(os.path.join(feature_path, "tests"), exist_ok=True)
    os.makedirs(os.path.join(feature_path, "assets", "scripts"), exist_ok=True)

    open(os.path.join(feature_path, "tests", "__init__.py"), "a").close()

    context = {"feature_name": name}
    for filename, template_name in files_and_templates.items():
        _render(env, template_name, os.path.join(feature_path, filename), context)

    click.echo(click.style(f"Feature '{name}' created successfully.", fg="green"))

    # Match host UID/GID so files created from inside the dev container are owned
    # by the developer on the host (typical Docker dev workflow).
    uid, gid = 1000, 1000
    os.chown(feature_path, uid, gid)
    os.chmod(feature_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
    for root, dirs, files in os.walk(feature_path):
        for d in dirs:
            p = os.path.join(root, d)
            os.chown(p, uid, gid)
            os.chmod(p, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
        for f in files:
            p = os.path.join(root, f)
            os.chown(p, uid, gid)
            os.chmod(p, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)

    click.echo(click.style(f"Feature '{name}' permissions changed successfully.", fg="green"))
