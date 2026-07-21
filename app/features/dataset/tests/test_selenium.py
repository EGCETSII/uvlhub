"""Browser-driven end-to-end tests for datasets.

Runs against the live app and the selenium grid started by
``docker compose -f docker/docker-compose.dev.yml up``, so it uses the
seeded development database rather than the test database. Run with::

    rosemary test dataset --e2e

The tests only read: they log in as the seeded users, browse their dataset
lists and open dataset pages by DOI. Nothing is uploaded or deleted, because
the development database is shared and never reset between runs.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from tests.selenium_support import close_driver, get_host_for_selenium_testing, initialize_driver

pytestmark = pytest.mark.e2e

PASSWORD = "1234"

# Seeded development data: each user owns two synchronized datasets.
DATASETS_BY_OWNER = {
    "user1@example.com": {"Sample dataset 1", "Sample dataset 3"},
    "user2@example.com": {"Sample dataset 2", "Sample dataset 4"},
}
ALL_SEEDED_TITLES = set().union(*DATASETS_BY_OWNER.values())

# "Sample dataset 1" and the three UVL files seeded under it.
SAMPLE_DOI = "10.1234/dataset1"
SAMPLE_TITLE = "Sample dataset 1"
SAMPLE_DESCRIPTION = "Description for dataset 1"
SAMPLE_AUTHOR = "Author 1"
SAMPLE_FILES = {"file1.uvl", "file2.uvl", "file3.uvl"}

LOGGED_IN = (By.CSS_SELECTOR, 'a[href="/logout"]')


def log_in(driver, host, email):
    driver.get(f"{host}/login")
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "submit").click()
    WebDriverWait(driver, 15).until(EC.presence_of_element_located(LOGGED_IN))


@pytest.mark.parametrize("path", ["/dataset/list", "/dataset/upload"])
def test_anonymous_visitors_are_sent_to_the_login_form(path):
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}{path}")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "password")))
        assert "/login" in driver.current_url
        # login_required keeps the destination so the visitor lands there
        # after authenticating.
        assert path.replace("/", "%2F") in driver.current_url
        assert not driver.find_elements(*LOGGED_IN)
    finally:
        close_driver(driver)


@pytest.mark.parametrize("email", sorted(DATASETS_BY_OWNER))
def test_dataset_list_shows_only_the_datasets_owned_by_the_logged_in_user(email):
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        log_in(driver, host, email)
        driver.get(f"{host}/dataset/list")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))
        assert driver.find_element(By.CSS_SELECTOR, "h1").text.strip() == "My datasets"

        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        titles = {row.find_element(By.CSS_SELECTOR, "td a").text.strip() for row in rows}

        assert titles == DATASETS_BY_OWNER[email]
        assert not (titles & (ALL_SEEDED_TITLES - DATASETS_BY_OWNER[email]))
    finally:
        close_driver(driver)


def test_dataset_list_rows_carry_the_doi_and_download_links_of_the_dataset():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        log_in(driver, host, "user1@example.com")
        driver.get(f"{host}/dataset/list")

        row = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, f"//table//tr[td//a[normalize-space()='{SAMPLE_TITLE}']]"))
        )

        cells = row.find_elements(By.TAG_NAME, "td")
        assert cells[1].text.strip() == SAMPLE_DESCRIPTION
        assert cells[2].text.strip() == "Data Management Plan"

        assert any(SAMPLE_DOI in link.get_attribute("href") for link in row.find_elements(By.TAG_NAME, "a"))
        assert row.find_elements(By.CSS_SELECTOR, 'a[href^="/dataset/download/"]')
    finally:
        close_driver(driver)


def test_upload_page_offers_the_dataset_metadata_form():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        log_in(driver, host, "user1@example.com")
        driver.get(f"{host}/dataset/upload")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "title")))
        assert driver.find_element(By.CSS_SELECTOR, "h1").text.strip() == "Upload dataset"

        assert driver.find_element(By.CSS_SELECTOR, 'textarea[name="desc"]').is_displayed()
        assert driver.find_element(By.NAME, "tags").is_displayed()
        assert driver.find_element(By.ID, "add_author").is_displayed()

        # The UVL files are collected by a dropzone posting to the file
        # endpoint, not by a plain file input.
        dropzone = driver.find_element(By.ID, "myDropzone")
        assert dropzone.get_attribute("action").endswith("/dataset/file/upload")

        publication_type = Select(driver.find_element(By.NAME, "publication_type"))
        values = [option.get_attribute("value") for option in publication_type.options]
        assert "datamanagementplan" in values

        # Uploading stays blocked until a UVL model has been dropped in.
        assert not driver.find_element(By.ID, "upload_dataset").is_displayed()
        assert not driver.find_element(By.ID, "upload_button").is_enabled()
    finally:
        close_driver(driver)


def test_dataset_page_shows_the_metadata_and_uvl_files_behind_its_doi():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/doi/{SAMPLE_DOI}/")

        heading = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1 b")))
        assert heading.text.strip() == SAMPLE_TITLE

        body = driver.find_element(By.TAG_NAME, "body").text
        assert SAMPLE_DESCRIPTION in body
        assert SAMPLE_AUTHOR in body
        assert "Data Management Plan" in body
        # Uploaded by: the profile of the seeded owner.
        assert "Doe, John" in body

        # Each UVL file is listed as "<name>" over its "(<size>)".
        files = {
            cell.text.splitlines()[0].strip()
            for cell in driver.find_elements(By.CSS_SELECTOR, ".list-group-item div.col-8")
            if cell.text.strip()
        }
        assert files == SAMPLE_FILES

        badge = driver.find_element(By.XPATH, "//h4[normalize-space()='UVL models']/following::span[1]")
        assert badge.text.strip() == str(len(SAMPLE_FILES))
    finally:
        close_driver(driver)


def test_dataset_page_links_back_to_explore_and_to_the_full_download():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/doi/{SAMPLE_DOI}/")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1 b")))

        assert driver.find_element(By.CSS_SELECTOR, 'a.btn[href="/explore"]').is_displayed()

        download = driver.find_element(By.CSS_SELECTOR, 'a.btn[href^="/dataset/download/"]')
        assert "Download all" in download.text
    finally:
        close_driver(driver)


def test_an_unknown_doi_answers_with_the_not_found_page():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/doi/10.1234/there-is-no-such-dataset/")

        heading = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
        assert heading.text.strip() == "404"
        assert "Page Not Found" in driver.find_element(By.CSS_SELECTOR, "p.lead").text
    finally:
        close_driver(driver)
