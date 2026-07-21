"""Browser-driven end-to-end tests for team.

Runs against the live app and the selenium grid started by
``docker compose -f docker/docker-compose.dev.yml up``, so it uses the
seeded development database rather than the test database. Run with::

    rosemary test team --e2e

The page is static, so these tests are read-only and safe to repeat.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.selenium_support import close_driver, get_host_for_selenium_testing, initialize_driver

pytestmark = pytest.mark.e2e

EXPECTED_PARTNERS = {
    "University of Seville, Spain": "http://www.us.es",
    "University of Malaga, Spain": "http://www.uma.es",
    "University of Ulm, Germany": "http://www.uni-ulm.de",
}


def test_team_page_shows_one_card_per_partner_university():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/team")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card")))

        assert driver.find_element(By.TAG_NAME, "h1").text.strip() == "Team"

        titles = [element.text.strip() for element in driver.find_elements(By.CSS_SELECTOR, "div.card h5.card-title")]
        assert titles == list(EXPECTED_PARTNERS)
    finally:
        close_driver(driver)


def test_each_partner_card_links_to_its_own_institution():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/team")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card")))

        for card in driver.find_elements(By.CSS_SELECTOR, "div.card"):
            title = card.find_element(By.CSS_SELECTOR, "h5.card-title").text.strip()
            link = card.find_element(By.CSS_SELECTOR, ".card-footer a")

            assert link.get_attribute("href").rstrip("/") == EXPECTED_PARTNERS[title]
            assert link.get_attribute("target") == "_blank"
            assert card.find_element(By.CSS_SELECTOR, "p.card-text").text.strip()
    finally:
        close_driver(driver)


def test_team_page_is_reachable_from_the_sidebar():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(host)

        # Match on the href: the sidebar entry is an icon plus a label span.
        driver.find_element(By.CSS_SELECTOR, '#sidebar a[href="/team"]').click()

        WebDriverWait(driver, 15).until(EC.url_contains("/team"))
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card h5.card-title")))

        assert driver.find_element(By.TAG_NAME, "h1").text.strip() == "Team"
        # The sidebar marks the current section as active.
        active = driver.find_element(By.CSS_SELECTOR, "#sidebar li.sidebar-item.active a")
        assert active.get_attribute("href").endswith("/team")
    finally:
        close_driver(driver)


def test_team_page_is_public_and_needs_no_session():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/team")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card h5.card-title")))

        assert "/login" not in driver.current_url
        # Anonymous visitors get the login entry, never the logout one.
        assert driver.find_elements(By.CSS_SELECTOR, 'a[href="/login"]')
        assert not driver.find_elements(By.CSS_SELECTOR, 'a[href="/logout"]')
        assert len(driver.find_elements(By.CSS_SELECTOR, "div.card h5.card-title")) == len(EXPECTED_PARTNERS)
    finally:
        close_driver(driver)
