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
from webdriver_manager.chrome import ChromeDriverManager        # Automatically downloads & manages correct ChromeDriver version
from dotenv import load_dotenv                                  # Loads var from .env file into os.getenv()

# Load environment variables
load_dotenv()

# Base URL for the app
BASE_URL = os.getenv("TEST_BASE_URL", "https://example.com")

@pytest.fixture(scope="session")
def base_url():
    # Provide BASE_URL to tests
    return BASE_URL

# Admin credentials (setup in .env)
ADMIN_USERNAME = os.getenv("TEST_ADMIN_USERNAME", "example")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "example")

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
    yield
    # We can add more clean up logic after this