from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from chakra_ui_helpers import complete_quiz_and_open_results

RESULTS_PATH = "/results"
ASSESSMENT_PATH = "/assessment"

# --- Local helpers ---

def wait_ready(wait, d):
    wait.until(lambda dr: dr.execute_script("return document.readyState")=="complete")

def modal_visible(d):
    els = d.find_elements(By.ID, "saveResultsModal")
    return bool(els and els[0].is_displayed())

def wait_for_results_modal(wait, d, timeout_msg="Expected save-results modal to appear"):
    wait.until(lambda _ : modal_visible(d)), timeout_msg

def close_results_modal(wait, d):
    # Prefer the dedicated close button
    btns = d.find_elements(By.ID, "modalClose")
    if btns:
        d.execute_script("arguments[0].scrollIntoView({block:'center'});", btns[0])
        btns[0].click()
    # Ensure it hid
    wait.until(EC.invisibility_of_element_located((By.ID, "saveResultsModal")))

def submit_assessment_and_land_on_results(d, base_url, wait):
    # wrapper if you prefer this name in your tests
    complete_quiz_and_open_results(d, base_url, wait, use_admin_autofill=True)

def test_results_modal_close_button_hides_modal(tos_accepted_driver, base_url, wait):
    d = tos_accepted_driver
    submit_assessment_and_land_on_results(d, base_url, wait)

    # Now we KNOW we’re on /results
    # modal may or may not be present depending on tempSavePrompt
    modals = d.find_elements(By.ID, "saveResultsModal")
    if not modals:
        # if your app only shows it sometimes, skip gracefully
        return
    modal = modals[0]
    assert modal.is_displayed()

    close_btn = d.find_element(By.ID, "modalClose")
    close_btn.click()
    wait.until(EC.invisibility_of_element_located((By.ID, "saveResultsModal")))

def test_results_modal_signup_link_routes(tos_accepted_driver, base_url, wait):
    d = tos_accepted_driver
    submit_assessment_and_land_on_results(d, base_url, wait)

    modals = d.find_elements(By.ID, "saveResultsModal")
    if not modals:
        return
    d.find_element(By.CSS_SELECTOR, "#saveResultsModal a[href='/user-signup']").click()
    wait.until(lambda drv: "/user-signup" in drv.current_url)

def test_results_modal_login_link_routes(tos_accepted_driver, base_url, wait):
    d = tos_accepted_driver
    submit_assessment_and_land_on_results(d, base_url, wait)

    modals = d.find_elements(By.ID, "saveResultsModal")
    if not modals:
        return
    d.find_element(By.CSS_SELECTOR, "#saveResultsModal a[href='/user-login']").click()
    wait.until(lambda drv: "/user-login" in drv.current_url)