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

# Print BASE_URL for debugging
print(f"\n{'='*60}")
print(f"TEST CONFIGURATION:")
print(f"BASE_URL: {BASE_URL}")
print(f"TEST_BASE_URL env var: {os.getenv('TEST_BASE_URL', 'NOT SET (using default)')}")
print(f"{'='*60}\n")

# Domain verification removed to allow testing against any URL including production

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
    
    # Navigate to BASE_URL initially
    print(f"Initializing driver with BASE_URL: {BASE_URL}")
    driver.get(f"{BASE_URL}/")
    wait_for_page_load(driver)
    time.sleep(1)

    yield driver

    # Cleanup
    try:
        driver.quit()
    except:
        pass  # Driver might already be closed

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
    
    # Clear all cookies before login to ensure fresh session
    # This helps avoid CSRF token validation issues from previous test runs
    try:
        driver.delete_all_cookies()
        print("✓ Cleared all cookies before login")
    except:
        pass
    
    # Clear any previous navigation and navigate to BASE_URL
    driver.get(f"{BASE_URL}/")
    wait_for_page_load(driver)
    time.sleep(1)
    
    # Now navigate to login page
    driver.get(f"{BASE_URL}/login")
    wait_for_page_load(driver)
    time.sleep(1)  # Additional wait for page to fully load
    
    current_url = driver.current_url
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

    # Try to submit login with retry mechanism for CSRF issues
    max_login_retries = 2
    login_successful = False
    
    for attempt in range(max_login_retries):
        if attempt > 0:
            # On retry, refresh the page to get a fresh CSRF token
            print(f"⚠ Login attempt {attempt} failed, refreshing page for fresh CSRF token (attempt {attempt + 1}/{max_login_retries})...")
            driver.get(f"{BASE_URL}/login")
            wait_for_page_load(driver)
            time.sleep(2)
            
            # Wait for login form to load again
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "_csrf"))
            )
            
            # Re-fill the form with fresh CSRF token
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            username_field.clear()
            username_field.send_keys(ADMIN_USERNAME)
            password_field.clear()
            password_field.send_keys(ADMIN_PASSWORD)
            
            # Verify CSRF token is present and fresh
            csrf_input = driver.find_element(By.NAME, "_csrf")
            fresh_csrf_value = csrf_input.get_attribute("value")
            assert fresh_csrf_value, f"CSRF token is empty on retry attempt {attempt + 1}"
            print(f"✓ Got fresh CSRF token for retry: {fresh_csrf_value[:20]}...")
        
        # Submit login form
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        
        # Get current URL before clicking
        url_before_login = driver.current_url
        
        login_button.click()
        
        # Wait a moment for form submission to process
        time.sleep(3)  # Increased wait time
        
        # Check if URL changed immediately (indicates redirect started)
        try:
            WebDriverWait(driver, 2).until(
                lambda d: d.current_url != url_before_login
            )
            print("✓ URL changed after login click, redirect in progress...")
        except TimeoutException:
            # URL didn't change quickly, might be an error
            pass
        
        time.sleep(2)  # Additional wait for redirect to complete

        # Wait for redirect after successful login (check immediately, don't wait for errors first)
        # The redirect should happen quickly if login is successful
        try: 
            WebDriverWait(driver, 15).until(
                lambda d: d.current_url and "/login" not in d.current_url
            )
            final_url = driver.current_url
            print(f"✓ Login successful, redirected to: {final_url}")
            login_successful = True
            break  # Success! Exit retry loop
        except TimeoutException:
            # Login didn't redirect, check for errors
            pass
        
        # If we haven't succeeded yet and there are more retries, continue to next attempt
        if not login_successful and attempt < max_login_retries - 1:
            # Check for CSRF error before retrying
            page_source = driver.page_source.lower()
            if "invalid csrf token" in page_source:
                print(f"⚠ CSRF token error detected on attempt {attempt + 1}, will retry...")
            continue
    
    # If login didn't succeed after all retries, check for error messages
    if not login_successful:
        time.sleep(1)  # Wait a bit for any error messages to appear
        try:
            error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, [class*='error'], [class*='alert'], p.error, [id='msg']")
            error_text = "\n".join([elem.text for elem in error_elements if elem.text.strip()])

            if error_text and "csrf" in error_text.lower():
                pytest.fail(f"CSRF token error during login: {error_text}\nCurrent URL: {driver.current_url}")
            elif error_text:
                pytest.fail(f"Login failed with error: {error_text}\nCurrent URL: {driver.current_url}")
        except:
            pass
        
        # Check current URL and page source
        current_url = driver.current_url
        print(f"⚠ Login redirect timeout. Current URL: {current_url}")
        
        # Check page source for error messages
        page_source = driver.page_source.lower()
        
        # Check for specific error messages in page source
        has_csrf_error = "invalid csrf token" in page_source or ("csrf" in page_source and "error" in page_source and "token" in page_source)
        has_credential_error = "invalid username" in page_source or "invalid password" in page_source
        
        # Try to find visible error elements on the page
        error_text = ""
        try:
            error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, [class*='error'], [class*='alert'], p.error, [id='msg'], [role='alert']")
            error_text = "\n".join([elem.text for elem in error_elements if elem.text.strip()])
        except:
            pass
        
        # Determine the actual error
        if has_csrf_error or (error_text and "csrf" in error_text.lower()):
            pytest.fail(f"CSRF token error during login.\nError text: {error_text}\nCurrent URL: {current_url}\nPage source snippet: {page_source[:300]}")
        elif has_credential_error or (error_text and ("invalid" in error_text.lower() or "password" in error_text.lower() or "username" in error_text.lower())):
            pytest.fail(f"Invalid credentials.\nError text: {error_text}\nCurrent URL: {current_url}")
        else:
            # Check if we're on login page but no error shown - login might have failed silently
            if "/login" in current_url:
                # Check if form was actually submitted (check if fields are still filled)
                try:
                    username_field = driver.find_element(By.NAME, "username")
                    if username_field.get_attribute("value") == ADMIN_USERNAME:
                        # Form still has values, might not have submitted
                        pytest.fail(f"Login form submission may have failed. Still on login page: {current_url}.\nNo error message found. Check:\n1. Server is running and accessible\n2. Credentials are correct\n3. Network connectivity\nPage source snippet: {page_source[:500]}")
                    else:
                        pytest.fail(f"Login did not redirect. Still on login page: {current_url}.\nNo error message found. Check if credentials are correct and server is responding.\nPage source snippet: {page_source[:500]}")
                except:
                    pytest.fail(f"Login did not redirect. Still on login page: {current_url}.\nNo error message found. Check if credentials are correct and server is responding.\nPage source snippet: {page_source[:500]}")
            else:
                pytest.fail(f"Login did not redirect as expected. Current URL: {current_url}.\nPage may contain errors.\nPage source snippet: {page_source[:500]}")

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
    # Before test: Ensure driver session is valid
    try:
        # Check if driver session is still valid
        driver.current_url  # This will raise InvalidSessionIdException if session is invalid
    except Exception as e:
        # Driver might not be initialized yet, or session is invalid
        # This is fine - the test will handle driver initialization
        if "InvalidSessionIdException" not in str(type(e).__name__):
            # Only log if it's not a session error (which is expected sometimes)
            pass
    
    yield
    
    # After test: Clean up
    # Clean up: dismiss any alerts that might be left from the test
    try:
        # Check if driver session is still valid before accessing
        driver.current_url  # This will raise InvalidSessionIdException if session is invalid
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        print(f"⚠ Dismissed alert after test: {alert_text}")
    except Exception as e:
        # No alert present or session invalid, which is fine
        if "InvalidSessionIdException" not in str(type(e).__name__):
            pass
    
    # Clean up any custom attributes added during tests
    try:
        if hasattr(driver, '_booking_alert_text'):
            delattr(driver, '_booking_alert_text')
    except:
        pass
    
    # After test cleanup (driver state is managed by logged_in_driver fixture)
    pass