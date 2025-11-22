from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

from dotenv import load_dotenv
import os

import time

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def admin_login(driver, wait):
    driver.delete_all_cookies()

    driver.get("http://localhost:8080/login")

    driver.refresh()

    # Wait for CSRF cookie
    wait.until(lambda d: any(c['name'] == '_csrf' for c in d.get_cookies()))

    # Fill form
    driver.find_element(By.NAME, "username").send_keys(ADMIN_USERNAME)
    driver.find_element(By.NAME, "password").send_keys(ADMIN_PASSWORD)

    # Normal click
    login_btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button.login_button[type='submit']")
    ))
    login_btn.click()

    # Wait for redirect
    wait.until(EC.url_contains("/adminportal"))

def test_delete_energy_leak_results(driver):
     # 1. Wait for page to load 
    wait = WebDriverWait(driver, 10)

    # 2. Log into Admin Portal
    admin_login(driver, wait)

    # 3. Go to Energy Leak Results
    driver.get("http://localhost:8080/clientmanagement/chakraquiz-results")

    # 4. Select most recent Energy Leak Result
    first_checkbox = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='checkbox'][name='ids[]']")
        )
    )

    # Click the checkbox
    first_checkbox.click()

    # debug if right check box was clicked 
    #time.sleep(5)

    # 5. Get value of item we will delete
    deleted_id = first_checkbox.get_attribute("value")

    # 6. Find delete button 
    delete_button = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[contains(text(), 'Delete Selected')]")
        )
    )

    delete_button.click()

    # debug if right check box was clicked 
    # time.sleep(5)

    # 7. Accept alert
    alert = wait.until(EC.alert_is_present())
    alert.accept()

    # 8. Wait for reload
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "table")  # ensures the page refreshed
    ))


    # 9. Get the new page HTML
    page_source = driver.page_source

    # 10. confirm deleted
    assert deleted_id not in page_source