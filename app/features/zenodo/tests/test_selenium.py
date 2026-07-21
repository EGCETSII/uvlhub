"""Browser-driven end-to-end tests for zenodo.

Runs against the live app and the selenium grid started by
``docker compose -f docker/docker-compose.dev.yml up``, so it uses the
seeded development database rather than the test database. Run with::

    rosemary test zenodo --e2e

The feature's own route, ``/zenodo``, renders a template whose content
block is empty, so there is nothing on it for a user to see. What is
browsable is the connection check behind ``/zenodo/test``, which the
dataset upload page calls on load, and the Zenodo record link that a
synchronized dataset shows. That is what these tests drive.

Two limits shape what can be asserted here:

* this deployment has no ``ZENODO_ACCESS_TOKEN``, so the sandbox API
  answers 403 and the check reports a failure. The tests assert the
  contract of the answer and only inspect the failure text once the check
  has actually reported a failure, so a configured token would not turn
  them red;
* the warning banner that the upload page is supposed to reveal when the
  check fails never appears, because the script that calls the endpoint is
  served from ``/zenodo/scripts/scripts.js`` and that URL 404s. It is not
  covered here for that reason.

Everything below is read-only: no deposition is ever created through the
browser.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.selenium_support import close_driver, get_host_for_selenium_testing, initialize_driver

pytestmark = pytest.mark.e2e

# Seeded datasets are all synchronized, and deposition ids mirror dataset ids.
SEEDED_RECORDS = {"10.1234/dataset1": "1", "10.1234/dataset2": "2"}

FETCH_CONNECTION_CHECK = """
const done = arguments[arguments.length - 1];
fetch('/zenodo/test')
    .then(response => response.json().then(body => done({status: response.status, body: body})))
    .catch(error => done({status: -1, body: String(error)}));
"""


def _connection_check(driver, host):
    """Ask ``/zenodo/test`` from the app origin, the way the upload page does."""
    driver.get(host)
    driver.set_script_timeout(120)
    return driver.execute_async_script(FETCH_CONNECTION_CHECK)


def _record_url(deposition_id):
    # Development points at the Zenodo sandbox rather than production.
    return f"https://sandbox.zenodo.org/records/{deposition_id}"


def test_connection_check_answers_anonymous_callers_with_a_success_flag():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        result = _connection_check(driver, host)

        # No session is established anywhere in this test.
        assert not driver.find_elements(By.CSS_SELECTOR, 'a[href="/logout"]')
        assert result["status"] == 200

        body = result["body"]
        assert isinstance(body, dict), body
        assert isinstance(body["success"], bool)
        assert "messages" in body
    finally:
        close_driver(driver)


def test_connection_check_failure_names_the_rejected_step_and_response_code():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        body = _connection_check(driver, host)["body"]

        if body["success"]:
            pytest.skip("Zenodo is reachable here, so there is no failure message to inspect")

        assert "Failed to create test deposition on Zenodo" in body["messages"]
        assert "Response code:" in body["messages"]
    finally:
        close_driver(driver)


def test_synchronized_dataset_links_back_to_its_own_zenodo_record():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()

        for doi, deposition_id in SEEDED_RECORDS.items():
            driver.get(f"{host}/doi/{doi}/")

            expected = _record_url(deposition_id)
            link = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'a[href="{expected}"]')),
            )

            assert link.text.strip() == expected
            assert link.get_attribute("target") == "_blank"
            # The page must not advertise a record belonging to another dataset.
            for other_id in set(SEEDED_RECORDS.values()) - {deposition_id}:
                assert not driver.find_elements(By.CSS_SELECTOR, f'a[href="{_record_url(other_id)}"]')
    finally:
        close_driver(driver)


def test_dataset_page_labels_the_zenodo_record_row():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        doi, deposition_id = next(iter(SEEDED_RECORDS.items()))
        driver.get(f"{host}/doi/{doi}/")

        link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'a[href="{_record_url(deposition_id)}"]')),
        )
        row = link.find_element(By.XPATH, "ancestor::div[contains(@class, 'row')][1]")

        assert "Zenodo record" in row.text
    finally:
        close_driver(driver)
