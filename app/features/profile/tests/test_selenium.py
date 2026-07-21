"""Browser-driven end-to-end tests for profile.

Runs against the live app and the selenium grid started by
``docker compose -f docker/docker-compose.dev.yml up``, so it uses the
seeded development database rather than the test database. Run with::

    rosemary test profile --e2e

The seeded users are user1 (John Doe, datasets 1 and 3) and user2 (Jane
Doe, datasets 2 and 4), both with password 1234.

``/profile/edit`` writes to that shared database, so the tests here never
change it: the save path is exercised by resubmitting the values already
stored, and the validation path by submitting an ORCID that the form
rejects before anything is persisted. Both leave the profile exactly as
they found it, so the suite is safe to run repeatedly.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.selenium_support import close_driver, get_host_for_selenium_testing, initialize_driver

pytestmark = pytest.mark.e2e

PASSWORD = "1234"
USER_ONE = {
    "email": "user1@example.com",
    "name": "John",
    "surname": "Doe",
    "affiliation": "Some University",
    "datasets": {"Sample dataset 1": "10.1234/dataset1", "Sample dataset 3": "10.1234/dataset3"},
    "foreign_datasets": ["Sample dataset 2", "Sample dataset 4"],
}
USER_TWO = {
    "email": "user2@example.com",
    "name": "Jane",
    "surname": "Doe",
    "affiliation": "Some University",
    "datasets": {"Sample dataset 2": "10.1234/dataset2", "Sample dataset 4": "10.1234/dataset4"},
    "foreign_datasets": ["Sample dataset 1", "Sample dataset 3"],
}


def _log_in(driver, host, user):
    driver.get(f"{host}/login")
    driver.find_element(By.NAME, "email").send_keys(user["email"])
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "submit").click()
    # The logout control is an icon link, so match on its href.
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/logout"]')))


def _summary_text(driver, host):
    driver.get(f"{host}/profile/summary")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card-body")))
    return driver.find_element(By.CSS_SELECTOR, "div.card-body").text


def _edit_field_values(driver):
    return {
        field: driver.find_element(By.NAME, field).get_attribute("value")
        for field in ("name", "surname", "affiliation", "orcid")
    }


def _submit_when_settled(driver):
    """Click submit only once the page has fully settled.

    The shell loads every feature's script plus CDN assets on each page, and a
    click dispatched mid-layout can land beside the button and silently do
    nothing: the POST never happens and the test times out waiting for the
    flash. Waiting for readyState complete pins the layout first.
    """
    WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
    button = driver.find_element(By.ID, "submit")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    button.click()


@pytest.mark.parametrize("path", ["/profile/summary", "/profile/edit"])
def test_profile_pages_send_anonymous_visitors_to_the_login_form(path):
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}{path}")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "password")))

        assert "/login" in driver.current_url
        # login_required keeps the original target so the user lands back on it.
        assert f"next={path.replace('/', '%2F')}" in driver.current_url
        assert not driver.find_elements(By.CSS_SELECTOR, 'a[href="/logout"]')
        assert driver.find_element(By.NAME, "email").is_displayed()
    finally:
        close_driver(driver)


@pytest.mark.parametrize("user", [USER_ONE, USER_TWO], ids=["user1", "user2"])
def test_summary_describes_the_user_who_is_logged_in(user):
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        _log_in(driver, host, user)

        text = _summary_text(driver, host)

        assert f"Name: {user['name']}" in text
        assert f"Surname: {user['surname']}" in text
        assert f"Affiliation: {user['affiliation']}" in text
        assert f"Email: {user['email']}" in text
        assert f"Uploaded datasets: {len(user['datasets'])} datasets" in text
        # The navbar greets the same person.
        assert f"{user['surname']}, {user['name']}" in driver.find_element(By.CSS_SELECTOR, "nav.navbar").text
    finally:
        close_driver(driver)


@pytest.mark.parametrize("user", [USER_ONE, USER_TWO], ids=["user1", "user2"])
def test_summary_lists_only_the_datasets_owned_by_the_user(user):
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        _log_in(driver, host, user)
        driver.get(f"{host}/profile/summary")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
        titles = [
            row.find_element(By.TAG_NAME, "td").text.strip()
            for row in driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        ]

        assert sorted(titles) == sorted(user["datasets"])
        for foreign in user["foreign_datasets"]:
            assert foreign not in titles
    finally:
        close_driver(driver)


def test_summary_dataset_titles_link_to_their_own_dataset_page():
    """Each row must point at the DOI of the dataset named in that row.

    The link is not followed: the template builds it from ``DOMAIN``, which
    is ``localhost`` here, and inside the browser container that resolves to
    the browser itself rather than to the app.
    """
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        _log_in(driver, host, USER_ONE)
        driver.get(f"{host}/profile/summary")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr a")))
        links = {
            link.text.strip(): link.get_attribute("href")
            for link in driver.find_elements(By.CSS_SELECTOR, "table tbody tr a")
        }

        assert sorted(links) == sorted(USER_ONE["datasets"])
        for title, doi in USER_ONE["datasets"].items():
            assert links[title].endswith(f"/doi/{doi}")
    finally:
        close_driver(driver)


def test_edit_form_arrives_prefilled_with_the_stored_profile():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        _log_in(driver, host, USER_ONE)
        driver.get(f"{host}/profile/edit")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))

        values = _edit_field_values(driver)
        assert values["name"] == USER_ONE["name"]
        assert values["surname"] == USER_ONE["surname"]
        assert values["affiliation"] == USER_ONE["affiliation"]
        assert driver.find_element(By.TAG_NAME, "h1").text.strip() == "Edit profile"
    finally:
        close_driver(driver)


def test_saving_the_unchanged_profile_confirms_success_and_keeps_the_values():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        _log_in(driver, host, USER_ONE)
        driver.get(f"{host}/profile/edit")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))
        before = _edit_field_values(driver)
        _submit_when_settled(driver)

        alert = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.alert-success")),
        )
        assert "Profile updated successfully" in alert.text
        assert "/profile/edit" in driver.current_url

        # Reload from the database rather than trusting the redirected page.
        driver.get(f"{host}/profile/edit")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))
        assert _edit_field_values(driver) == before

        text = _summary_text(driver, host)
        assert f"Name: {USER_ONE['name']}" in text
        assert f"Surname: {USER_ONE['surname']}" in text
    finally:
        close_driver(driver)


def test_edit_rejects_a_malformed_orcid_without_touching_the_profile():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        _log_in(driver, host, USER_ONE)
        driver.get(f"{host}/profile/edit")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "orcid")))
        orcid = driver.find_element(By.NAME, "orcid")
        orcid.clear()
        orcid.send_keys("not-an-orcid")
        _submit_when_settled(driver)

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "orcid")))
        errors = [element.text.strip() for element in driver.find_elements(By.CSS_SELECTOR, "form span")]
        assert any("ORCID" in error or "orcid" in error.lower() for error in errors), errors
        assert not driver.find_elements(By.CSS_SELECTOR, "div.alert-success")

        # Nothing was written, so a fresh load still shows the stored values.
        driver.get(f"{host}/profile/edit")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))
        values = _edit_field_values(driver)
        assert values["name"] == USER_ONE["name"]
        assert values["surname"] == USER_ONE["surname"]
        assert values["affiliation"] == USER_ONE["affiliation"]
        assert values["orcid"] == ""
    finally:
        close_driver(driver)
