from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def test_admin_stats_buttons(admin_login, base_url, wait):
    """
    Runs against the actual /adminportal page to verify that
    the Chakra Assessment Statistics controls work in production.
    """
    d = admin_login   # fixture that logs in as admin
    d.get(base_url.rstrip("/") + "/adminportal")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".stats-dashboard-section")))

    # Grab controls
    month  = d.find_element(By.ID, "statsMonthPicker")
    clear  = d.find_element(By.ID, "clearMonthBtn")
    refresh= d.find_element(By.ID, "refreshStatsBtn")
    label  = d.find_element(By.ID, "filterLabel")
    badge  = d.find_element(By.ID, "submissionCountBadge")

    # --- Refresh without month ---
    refresh.click()
    wait.until(lambda drv: drv.find_element(By.ID, "statsLoadingMessage").is_displayed())
    wait.until(lambda drv: not drv.find_element(By.ID, "statsLoadingMessage").is_displayed())
    assert "submissions" in badge.text.lower()

    # --- Apply month filter ---
    month.send_keys("2025-10")
    wait.until(lambda drv: "Oct" in drv.find_element(By.ID, "filterLabel").text or
                         "2025" in drv.find_element(By.ID, "filterLabel").text)

    refresh.click()
    wait.until(lambda drv: drv.find_element(By.ID, "statsLoadingMessage").is_displayed())
    wait.until(lambda drv: not drv.find_element(By.ID, "statsLoadingMessage").is_displayed())
    assert "submissions" in badge.text.lower()

    # --- Clear month ---
    clear.click()
    wait.until(lambda drv: drv.find_element(By.ID, "filterLabel").text.strip() == "All time")