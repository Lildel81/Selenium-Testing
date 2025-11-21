"""
Helper functions for Selenium tests.
Contains utility functions for common test operations.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


def wait_for_element(driver, by, value, timeout=10):
    """
    Wait for an element to be present on the page.
    
    Args:
        driver: WebDriver instance
        by: Selenium By locator (e.g., By.ID, By.NAME)
        value: Locator value
        timeout: Maximum time to wait in seconds
    
    Returns:
        WebElement if found, None otherwise
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None


def wait_for_clickable(driver, by, value, timeout=10):
    """
    Wait for an element to be clickable.
    
    Args:
        driver: WebDriver instance
        by: Selenium By locator
        value: Locator value
        timeout: Maximum time to wait in seconds
    
    Returns:
        WebElement if clickable, None otherwise
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        return None


def wait_for_text_in_element(driver, by, value, text, timeout=10):
    """
    Wait for specific text to appear in an element.
    
    Args:
        driver: WebDriver instance
        by: Selenium By locator
        value: Locator value
        text: Text to wait for
        timeout: Maximum time to wait in seconds
    
    Returns:
        True if text found, False otherwise
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.text_to_be_present_in_element((by, value), text)
        )
        return True
    except TimeoutException:
        return False


def extract_csrf_token(driver):
    """
    Extract CSRF token from the current page.
    
    Args:
        driver: WebDriver instance
    
    Returns:
        CSRF token string or None
    """
    try:
        element = driver.find_element(By.NAME, "_csrf")
        return element.get_attribute("value")
    except NoSuchElementException:
        return None


def safe_click(driver, by, value, timeout=10):
    """
    Safely click an element, waiting for it to be clickable.
    
    Args:
        driver: WebDriver instance
        by: Selenium By locator
        value: Locator value
        timeout: Maximum time to wait in seconds
    
    Returns:
        True if clicked successfully, False otherwise
    """
    element = wait_for_clickable(driver, by, value, timeout)
    if element:
        try:
            element.click()
            return True
        except Exception as e:
            print(f"Error clicking element: {e}")
            return False
    return False


def safe_send_keys(driver, by, value, text, clear_first=True):
    """
    Safely send keys to an input element.
    
    Args:
        driver: WebDriver instance
        by: Selenium By locator
        value: Locator value
        text: Text to send
        clear_first: Whether to clear the field first
    
    Returns:
        True if successful, False otherwise
    """
    element = wait_for_element(driver, by, value)
    if element:
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            print(f"Error sending keys: {e}")
            return False
    return False


def wait_for_url_change(driver, current_url, timeout=10):
    """
    Wait for the URL to change from the current URL.
    
    Args:
        driver: WebDriver instance
        current_url: Current URL to wait for change from
        timeout: Maximum time to wait in seconds
    
    Returns:
        True if URL changed, False otherwise
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.current_url != current_url
        )
        return True
    except TimeoutException:
        return False


def wait_for_page_load(driver, timeout=10):
    """
    Wait for page to finish loading.
    
    Args:
        driver: WebDriver instance
        timeout: Maximum time to wait in seconds
    """
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def scroll_to_element(driver, element):
    """
    Scroll to an element to make it visible.
    
    Args:
        driver: WebDriver instance
        element: WebElement to scroll to
    """
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)  # Small delay for scroll animation
