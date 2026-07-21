"""Browser-driven end-to-end tests for auth.

Runs against the live app and the selenium grid started by
``docker compose -f docker/docker-compose.dev.yml up``, so it uses the
seeded development database rather than the test database. Run with::

    rosemary test auth --e2e
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.selenium_support import close_driver, get_host_for_selenium_testing, initialize_driver

pytestmark = pytest.mark.e2e


def test_login_with_seeded_user_reaches_the_dashboard():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/login")

        driver.find_element(By.NAME, "email").send_keys("user1@example.com")
        driver.find_element(By.NAME, "password").send_keys("1234")
        driver.find_element(By.ID, "submit").click()

        # The logout control is an icon link, so match on its href rather than
        # on link text.
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/logout"]')))
        assert driver.current_url.rstrip("/") == host.rstrip("/")
    finally:
        close_driver(driver)


def test_login_with_wrong_password_keeps_the_user_on_the_form():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/login")

        driver.find_element(By.NAME, "email").send_keys("user1@example.com")
        driver.find_element(By.NAME, "password").send_keys("definitely-not-the-password")
        driver.find_element(By.ID, "submit").click()

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "password")))
        assert "/login" in driver.current_url
        assert not driver.find_elements(By.CSS_SELECTOR, 'a[href="/logout"]')
    finally:
        close_driver(driver)
