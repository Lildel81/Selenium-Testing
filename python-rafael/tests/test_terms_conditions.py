import logging, os, tempfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

log = logging.getLogger(__name__)

def _dump_page(driver, name="page"):
    tmp = tempfile.gettempdir()
    html_path = os.path.join(tmp, f"{name}.html")
    png_path  = os.path.join(tmp, f"{name}.png")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.save_screenshot(png_path)
    log.error("Saved HTML -> %s", html_path)
    log.error("Saved PNG  -> %s", png_path)

def test_terms_modal_routes_correctly(driver, base_url, wait):
    # 1) Open intro page
    url = base_url + "/intro"
    log.info("Opening %s", url)
    driver.get(url)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    # 2) Open modal
    wait.until(EC.element_to_be_clickable((By.ID, "start-assessment-btn"))).click()
    modal = driver.find_element(By.ID, "terms-modal")
    wait.until(lambda d: modal.is_displayed())

    # 3) Enable checkbox (scroll to bottom) and click it
    checkbox = driver.find_element(By.ID, "terms-checkbox")
    continue_btn = driver.find_element(By.ID, "continue-btn")
    terms_scroll = driver.find_element(By.ID, "terms-scroll")
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", terms_scroll)
    wait.until(lambda d: not checkbox.get_attribute("disabled"))
    checkbox.click()
    wait.until(lambda d: continue_btn.is_enabled())

    # 4) Click Continue and verify navigation
    before_handles = set(driver.window_handles)
    continue_btn.click()

    # First try same-tab navigation:
    try:
        wait.until(EC.url_contains("/assessment"))
        assert "/assessment" in driver.current_url, (
            f"Expected to be on '{"/assessment"}', but got '{driver.current_url}'"
        )
        log.info("Routed correctly to %s", driver.current_url)
        return
    except Exception:
        # If same-tab check failed, see if a new tab opened and switch to it.
        after_handles = set(driver.window_handles)
        new_handles = list(after_handles - before_handles)
        if new_handles:
            driver.switch_to.window(new_handles[0])
            try:
                wait.until(EC.url_contains("/assessment"))
                assert "/assessment" in driver.current_url, (
                    f"Expected to be on '{"/assessment"}', but got '{driver.current_url}'"
                )
                log.info("Routed correctly (new tab) to %s", driver.current_url)
                return
            except Exception:
                _dump_page(driver, "route_new_tab_failure")
                raise

        # Neither same-tab nor new-tab matched — dump for debugging and fail.
        _dump_page(driver, "route_failure")
        raise AssertionError(
            f"Did not navigate to expected path '{"/assessment"}'. "
            f"Current URL: {driver.current_url}"
        )
