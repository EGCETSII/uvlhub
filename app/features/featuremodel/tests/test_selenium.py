"""Browser-driven end-to-end tests for featuremodel.

Runs against the live app and the selenium grid started by
``docker compose -f docker/docker-compose.dev.yml up``, so it uses the
seeded development database rather than the test database. Run with::

    rosemary test featuremodel --e2e

The feature's own route, ``/featuremodel``, renders a template whose
content block is empty, so there is nothing on it for a user to see. The
place where feature models are actually browsable is the dataset page,
which lists the UVL models of a dataset and lets the user read and export
each one. That is what these tests drive. Everything here is read-only.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.selenium_support import close_driver, get_host_for_selenium_testing, initialize_driver

pytestmark = pytest.mark.e2e

# Seeded datasets: every one owns three feature models, one UVL file each.
DATASET_ONE_DOI = "10.1234/dataset1"
DATASET_TWO_DOI = "10.1234/dataset2"
DATASET_ONE_FILES = ["file1.uvl", "file2.uvl", "file3.uvl"]
DATASET_TWO_FILES = ["file4.uvl", "file5.uvl", "file6.uvl"]


def _open_dataset(driver, host, doi):
    driver.get(f"{host}/doi/{doi}/")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="/file/download/"]')),
    )


def _listed_file_names(driver):
    """Names of the UVL models rendered in the sidebar list of the dataset."""
    return [
        link.find_element(By.XPATH, "ancestor::div[contains(@class, 'list-group-item')][1]")
        .find_element(By.CSS_SELECTOR, "div.col-8")
        .text.splitlines()[0]
        .strip()
        for link in driver.find_elements(By.CSS_SELECTOR, 'a[href^="/file/download/"]')
    ]


def test_dataset_page_lists_every_feature_model_of_the_dataset():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        _open_dataset(driver, host, DATASET_ONE_DOI)

        assert driver.find_element(By.CSS_SELECTOR, "span.badge.bg-dark").text.strip() == str(len(DATASET_ONE_FILES))
        assert sorted(_listed_file_names(driver)) == sorted(DATASET_ONE_FILES)
    finally:
        close_driver(driver)


def test_feature_models_are_scoped_to_their_own_dataset():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        _open_dataset(driver, host, DATASET_TWO_DOI)

        names = _listed_file_names(driver)
        assert sorted(names) == sorted(DATASET_TWO_FILES)
        assert not set(names) & set(DATASET_ONE_FILES)
    finally:
        close_driver(driver)


def test_every_feature_model_offers_uvl_and_converted_exports():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        _open_dataset(driver, host, DATASET_ONE_DOI)

        file_ids = [
            link.get_attribute("href").rstrip("/").rsplit("/", 1)[-1]
            for link in driver.find_elements(By.CSS_SELECTOR, 'a[href^="/file/download/"]')
        ]
        assert len(file_ids) == len(DATASET_ONE_FILES)

        for file_id in file_ids:
            for prefix in ("/flamapy/to_glencoe/", "/flamapy/to_cnf/", "/flamapy/to_splot/"):
                assert driver.find_elements(By.CSS_SELECTOR, f'a[href="{prefix}{file_id}"]')
    finally:
        close_driver(driver)


def test_feature_model_source_can_be_read_from_the_dataset_page():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        _open_dataset(driver, host, DATASET_ONE_DOI)

        first_link = driver.find_element(By.CSS_SELECTOR, 'a[href^="/file/download/"]')
        file_id = first_link.get_attribute("href").rstrip("/").rsplit("/", 1)[-1]

        # The viewer button carries no id, so match on the handler it invokes.
        driver.find_element(By.CSS_SELECTOR, f"button[onclick=\"viewFile('{file_id}')\"]").click()

        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "fileViewerModal")))
        content = (
            WebDriverWait(driver, 15)
            .until(
                EC.visibility_of_element_located((By.ID, "fileContent")),
            )
            .text
        )

        assert driver.find_element(By.ID, "fileViewerModalLabel").text.strip() == "Feature model view"
        # A UVL model always opens with a features block and may add constraints.
        assert content.startswith("features")
        assert "mandatory" in content
    finally:
        close_driver(driver)
