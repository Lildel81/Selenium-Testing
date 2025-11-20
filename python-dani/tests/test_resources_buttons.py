from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_resource_download_button_redirects(driver):
    driver.get("http://localhost:8080/resources")
    wait = WebDriverWait(driver, 10)

    # select button
    buttons = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//button[contains(@class, 'image-button')]")
        )
    )

    assert len(buttons) > 0, "No clickable buttons found"

    first_button = buttons[0]

    # Scroll into view (important on grid layouts)
    driver.execute_script("arguments[0].scrollIntoView(true);", first_button)

    # Click using JS because Selenium click fails on nested <a><button> situations
    driver.execute_script("arguments[0].click();", first_button)

    # Wait for new tab to appear
    wait.until(lambda d: len(d.window_handles) > 1)

    # Switch to new tab
    driver.switch_to.window(driver.window_handles[-1])

    # Wait for URL to load
    wait.until(lambda d: d.current_url != "")

    # Validate redirect
    assert "google" in driver.current_url.lower()
