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

    # Wait for CSRF field
    # csrf_input = wait.until(
    #     EC.presence_of_element_located((By.NAME, "_csrf"))
    # )
    # csrf_token = csrf_input.get_attribute("value")

    # Wait for CSRF cookie
    wait.until(lambda d: any(c['name'] == '_csrf' for c in d.get_cookies()))

    # csrf_cookie = next(c for c in driver.get_cookies() if c['name'] == '_csrf')

    # for debugging purposes 
    # print("FIELD:", csrf_token)
    # print("COOKIE:", csrf_cookie['value'])

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

def test_admin_login(driver):
    wait = WebDriverWait(driver, 10)
    admin_login(driver, wait)

    # Final assertion
    assert "/adminportal" in driver.current_url

def switch_to_services_iframe(driver, wait):
    # Go to Content Management
    driver.get("http://localhost:8080/content-management")

    # 1. Click the Services tab
    services_tab = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@class='tab' and @data-target='panel-services']")
        )
    )
    services_tab.click()

    # 2. Wait for the panel to become visible
    wait.until(
        EC.visibility_of_element_located((By.ID, "panel-services"))
    )

    # 3. Now wait for the iframe inside this panel
    iframe = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//iframe[@title='Services Management']")
        )
    )

    # 4. Switch to the iframe
    driver.switch_to.frame(iframe)

    # 5. Wait for header inside iframe
    header = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h2[contains(text(), 'Manage Services')]")
        )
    )
    return header


def test_open_services_management(driver):
    wait = WebDriverWait(driver, 10)
    admin_login(driver, wait)

    header = switch_to_services_iframe(driver, wait)

    assert header.is_displayed()

def test_create_service(driver):
    wait = WebDriverWait(driver, 10)

    admin_login(driver, wait)
    switch_to_services_iframe(driver, wait)

    # Fill form
    driver.find_element(By.NAME, "serviceName").send_keys("Test Service")
    driver.find_element(By.NAME, "serviceDescription").send_keys("Service created by Selenium")
    driver.find_element(By.NAME, "buttonText").send_keys("Learn More")
    driver.find_element(By.NAME, "buttonUrl").send_keys("https://example.com")

    # Upload an image (use a small PNG from your repo)
    test_image_path = os.path.abspath("tests/test.jpg")
    driver.find_element(By.ID, "image").send_keys(test_image_path)

    # Submit
    driver.find_element(By.XPATH, "//button[text()='Add Service']").click()

    # Wait for table to update & find the new row
    new_row = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//td[contains(text(), 'Test Service')]")
        )
    )

    assert new_row.is_displayed()

def test_edit_service(driver):
    wait = WebDriverWait(driver, 10)

    # 1. Log in
    admin_login(driver, wait)

    # 2. Enter iframe
    switch_to_services_iframe(driver, wait)

    # 3. Click edit link
    edit_link = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//tr[td[contains(text(), 'Test Service')]]//a[contains(text(), 'Edit')]")
        )
    )
    edit_link.click()

    # 🚫 NO staleness_of — iframe did NOT reload

    # 4. Now directly wait for the edit page fields (inside same iframe)
    name_field = wait.until(
        EC.presence_of_element_located((By.NAME, "serviceName"))
    )
    desc_field = driver.find_element(By.NAME, "serviceDescription")

    # 5. Edit fields
    name_field.clear()
    name_field.send_keys("Updated Test Service")

    desc_field.clear()
    desc_field.send_keys("Updated description")

    # 6. Submit update
    update_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Update Service')]")
        )
    )
    update_btn.click()

    # 7. After clicking update, the iframe WILL reload → switch out & back in
    driver.switch_to.default_content()
    switch_to_services_iframe(driver, wait)

    # 8. Verify update
    updated_row = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//td[contains(text(), 'Updated Test Service')]")
        )
    )

    assert updated_row.is_displayed()

def test_delete_service(driver):
    wait = WebDriverWait(driver, 10)

    # 1. Log in
    admin_login(driver, wait)

    # 2. Enter iframe
    switch_to_services_iframe(driver, wait)

    # 3. Find delete button for the correct row
    delete_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//tr[td[contains(text(),'Updated Test Service')]]//form/button[contains(text(),'Delete') or contains(text(),'🗑️')]"
        ))
    )

    # Click delete
    delete_button.click()

    # 4. After clicking delete, iframe reloads
    driver.switch_to.default_content()
    switch_to_services_iframe(driver, wait)

    # 5. Verify the service is gone
    page_source = driver.page_source

    assert "Updated Test Service" not in page_source
