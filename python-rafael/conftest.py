"""
    Pytest configuration and fixtures for Selenium tests
    This provides shared test fixtures and configuration
"""
import pytest                                                   # Testing framework; automatically discovers and runs tests
import os                                                       # Access env var, file paths,...
import time                                                     # for sleep and timeouts
from selenium import webdriver                                  # Core Selenium Webdriver (controls the browser)
from selenium.webdriver.chrome.service import Service           # Specifies ChromeDriver executable location
from selenium.webdriver.chrome.options import Options           # configures Chrome behavior
from selenium.webdriver.support.ui import WebDriverWait         # Explicit waits (wait for conditions instead of sleep)
from selenium.webdriver.support import expected_conditions as EC# Pre-built wait conditions
from selenium.webdriver.common.by import By                     # Locators: By.ID, By.PATH, By.CSS_SELECTOR,...
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException # Exception handling
from webdriver_manager.chrome import ChromeDriverManager        # Automatically downloads & manages correct ChromeDriver version
from dotenv import load_dotenv                                  # Loads var from .env file into os.getenv()
import contextlib                                               # for suppressing exceptions

# Load environment variables
load_dotenv()

CHROMEDRIVER_VERSION = "142.0.7444.175"

# Base URL for the app
BASE_URL = os.getenv("TEST_BASE_URL")

@pytest.fixture(scope="session")
def base_url():
    # Provide BASE_URL to tests
    return BASE_URL

# Admin credentials (setup in .env)
ADMIN_USERNAME = os.getenv("TEST_ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD")

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
    service = Service(ChromeDriverManager(CHROMEDRIVER_VERSION).install())
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
    driver.get(f"{BASE_URL}/login")

    # Wait for login form to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.NAME, "username"))
    )

    # Extract CSRF token from the page
    csrf_token = driver.find_element(By.NAME, "_csrf").get_attribute("value")

    # Fill in login form
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")

    username_field.clear()
    username_field.send_keys(ADMIN_USERNAME)

    password_field.clear()
    password_field.send_keys(ADMIN_PASSWORD)

    # Submit login form
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
    login_button.click()

    # Wait for redirect after successful login
    WebDriverWait(driver, 10).until(
        lambda d: "/login" not in d.current_url
    )

    yield driver

def _safe_click(driver, wait, locator):
    el = wait.until(EC.element_to_be_clickable(locator))
    # center-scroll helps with sticky headers
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        el.click()
    except ElementClickInterceptedException:
        # Try one more time after a short pause
        time.sleep(0.05)
        try:
            driver.execute_script("arguments[0].click();", el)
        except ElementClickInterceptedException:
            # final fallback: re-find and JS click
            el = driver.find_element(*locator)
            driver.execute_script("arguments[0].click();", el)

@pytest.fixture
def admin_login(driver, wait, base_url):
    """
    Logs in as an admin and waits until /adminportal is loaded.
    Returns the same driver (now authenticated).
    """
    # Fresh session to avoid leftover cookies
    driver.delete_all_cookies()

    # Go to login page
    driver.get(base_url.rstrip("/") + "/login")

    # Some setups need a refresh once so the server sets CSRF cookie consistently
    driver.refresh()

    # Wait for CSRF input field to appear
    csrf_input = wait.until(EC.presence_of_element_located((By.NAME, "_csrf")))
    csrf_token = csrf_input.get_attribute("value")

    # Wait for CSRF cookie to exist (name _csrf in your stack)
    wait.until(lambda d: any(c['name'] == '_csrf' for c in d.get_cookies()))

    # Fill credentials
    user_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    pass_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    user_field.clear(); user_field.send_keys(ADMIN_USERNAME)
    pass_field.clear(); pass_field.send_keys(ADMIN_PASSWORD)

    # Click the submit button (your classmate’s selector)
    _safe_click(driver, wait, (By.CSS_SELECTOR, "button.login_button[type='submit']"))

    # Handle quick flashes/redirects + occasional staleness
    with contextlib.suppress(StaleElementReferenceException):
        wait.until(EC.url_contains("/adminportal"))

    # As an extra guard, if URL didn’t change yet, check once more
    if "/adminportal" not in driver.current_url:
        wait.until(EC.url_contains("/adminportal"))

    return driver
    
@pytest.fixture
def tos_accepted_driver(driver, base_url):
    """Drive /intro TOS flow so req.session.acceptedTOS = true, then return driver."""
    wait = WebDriverWait(driver, 15)
    driver.get(base_url.rstrip("/") + "/intro")
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    # Open TOS modal
    wait.until(EC.element_to_be_clickable((By.ID, "start-assessment-btn"))).click()

    # Wait until the modal is displayed (presence + displayed)
    wait.until(EC.visibility_of_element_located((By.ID, "terms-modal")))

    # Scroll to bottom -> enable checkbox
    terms_scroll = driver.find_element(By.ID, "terms-scroll")
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", terms_scroll)

    # Enable + tick checkbox
    wait.until(lambda d: not d.find_element(By.ID, "terms-checkbox").get_attribute("disabled"))
    driver.find_element(By.ID, "terms-checkbox").click()

    # Continue
    continue_btn = driver.find_element(By.ID, "continue-btn")
    wait.until(lambda d: continue_btn.is_enabled())
    before = driver.current_url
    continue_btn.click()

    # Robust wait: either URL changes OR the modal becomes invisible (both re-query)
    wait.until(
        EC.any_of(
            EC.url_changes(before),
            EC.invisibility_of_element_located((By.ID, "terms-modal")),
        )
    )
    return driver

"""
    Provides a WebDriverWait instance for explicit waits
"""
@pytest.fixture
def wait(driver):
    # 2s timeout, 50ms poll — fails fast instead of burning 10s
    return WebDriverWait(driver, 2, poll_frequency=0.05)

@pytest.fixture(autouse=True)
def no_implicit_wait(driver):
    driver.implicitly_wait(0)  # important: avoid compounding waits
    yield

"""
    Reset state before each test
    This can be customized to clean up test data if needed
"""
@pytest.fixture(autouse=True)
def reset_state(driver):
    yield
    # We can add more clean up logic after this