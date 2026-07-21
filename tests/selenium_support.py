"""Driver and host resolution for the e2e layer.

Since splent_framework 1.7.1 the framework itself can drive a Selenium Grid:
``initialize_driver`` attaches to ``SELENIUM_GRID_URL`` over
``webdriver.Remote``, and ``get_host_for_selenium_testing`` honours
``SELENIUM_TARGET_URL``. This module is now a thin product-level wrapper that
supplies uvlhub's defaults and its deterministic viewport, so the ten e2e
files keep a single import point.

What it adds on top of the framework helpers:

* Defaults for the grid and target URLs matching the container names that
  ``docker/docker-compose.dev.yml`` fixes, applied only under Docker and only
  when the variables are not already set.
* A pinned 1920x1080 window. Chrome nodes open at about 945px and firefox at
  about 1280px, and below the responsive breakpoint the sidebar collapses
  off-canvas, so an unpinned viewport makes the same test pass on one browser
  and fail on the other.
"""

import os

from splent_framework.environment.host import get_host_for_selenium_testing
from splent_framework.selenium.common import close_driver
from splent_framework.selenium.common import initialize_driver as _framework_driver

__all__ = ["close_driver", "get_host_for_selenium_testing", "initialize_driver"]

# Explicit container_name entries in the compose file, so these hold whatever
# project name the stack is brought up under. Only defaulted in Docker: a
# local run without a grid should keep launching a local browser.
if os.getenv("WORKING_DIR", "") == "/workspace/":
    os.environ.setdefault("SELENIUM_GRID_URL", "http://selenium_hub_container:4444")
    os.environ.setdefault("SELENIUM_TARGET_URL", "http://nginx_web_server_container")


def initialize_driver(browser: str | None = None):
    driver = _framework_driver(browser)
    driver.set_window_size(1920, 1080)
    return driver
