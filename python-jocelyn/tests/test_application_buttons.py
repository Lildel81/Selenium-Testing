import os

import pytest
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (NoAlertPresentException, TimeoutException,  StaleElementReferenceException,)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

# Read BASE_URL from environment
BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    raise RuntimeError("BASE_URL is not set in .env")


def open_page(driver, path):
    driver.get(BASE_URL + path)


def click_all_buttons(driver):
    buttons = driver.find_elements(By.TAG_NAME, "button")
    links = driver.find_elements(By.CSS_SELECTOR, "a.btn-next")
    all_clickables = buttons + links

    assert len(all_clickables) > 0, "No buttons found on page."

    for i in range(len(all_clickables)):
        # Reload DOM
        buttons = driver.find_elements(By.TAG_NAME, "button")
        links = driver.find_elements(By.CSS_SELECTOR, "a.btn-next")
        all_clickables = buttons + links

        element = all_clickables[i]
        assert element.is_displayed()
        assert element.is_enabled()
        element.click()





def click_submit_button(driver, timeout=10):
    """
    Waits for the main application submit button to be clickable
    and clicks it. Retries a couple times if the element goes stale.
    """
    wait = WebDriverWait(driver, timeout)
    for _ in range(3):  # try up to 3 times if it goes stale
        try:
            btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.submit-btn"))
            )
            btn.click()
            return
        except StaleElementReferenceException:
            # DOM changed between finding and clicking, try again
            continue

    # If we reach here, all attempts failed
    assert False, "Submit button kept going stale and could not be clicked."




def wait_for_application_form(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "assessment-form"))
    )



# Verify that all buttons on the pre-application page are visible
@pytest.mark.app
def test_pre_app_buttons_clickable(driver):
    open_page(driver, "/pre-app")

    button = driver.find_element(By.CSS_SELECTOR, "button.btn-next")
    assert button.is_enabled()
    button.click()

    try:
        alert = driver.switch_to.alert
        text = alert.text
        # Optional: check message contains expected text
        assert "Please answer question 1" in text
        alert.accept()  # close the alert
    except NoAlertPresentException:
        # If no alert showed up, that’s fine too
        pass


#Tests: APPLICATION PAGE
def fill_application_form(driver):

    # ---- REQUIRED INPUT TEXT FIELDS ----
    driver.find_element(By.ID, "fullName").send_keys("Test User")
    driver.find_element(By.ID, "email").send_keys("test@example.com")
    driver.find_element(By.ID, "contactNumber").send_keys("916-555-1234")

    # ---- RADIO BUTTONS ---- (Age bracket)
    driver.find_element(By.CSS_SELECTOR, "input[name='ageBracket'][value='30-40']").click()

    # Healthcare Worker
    driver.find_element(By.ID, "hc-no").click()

    # ---- JOB TITLE ----
    driver.find_element(By.ID, "jobTitle").send_keys("Software Engineer")

    # ---- PRACTITIONER RADIO ----
    driver.find_element(By.CSS_SELECTOR, "input[name='workedWithPractitioner'][value='First time']").click()

    # ---- FAMILIAR WITH (checkboxes) ----
    driver.find_element(By.CSS_SELECTOR, "input[name='familiarWith'][value='Kundalini Yoga']").click()

    # ---- EXPERIENCE textarea ----
    driver.find_element(By.ID, "experience").send_keys("Some experience, felt calm afterwards.")

    # ---- GOALS textarea ----
    driver.find_element(By.ID, "goals").send_keys("Improve sleep and reduce burnout.")

    # ---- CHALLENGES (checkboxes) ----
    driver.find_element(By.CSS_SELECTOR, "input[name='challenges'][value='Emotional']").click()
    driver.find_element(By.CSS_SELECTOR, "input[name='challenges'][value='Mental']").click()







@pytest.mark.app
def test_application_other_buttons_clickable(driver):
    open_page(driver, "/application")
    wait_for_application_form(driver)

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button.submit-btn")
    assert submit_btn.is_displayed()
    assert submit_btn.is_enabled()






