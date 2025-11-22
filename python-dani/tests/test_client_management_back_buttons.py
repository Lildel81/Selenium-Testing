from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from dotenv import load_dotenv
import os

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

def test_back_to_admin_portal_button(driver):
    # 1. wait for page to load 
    wait = WebDriverWait(driver, 10)

    # 2. Log into Admin Portal
    admin_login(driver, wait)

    # 3. Go to Content Management
    driver.get("http://localhost:8080/clientmanagement")

    # 4. Click the back button
    back_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Back to Admin Portal')]")
        )
    )
    back_button.click()

    # 5. See if back to Admin Portal
    wait.until(lambda d: d.current_url != "")
    assert "/adminportal" in driver.current_url, "Client Management back button did not open /adminportal"

def test_appliction_back_to_client_management_button(driver):
    # 1. wait for page to load 
    wait = WebDriverWait(driver, 10)

    # 2. Log into Admin Portal
    admin_login(driver, wait)

    # 3. Go to Content Management
    driver.get("http://localhost:8080/clientmanagement/prequiz-results")

    # 4. Click the back button
    back_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[@class='btn back-page-action']")
        )
    )
    back_button.click()

    # 5. See if back to Admin Portal
    wait.until(lambda d: d.current_url != "")
    assert "/clientmanagement" in driver.current_url, "Application Results back button did not open /clientmanagement"

def test_energy_leak_back_to_client_management_button(driver):
    # 1. wait for page to load 
    wait = WebDriverWait(driver, 10)

    # 2. Log into Admin Portal
    admin_login(driver, wait)

    # 3. Go to Content Management
    driver.get("http://localhost:8080/clientmanagement/chakraquiz-results")

    # 4. Click the back button
    back_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[@class='btn back-page-action']")
        )
    )
    back_button.click()

    # 5. See if back to Admin Portal
    wait.until(lambda d: d.current_url != "")
    assert "/clientmanagement" in driver.current_url, "Energy Leak Results back button did not open /clientmanagement"

def test_add_client_to_admin_portal_button(driver):
    # 1. wait for page to load 
    wait = WebDriverWait(driver, 10)

    # 2. Log into Admin Portal
    admin_login(driver, wait)

    # 3. Go to Content Management
    driver.get("http://localhost:8080/clientmanagement/add")

    # 4. Click the back button
    back_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[@class='btn-back']")
        )

    )
    back_button.click()

    # 5. See if back to Admin Portal
    wait.until(lambda d: d.current_url != "")
    assert "/adminportal" in driver.current_url, "Add Client back button did not open /adminportal"