"""Driver and host resolution for the e2e layer.

This exists because ``splent_framework.selenium.common`` cannot drive the
Selenium Grid that ``docker/docker-compose.dev.yml`` starts. Its
``initialize_driver`` builds a *local* Chrome through ``webdriver_manager``,
and there is no browser installed inside ``web_app_container``, so every e2e
test raises before it reaches the app. The framework also exports no
``set_service_driver``, though ``rosemary selenium`` calls it.

Until splent_framework grows grid support, uvlhub resolves its own driver
here. Drop this module and go back to the framework helpers once it does.

Two things differ from the framework version:

* the driver is a ``webdriver.Remote`` pointed at the grid, so the browser
  runs in the selenium-chrome / selenium-firefox container;
* the host is the nginx container, not ``localhost``. ``localhost`` is
  resolved *by the browser*, and inside the browser container that is the
  browser itself. ``get_host_for_locust_testing`` already gets this right;
  ``get_host_for_selenium_testing`` does not.
"""

import os

from selenium import webdriver

# Explicit container_name entries in the compose file, so these hold whatever
# project name the stack is brought up under.
GRID_URL = os.getenv("SELENIUM_GRID_URL", "http://selenium_hub_container:4444")
DOCKER_HOST_URL = os.getenv("SELENIUM_TARGET_URL", "http://nginx_web_server_container")
LOCAL_HOST_URL = "http://localhost:5000"


def get_host_for_selenium_testing() -> str:
    """URL of the app *as the browser sees it*."""
    return DOCKER_HOST_URL if os.getenv("WORKING_DIR", "") == "/workspace/" else LOCAL_HOST_URL


def _options_for(browser: str):
    if browser == "firefox":
        return webdriver.FirefoxOptions()
    return webdriver.ChromeOptions()


def initialize_driver(browser: str | None = None):
    """Return a driver attached to the grid, or a local one outside Docker.

    ``browser`` defaults to $SELENIUM_BROWSER, which ``rosemary selenium``
    sets from its ``--driver`` flag.
    """
    browser = (browser or os.getenv("SELENIUM_BROWSER") or "chrome").lower()

    if os.getenv("WORKING_DIR", "") == "/workspace/":
        driver = webdriver.Remote(command_executor=GRID_URL, options=_options_for(browser))
    elif browser == "firefox":
        driver = webdriver.Firefox()
    else:
        driver = webdriver.Chrome()

    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    return driver


def close_driver(driver):
    if driver is not None:
        driver.quit()
