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

def test_admin_login(driver):
    wait = WebDriverWait(driver, 10)
    admin_login(driver, wait)

    # Final assertion
    assert "/adminportal" in driver.current_url

def switch_to_aboutus_iframe(driver, wait):
    # Go to Content Management
    driver.get("http://localhost:8080/content-management")

    # 1. Click the About Us tab
    aboutus_tab = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@class='tab' and @data-target='panel-about']")
        )
    )
    aboutus_tab.click()

    # 2. Wait for the panel to become visible
    wait.until(
        EC.visibility_of_element_located((By.ID, "panel-about"))
    )

    # 3. Now wait for the iframe inside this panel
    iframe = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//iframe[@title='About Us Management']")
        )
    )

    # 4. Switch to the iframe
    driver.switch_to.frame(iframe)

    # 5. Wait for header inside iframe
    header = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h2[contains(text(), 'Manage About Us')]")
        )
    )
    return header

def test_open_aboutus_management(driver):
    wait = WebDriverWait(driver, 10)
    admin_login(driver, wait)

    header = switch_to_aboutus_iframe(driver, wait)

    assert header.is_displayed()

def test_edit_aboutus_intro(driver):
    wait = WebDriverWait(driver, 10)

    admin_login(driver, wait)
    switch_to_aboutus_iframe(driver, wait)

    new_title = "Selenium Intro Title"
    new_description = "This intro was updated automatically by a Selenium test."

    # --- Step 1: edit fields ---
    title_input = driver.find_element(By.NAME, "title")
    desc_textarea = driver.find_element(By.NAME, "description")
    headshot_input = driver.find_element(By.NAME, "headshot")

    title_input.clear()
    title_input.send_keys(new_title)

    desc_textarea.clear()
    desc_textarea.send_keys(new_description)

    # Upload image
    test_image_path = os.path.abspath("tests/test.jpg")
    headshot_input.send_keys(test_image_path)

    # Submit form
    submit_btn = driver.find_element(
        By.XPATH, "//button[contains(text(), 'Update Intro')]"
    )
    submit_btn.click()

    # --- Step 2: iframe reloads → switch out and back in ---
    driver.switch_to.default_content()
    switch_to_aboutus_iframe(driver, wait)

    # --- Step 3: Wait for updated values ---
    updated_title_input = wait.until(
        EC.presence_of_element_located((By.NAME, "title"))
    )
    updated_title = updated_title_input.get_attribute("value")

    updated_desc = driver.find_element(By.NAME, "description").get_attribute("value")

    # --- Step 4: Assertions ---
    assert updated_title == new_title
    assert new_description in updated_desc


def test_create_aboutus_content(driver):
    wait = WebDriverWait(driver, 10)
    admin_login(driver, wait)
    switch_to_aboutus_iframe(driver, wait)

    # Unique test values
    content_title = "About Block Title"
    content_description = "This is an about-us content block created by Selenium."

    # Find the "Add New Content Section" form via its button text
    content_form = driver.find_element(
        By.XPATH, "//form[.//button[text()='Add Content Block']]"
    )

    # Fill fields within that form
    title_input = content_form.find_element(By.NAME, "title")
    desc_textarea = content_form.find_element(By.NAME, "description")
    image_input = content_form.find_element(By.NAME, "image")

    title_input.send_keys(content_title)
    desc_textarea.send_keys(content_description)

    # Upload required image
    test_image_path = os.path.abspath("tests/test.jpg")
    image_input.send_keys(test_image_path)

    # Submit the form
    content_form.find_element(By.XPATH, ".//button[text()='Add Content Block']").click()

    # Wait for table row with this title
    new_row = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, f"//tbody/tr[td[contains(text(), '{content_title}')]]")
        )
    )

    assert new_row.is_displayed()

def test_edit_aboutus_content(driver):
    wait = WebDriverWait(driver, 10)
    admin_login(driver, wait)
    switch_to_aboutus_iframe(driver, wait)

    original_title = "About Block Title"
    updated_title = "Updated About Block Title"
    updated_description = "Updated about-us block description."

    # Click the Edit link for the row with original title
    edit_link = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f"//tr[td[contains(text(), '{original_title}')]]//a[contains(text(), 'Edit')]"
            )
        )
    )
    edit_link.click()

    # Stay inside iframe – edit page loads in same iframe
    name_field = wait.until(
        EC.presence_of_element_located((By.NAME, "title"))
    )
    desc_field = driver.find_element(By.NAME, "description")

    # Clear + update
    name_field.clear()
    name_field.send_keys(updated_title)

    desc_field.clear()
    desc_field.send_keys(updated_description)

    # upload new image
    image_input = driver.find_element(By.NAME, "image")
    test_image_path = os.path.abspath("tests/test2.jpg")
    image_input.send_keys(test_image_path)

    # Submit
    update_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Update Content Block')]")
        )
    )
    update_btn.click()

    # After update, iframe reloads → reset context
    driver.switch_to.default_content()
    switch_to_aboutus_iframe(driver, wait)

    # Verify updated title row exists
    updated_row = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//tr[td[contains(., 'Updated About Block Title')]]")
        )
    )

    assert updated_row.is_displayed()


def test_delete_aboutus_content(driver):
    wait = WebDriverWait(driver, 10)

    # 1. Login
    admin_login(driver, wait)

    # 2. Enter About Us iframe
    switch_to_aboutus_iframe(driver, wait)

    # 3. Click the delete button for the updated content block
    delete_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//tr[td[contains(., 'Updated About Block Title')]]"
            "//form/button[contains(text(), 'Delete') or contains(text(), '🗑')]"
        ))
    )

    delete_button.click()

    # 4. After clicking delete, the iframe reloads → switch out and back in
    driver.switch_to.default_content()
    switch_to_aboutus_iframe(driver, wait)

    # 5. Verify content is removed from table
    page_source = driver.page_source

    assert "Updated About Block Title" not in page_source

