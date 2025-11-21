from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_contact_buttons(driver):
    driver.get("http://localhost:8080/contact")
    wait = WebDriverWait(driver, 10)

    # Buttons on the page
    quiz_button = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[text()='Take the Quiz']"))
    )
    app_button = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[text()='Start Application']"))
    )

    # === Test 1: "Take the Quiz" button ===
    initial_tabs = driver.window_handles

    # Scroll into view
    driver.execute_script("arguments[0].scrollIntoView(true);", quiz_button)

    # JavaScript click for reliability
    driver.execute_script("arguments[0].click();", quiz_button)

    # Wait for new tab
    wait.until(lambda d: len(d.window_handles) > len(initial_tabs))

    # Switch to new tab
    new_tab = driver.window_handles[-1]
    driver.switch_to.window(new_tab)

    # Check URL
    wait.until(lambda d: d.current_url != "")
    assert "/intro" in driver.current_url, "Quiz button did not open /intro page"

    # Close tab and return to main tab
    driver.close()
    driver.switch_to.window(initial_tabs[0])

    # === Test 2: "Start Application" button ===
    initial_tabs = driver.window_handles

    driver.execute_script("arguments[0].scrollIntoView(true);", app_button)
    driver.execute_script("arguments[0].click();", app_button)

    wait.until(lambda d: len(d.window_handles) > len(initial_tabs))

    new_tab = driver.window_handles[-1]
    driver.switch_to.window(new_tab)

    wait.until(lambda d: d.current_url != "")
    assert "/pre-app" in driver.current_url, "Start Application button did not open /pre-app page"
