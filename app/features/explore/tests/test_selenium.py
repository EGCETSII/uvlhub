"""Browser-driven end-to-end tests for the explore page.

Runs against the live app and the selenium grid started by
``docker compose -f docker/docker-compose.dev.yml up``, so it uses the
seeded development database rather than the test database. Run with::

    rosemary test explore --e2e

Note on request sequencing. The result list is rendered client side by
``app/features/explore/assets/js/scripts.js``, which fires one POST /explore
per filter event (input or change). The client keeps a single in-flight
request and aborts it (via an AbortController) whenever a new event starts
another one, so only the response to the latest query can repaint the list.
Typing "file7" still issues five requests, but the superseded ones are
cancelled and the page settles on the result of the full query.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from app.features.dataset.models import PublicationType
from tests.selenium_support import close_driver, get_host_for_selenium_testing, initialize_driver

pytestmark = pytest.mark.e2e

# Seeded development data. Every seeded dataset is synchronized, so all of
# them are searchable.
SEEDED_DATASET_TITLES = {
    "Sample dataset 1",
    "Sample dataset 2",
    "Sample dataset 3",
    "Sample dataset 4",
}
SEEDED_DATASET_COUNT = len(SEEDED_DATASET_TITLES)

# "file7.uvl" is the only seeded UVL file whose name contains "file7", and it
# belongs to "Sample dataset 3", so this query matches exactly one dataset.
NARROWING_QUERY = "file7"
NARROWING_QUERY_TITLE = "Sample dataset 3"
UNMATCHED_QUERY = "nonexistentquery"

RESULT_CARDS = (By.CSS_SELECTOR, "#results > div")


def expected_counter_text(count):
    return f"{count} dataset found" if count == 1 else f"{count} datasets found"


def wait_for_results(driver, count):
    """Wait until the page reports ``count`` results and return the cards."""
    WebDriverWait(driver, 20).until(
        EC.text_to_be_present_in_element((By.ID, "results_number"), expected_counter_text(count))
    )
    cards = driver.find_elements(*RESULT_CARDS)
    # Guard against a slower in-flight request repainting the list after the
    # counter matched: the two must agree at assertion time.
    assert driver.find_element(By.ID, "results_number").text == expected_counter_text(count)
    assert len(cards) == count
    return cards


def card_titles(cards):
    return {card.find_element(By.CSS_SELECTOR, "h3 a").text.strip() for card in cards}


def open_explore(driver, host, query=""):
    suffix = f"?query={query}" if query else ""
    driver.get(f"{host}/explore{suffix}")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "query")))


def test_explore_page_offers_the_whole_search_form():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        open_explore(driver, host)

        # Not driver.title: base_template.html hardcodes the <title> and never
        # renders the per-page {% block title %}.
        assert driver.find_element(By.CSS_SELECTOR, "h1").text.strip() == "Explore"

        # The search posts JSON back to /explore, so the token it reads has to
        # be on the page.
        assert driver.find_element(By.ID, "csrf_token").get_attribute("value")

        assert driver.find_element(By.ID, "query").get_attribute("autofocus") is not None
        assert driver.find_element(By.ID, "clear-filters").is_displayed()

        sorting = driver.find_elements(By.CSS_SELECTOR, 'input[name="sorting"]')
        assert [option.get_attribute("value") for option in sorting] == ["newest", "oldest"]
        assert sorting[0].is_selected(), "newest first should be the default sorting"
    finally:
        close_driver(driver)


def test_publication_type_filter_offers_every_publication_type_the_app_knows():
    """The option values feed straight into the repository filter.

    ``ExploreRepository.filter`` matches an option against
    ``PublicationType.value.lower()``. A value the enum does not carry silently
    filters nothing, so the two lists have to stay in step.
    """
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        open_explore(driver, host)

        options = Select(driver.find_element(By.ID, "publication_type")).options
        values = [option.get_attribute("value") for option in options]

        assert values[0] == "any", "the unfiltered option should come first"
        assert set(values[1:]) == {publication_type.value.lower() for publication_type in PublicationType}
    finally:
        close_driver(driver)


def test_explore_lists_every_synchronized_dataset_by_default():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        open_explore(driver, host)

        cards = wait_for_results(driver, SEEDED_DATASET_COUNT)
        assert card_titles(cards) == SEEDED_DATASET_TITLES
    finally:
        close_driver(driver)


def test_typing_a_query_narrows_the_visible_results():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        open_explore(driver, host)
        wait_for_results(driver, SEEDED_DATASET_COUNT)

        driver.find_element(By.ID, "query").send_keys(NARROWING_QUERY)

        cards = wait_for_results(driver, 1)
        assert card_titles(cards) == {NARROWING_QUERY_TITLE}
    finally:
        close_driver(driver)


def test_a_query_without_matches_shows_the_not_found_panel():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        open_explore(driver, host)
        wait_for_results(driver, SEEDED_DATASET_COUNT)

        not_found = driver.find_element(By.ID, "results_not_found")
        assert not not_found.is_displayed()

        driver.find_element(By.ID, "query").send_keys(UNMATCHED_QUERY)

        wait_for_results(driver, 0)
        WebDriverWait(driver, 15).until(EC.visibility_of(not_found))
        assert "We have not found any datasets" in not_found.text
    finally:
        close_driver(driver)


def test_clearing_the_filters_restores_the_full_result_list():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        open_explore(driver, host)
        wait_for_results(driver, SEEDED_DATASET_COUNT)

        query_input = driver.find_element(By.ID, "query")
        query_input.send_keys(NARROWING_QUERY)
        wait_for_results(driver, 1)

        driver.find_element(By.ID, "clear-filters").click()

        cards = wait_for_results(driver, SEEDED_DATASET_COUNT)
        assert card_titles(cards) == SEEDED_DATASET_TITLES
        assert query_input.get_attribute("value") == ""
    finally:
        close_driver(driver)


def test_filtering_by_a_publication_type_nobody_uses_empties_the_result_list():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        open_explore(driver, host)
        wait_for_results(driver, SEEDED_DATASET_COUNT)

        publication_type = Select(driver.find_element(By.ID, "publication_type"))

        # No seeded dataset is a book.
        publication_type.select_by_value("book")
        wait_for_results(driver, 0)

        # Every seeded dataset is a data management plan.
        publication_type.select_by_value("datamanagementplan")
        cards = wait_for_results(driver, SEEDED_DATASET_COUNT)
        assert card_titles(cards) == SEEDED_DATASET_TITLES
    finally:
        close_driver(driver)


def test_a_query_in_the_url_prefills_the_search_box_and_filters_the_results():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        open_explore(driver, host, query=NARROWING_QUERY)

        assert driver.find_element(By.ID, "query").get_attribute("value") == NARROWING_QUERY

        cards = wait_for_results(driver, 1)
        assert card_titles(cards) == {NARROWING_QUERY_TITLE}
    finally:
        close_driver(driver)


def test_a_result_card_links_to_the_dataset_and_to_its_download():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        open_explore(driver, host, query=NARROWING_QUERY)

        card = wait_for_results(driver, 1)[0]

        title_link = card.find_element(By.CSS_SELECTOR, "h3 a")
        assert "/doi/" in title_link.get_attribute("href")

        download_link = card.find_element(By.CSS_SELECTOR, 'a[href^="/dataset/download/"]')
        assert "Download" in download_link.text
    finally:
        close_driver(driver)
