"""Browser-driven end-to-end tests for the public landing page.

Runs against the live app and the selenium grid started by
``docker compose -f docker/docker-compose.dev.yml up``, so it uses the
seeded development database rather than the test database. Run with::

    rosemary test public --e2e
"""

import re

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.selenium_support import close_driver, get_host_for_selenium_testing, initialize_driver

pytestmark = pytest.mark.e2e

# Seeded development data. The landing page counters are derived from it.
SEEDED_DATASET_TITLES = {
    "Sample dataset 1",
    "Sample dataset 2",
    "Sample dataset 3",
    "Sample dataset 4",
}
SEEDED_DATASET_COUNT = 4
SEEDED_FEATURE_MODEL_COUNT = 12
LATEST_DATASETS_SHOWN = 5

# The statistics card carries no id, so anchor on its heading instead of on a
# deep CSS path.
STATS_CARD = (
    By.XPATH,
    "//h2[b[normalize-space()='Hub statistics']]/ancestor::div[contains(@class, 'card-body')][1]",
)
# One anchor per dataset card in the latest datasets column.
DATASET_CARD_LINKS = (By.XPATH, "//h2/a[contains(@href, '/doi/')]")


def log_in(driver, host):
    driver.get(f"{host}/login")
    driver.find_element(By.NAME, "email").send_keys("user1@example.com")
    driver.find_element(By.NAME, "password").send_keys("1234")
    driver.find_element(By.ID, "submit").click()
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/logout"]')))


def scroll_into_view(driver, element):
    """Bring ``element`` into the viewport.

    The theme sets ``scroll-behavior: smooth`` on ``html``, so the default
    ``scrollIntoView`` animates and the element is still off screen when the
    click is attempted. Scroll instantly instead.
    """
    driver.execute_script(
        "const rect = arguments[0].getBoundingClientRect();"
        "window.scrollBy({top: rect.top - window.innerHeight / 2, behavior: 'instant'});",
        element,
    )


def read_statistic(driver, label):
    """Return the integer the statistics card reports for ``label``."""
    card = WebDriverWait(driver, 15).until(EC.presence_of_element_located(STATS_CARD))
    pattern = re.compile(rf"(\d+)\s+{re.escape(label)}\s*$")
    for line in card.text.splitlines():
        match = pattern.search(line.replace("\xa0", " ").strip())
        if match:
            return int(match.group(1))
    raise AssertionError(f"No '{label}' statistic on the landing page. Card text was:\n{card.text}")


def test_landing_page_reports_the_seeded_dataset_and_feature_model_counts():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/")

        assert read_statistic(driver, "datasets") == SEEDED_DATASET_COUNT
        assert read_statistic(driver, "feature models") == SEEDED_FEATURE_MODEL_COUNT
    finally:
        close_driver(driver)


def test_landing_page_reports_every_view_and_download_statistic():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/")

        # These grow as the hub is used, so assert they are reported at all
        # rather than pinning a value a concurrent visit would invalidate.
        for label in (
            "datasets viewed",
            "feature models viewed",
            "datasets downloaded",
            "feature models downloaded",
        ):
            assert read_statistic(driver, label) >= 0
    finally:
        close_driver(driver)


def test_landing_page_lists_the_latest_datasets_with_links_to_their_doi():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located(DATASET_CARD_LINKS))
        links = driver.find_elements(*DATASET_CARD_LINKS)

        # The landing page shows the newest datasets, capped at five.
        expected_cards = min(read_statistic(driver, "datasets"), LATEST_DATASETS_SHOWN)
        assert len(links) == expected_cards

        titles = {link.text.strip() for link in links}
        assert titles == SEEDED_DATASET_TITLES

        for link in links:
            assert re.search(r"/doi/10\.\d+/\S+$", link.get_attribute("href"))
    finally:
        close_driver(driver)


def test_landing_page_invites_anonymous_visitors_to_sign_up():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/")

        welcome = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card-welcome")))
        assert "Let's get started!" in welcome.text
        assert welcome.find_elements(By.CSS_SELECTOR, 'a[href="/signup"]')
        assert welcome.find_elements(By.CSS_SELECTOR, 'a[href="/login"]')
        assert not driver.find_elements(By.CSS_SELECTOR, 'a[href="/logout"]')
    finally:
        close_driver(driver)


def test_landing_page_drops_the_welcome_card_once_the_visitor_is_logged_in():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        log_in(driver, host)
        driver.get(f"{host}/")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located(STATS_CARD))
        assert driver.find_elements(By.CSS_SELECTOR, 'a[href="/logout"]')
        assert not driver.find_elements(By.CSS_SELECTOR, "div.card-welcome")
    finally:
        close_driver(driver)


def test_explore_more_datasets_button_opens_the_explore_page():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/")

        # The sidebar links to /explore too, so target the content button.
        button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.btn[href="/explore"]'))
        )
        assert "Explore more datasets" in button.text

        # The button sits below the fold once the dataset cards are rendered.
        scroll_into_view(driver, button)
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable(button)).click()

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "query")))
        assert driver.current_url.endswith("/explore")
    finally:
        close_driver(driver)
