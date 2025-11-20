"""
    Pytest configuration and fixtures for Selenium tests
    This provides shared test fixtures and configuration
"""
import pytest                                                   # Testing framework; automatically discovers and runs tests
import os                                                       # Access env var, file paths,...
from selenium import webdriver                                  # Core Selenium Webdriver (controls the browser)
from selenium.webdriver.chrome.service import Service           # Specifies ChromeDriver executable location
from selenium.webdriver.chrome.options import Options           # configures Chrome behavior
from selenium.webdriver.support.ui import WebDriverWait         # Explicit waits (wait for conditions instead of sleep)
from selenium.webdriver.support import expected_conditions as EC# Pre-built wait conditions
from selenium.webdriver.common.by import By                     # Locators: By.ID, By.PATH, By.CSS_SELECTOR,...
from selenium.common.exceptions import TimeoutException          # Exception for timeouts
from webdriver_manager.chrome import ChromeDriverManager        # Automatically downloads & manages correct ChromeDriver version
from dotenv import load_dotenv                                  # Loads var from .env file into os.getenv()
import sys
import os
import time                                                      # For sleep/delays
sys.path.insert(0, os.path.dirname(__file__))
from helpers import wait_for_page_load                          # Helper function for waiting for page load

# Load environment variables
load_dotenv()

# Base URL for the app
BASE_URL = os.getenv("TEST_BASE_URL", "https://graceful-living-web-application.onrender.com")

@pytest.fixture(scope="session")
def base_url():
    # Provide BASE_URL to tests
    return BASE_URL

# Admin credentials (setup in .env)
ADMIN_USERNAME = os.getenv("TEST_ADMIN_USERNAME", "skumar")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "changeyou")

# Create and configure Chrome WebDriver instance
# This fixture is session-scoped, so it's created once per test session
@pytest.fixture(scope="session")
def driver():
    chrome_options = Options()

    # Add options for better compatibility
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # If we want tests to run in headless mode which is no browser window, uncomment the below
    # chrome_options.add_argument("--headless")

    # Initialize Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    driver.implicitly_wait(10)

    yield driver

    # Cleanup
    driver.quit()

"""
    Fixture that logs in as admin and returns the driver
    This ensures all tests start with an authenticated session
"""
@pytest.fixture
def logged_in_driver(driver):
    # Handle any existing alerts from previous tests
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        print(f"⚠ Dismissed existing alert before login: {alert_text}")
    except:
        # No alert present, which is fine
        pass
    
    # Ensure we're on the correct domain - clear any previous navigation
    # First, navigate to BASE_URL to ensure we're on the right domain
    driver.get(f"{BASE_URL}/")
    wait_for_page_load(driver)
    time.sleep(1)
    
    # Now navigate to login page
    driver.get(f"{BASE_URL}/login")
    wait_for_page_load(driver)
    
    # Verify we're on the correct domain
    current_url = driver.current_url
    if BASE_URL not in current_url:
        pytest.fail(f"Wrong domain! Expected {BASE_URL}, but got {current_url}. Check TEST_BASE_URL environment variable.")
    print(f"✓ Navigating to login page: {current_url}")

    # Wait for login form to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    # Wait for CSRF token to be present in the form
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "_csrf"))
    )
    
    # Wait for CSRF cookie to be set (check cookies)
    import time
    max_retries = 5
    for i in range(max_retries):
        cookies = driver.get_cookies()
        csrf_cookie = next((c for c in cookies if c.get('name') == '_csrf'), None)
        if csrf_cookie and csrf_cookie.get('value'):
            print(f"✓ CSRF cookie found: {csrf_cookie.get('value')[:20]}...")
            break
        time.sleep(1)
    else:
        print("⚠ CSRF cookie not found in cookies, but continuing...")
    
    # Additional wait to ensure everything is loaded
    time.sleep(2)

    # Get CSRF token from form and verify it
    csrf_input = driver.find_element(By.NAME, "_csrf")
    csrf_value = csrf_input.get_attribute("value")
    
    if not csrf_value:
        # If token is missing, refresh and try again
        print("⚠ CSRF token is empty, refreshing page...")
        driver.refresh()
        wait_for_page_load(driver)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "_csrf"))
        )
        time.sleep(2)
        
        # Re-check CSRF token
        csrf_input = driver.find_element(By.NAME, "_csrf")
        csrf_value = csrf_input.get_attribute("value")
        if not csrf_value:
            pytest.fail("CSRF token is still empty after refresh")

    print(f"✓ CSRF token from form: {csrf_value[:20]}...")

    # Fill in login form
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")

    username_field.clear()
    username_field.send_keys(ADMIN_USERNAME)

    password_field.clear()
    password_field.send_keys(ADMIN_PASSWORD)

    # Verify CSRF token is still present right before submission
    csrf_input = driver.find_element(By.NAME, "_csrf")
    final_csrf_value = csrf_input.get_attribute("value")
    assert final_csrf_value, "CSRF token disappeared before form submission"
    
    # Verify CSRF cookie is still present
    cookies = driver.get_cookies()
    csrf_cookie = next((c for c in cookies if c.get('name') == '_csrf'), None)
    if csrf_cookie:
        print(f"✓ CSRF cookie verified before submission: {csrf_cookie.get('value')[:20]}...")

    # Submit login form
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
    login_button.click()

    # Wait a moment for form submission to process
    time.sleep(3)  # Increased wait time

    # Check for error messages first
    try:
        error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, [class*='error'], [class*='alert'], p.error")
        error_text = "\n".join([elem.text for elem in error_elements if elem.text.strip()])

        if error_text and "csrf" in error_text.lower():
            pytest.fail(f"CSRF token error during login: {error_text}\,Current URL: {driver.current_url}")
        elif error_text:
            pytest.fail(f"Login failed with error: {error_text}\nCurrent URL: {driver.current_url}")
    except:
        pass
    # Wait for redirect after successful login
    try: 
        WebDriverWait(driver, 15).until(
            lambda d: d.current_url and "/login" not in d.current_url and BASE_URL in d.current_url
        )
        # Verify we're on the correct domain after login
        final_url = driver.current_url
        if BASE_URL not in final_url:
            pytest.fail(f"After login, redirected to wrong domain! Expected {BASE_URL}, but got {final_url}")
        print(f"✓ Login successful, redirected to: {final_url}")
    except TimeoutException as e:
        # Check current URL first
        current_url = driver.current_url
        print(f"⚠ Login redirect timeout. Current URL: {current_url}")
        
        # Check page source for error messages
        page_source = driver.page_source.lower()
        if "invalid csrf token" in page_source or ("csrf" in page_source and "error" in page_source):
            pytest.fail(f"CSRF token error detected. Current URL: {current_url}")
        elif "invalid username" in page_source or "invalid password" in page_source:
            pytest.fail(f"Invalid credentials. Current URL: {current_url}")
        elif BASE_URL not in current_url:
            pytest.fail(f"Wrong domain after login attempt! Expected {BASE_URL}, but got {current_url}. Check TEST_BASE_URL environment variable.")
        else:
            pytest.fail(f"Login did not redirect. Current URL: {current_url}. Page may contain errors")

    yield driver

"""
    Provides a WebDriverWait instance for explicit waits
"""
@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 10)

"""
    Reset state before each test
    This can be customized to clean up test data if needed
"""
@pytest.fixture(autouse=True)
def reset_state(driver):
    # Before test: Ensure we're on the correct domain
    try:
        current_url = driver.current_url
        if current_url and BASE_URL not in current_url and "data:," not in current_url:
            # If we're on a wrong domain, navigate to BASE_URL
            print(f"⚠ Wrong domain detected before test: {current_url}, navigating to {BASE_URL}")
            driver.get(f"{BASE_URL}/")
            wait_for_page_load(driver)
            time.sleep(1)
    except:
        # Driver might not be initialized yet, which is fine
        pass
    
    yield
    
    # After test: Clean up
    # Clean up: dismiss any alerts that might be left from the test
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        print(f"⚠ Dismissed alert after test: {alert_text}")
    except:
        # No alert present, which is fine
        pass
    # Clean up any custom attributes added during tests
    if hasattr(driver, '_booking_alert_text'):
        delattr(driver, '_booking_alert_text')
    
    # Ensure we're back on BASE_URL after test (if driver is still active)
    try:
        current_url = driver.current_url
        if current_url and BASE_URL not in current_url and "data:," not in current_url:
            print(f"⚠ Wrong domain after test: {current_url}, resetting to {BASE_URL}")
            driver.get(f"{BASE_URL}/")
    except:
        # Driver might be closed, which is fine
        pass