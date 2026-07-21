import os
import subprocess

import click


@click.command("selenium", help="Executes Selenium tests based on the environment (local, Docker, or Vagrant).")
@click.argument("feature", required=False)
@click.option(
    "--driver",
    default="firefox",
    type=click.Choice(["firefox", "chrome"], case_sensitive=False),
    help="Specify the Selenium WebDriver to use.",
)
def selenium(feature, driver):
    """Unified Selenium test runner for local, Docker, and Vagrant environments."""
    try:
        working_dir = os.getenv("WORKING_DIR", "")
        features_dir = os.path.join(working_dir, "app/features")

        # tests/selenium_support.initialize_driver reads this. The framework's
        # selenium.common has no set_service_driver to call, despite what
        # earlier versions of this command assumed.
        os.environ["SELENIUM_BROWSER"] = driver.lower()

        def validate_feature(feature_name):
            if not feature_name:
                return
            feature_path = os.path.join(features_dir, feature_name)
            if not os.path.exists(feature_path):
                raise click.UsageError(f"Feature '{feature_name}' does not exist.")
            selenium_test_path = os.path.join(feature_path, "tests", "test_selenium.py")
            if not os.path.exists(selenium_test_path):
                raise click.UsageError(
                    f"Selenium test for feature '{feature_name}' not found at '{selenium_test_path}'."
                )

        def collect_test_paths(feature_name=None):
            if feature_name:
                return [os.path.join(features_dir, feature_name, "tests", "test_selenium.py")]
            paths = []
            for f in os.listdir(features_dir):
                selenium_test = os.path.join(features_dir, f, "tests", "test_selenium.py")
                if os.path.exists(selenium_test):
                    paths.append(selenium_test)
            return paths

        def run_selenium_tests(feature_name, env="local"):
            test_paths = collect_test_paths(feature_name)
            if not test_paths:
                click.echo(click.style("No selenium tests found.", fg="yellow"))
                return
            # Always pytest: the e2e files are marker-tagged test modules, not
            # scripts that call themselves on import the way the pre-refactor
            # ones did, so `python <file>` would silently run nothing.
            cmd = ["pytest", "-v", "-m", "e2e"] + test_paths

            env_label = "Docker (Selenium Grid)" if env == "docker" else "local environment"
            click.echo(click.style(f"Running Selenium tests in {env_label}...", fg="cyan"))
            click.echo(f"  Command: {' '.join(cmd)}")

            try:
                subprocess.run(cmd, check=True)
                click.echo(click.style("Selenium tests completed successfully.", fg="green"))
            except subprocess.CalledProcessError:
                click.echo(click.style("Selenium tests failed.", fg="red"))
                raise

        def run_vagrant_tests(feature_name):
            click.echo(
                click.style(
                    "Currently it is not possible to run Selenium tests from a Vagrant environment.",
                    fg="red",
                )
            )

        if feature:
            validate_feature(feature)

        if working_dir == "/workspace/":
            run_selenium_tests(feature, env="docker")
        elif working_dir == "":
            run_selenium_tests(feature, env="local")
        elif working_dir == "/vagrant/":
            run_vagrant_tests(feature)
        else:
            click.echo(click.style(f"Unrecognized WORKING_DIR: {working_dir}", fg="red"))

    except click.UsageError as e:
        raise e
    except subprocess.CalledProcessError:
        pass
    except Exception as e:
        click.echo(click.style(f"Unexpected error: {e}", fg="red"))
