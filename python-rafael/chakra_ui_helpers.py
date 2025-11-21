from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

def _scroll_center(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)

def _safe_click(driver, el):
    _scroll_center(driver, el)
    try:
        el.click()
        return
    except ElementClickInterceptedException:
        pass
    try:
        ActionChains(driver).move_to_element(el).pause(0.05).click().perform()
        return
    except ElementClickInterceptedException:
        pass
    driver.execute_script("arguments[0].click();", el)

def _active_section_id(driver):
    sec = driver.find_element(By.CSS_SELECTOR, ".chakra-section.active")
    return sec.get_attribute("id")

def _modal_visible(driver):
    els = driver.find_elements(By.ID, "validationModal")
    return bool(els and els[0].is_displayed())

def _close_modal(wait, driver):
    for sel in ("#validationModal .validation-modal-btn",
                "#validationModal .validation-modal-close"):
        btns = driver.find_elements(By.CSS_SELECTOR, sel)
        if btns:
            _safe_click(driver, btns[0])
            break
    wait.until(EC.invisibility_of_element_located((By.ID, "validationModal")))

def _safe_click_next(wait, driver):
    # dismiss validation modal if it’s up
    if _modal_visible(driver):
        _close_modal(wait, driver)

    nxt = driver.find_element(By.CSS_SELECTOR, ".chakra-section.active .next-btn")
    _scroll_center(driver, nxt)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".chakra-section.active .next-btn")))
    try:
        nxt.click()
    except ElementClickInterceptedException:
        # modal may have raced in
        wait.until(lambda d: _modal_visible(d))
        _close_modal(wait, driver)
        nxt = driver.find_element(By.CSS_SELECTOR, ".chakra-section.active .next-btn")
        _scroll_center(driver, nxt)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".chakra-section.active .next-btn")))
        nxt.click()

def _fill_required_minimum_in_active_section(driver):
    section = driver.find_element(By.CSS_SELECTOR, ".chakra-section.active")

    # text-like requireds
    for el in section.find_elements(By.CSS_SELECTOR, "input[required]:not([type='radio']):not([type='checkbox']), textarea[required]"):
        if not el.is_enabled(): 
            continue
        t = (el.get_attribute("type") or "").lower()
        el.clear()
        el.send_keys({
            "email": "test@example.com",
            "tel":   "555-555-1234",
            "number":"1",
        }.get(t, "ok"))

    # radios by group
    radios = section.find_elements(By.CSS_SELECTOR, "input[type='radio'][name]")
    by_name = {}
    for r in radios:
        by_name.setdefault(r.get_attribute("name"), []).append(r)
    for group in by_name.values():
        if any(r.get_attribute("required") is not None for r in group) and not any(r.is_selected() for r in group):
            for r in group:
                if r.is_enabled() and r.is_displayed():
                    _safe_click(driver, r)
                    break

    # checkbox groups (fieldset legend with '*')
    for fs in section.find_elements(By.CSS_SELECTOR, "fieldset"):
        legend = None
        try:
            legend = fs.find_element(By.TAG_NAME, "legend")
        except Exception:
            pass
        if legend and "*" in legend.text:
            boxes = [b for b in fs.find_elements(By.CSS_SELECTOR, "input[type='checkbox']") if b.is_enabled() and b.is_displayed()]
            if boxes and not any(b.is_selected() for b in boxes):
                non_none = [b for b in boxes if b.get_attribute("id") != "noneCheckbox"]
                _safe_click(driver, (non_none or boxes)[0])

    # conditionals
    try:
        if section.find_element(By.ID, "experienceOther").is_selected():
            t = section.find_element(By.ID, "experienceOtherText")
            if t.is_enabled():
                t.clear(); t.send_keys("Other")
    except Exception:
        pass
    try:
        if section.find_element(By.ID, "challengesOther").is_selected():
            t = section.find_element(By.ID, "challengeOtherText")
            if t.is_enabled():
                t.clear(); t.send_keys("Other")
    except Exception:
        pass
    try:
        yes = section.find_element(By.CSS_SELECTOR, "input[name='healthcareWorker'][value='yes']")
        if yes.is_selected():
            yrs = section.find_element(By.NAME, "healthcareYears")
            if yrs.is_enabled() and not yrs.get_attribute("value"):
                yrs.clear(); yrs.send_keys("1")
    except Exception:
        pass

def complete_quiz_and_open_results(tos_accepted_driver, base_url, wait, use_admin_autofill=True):
    d = tos_accepted_driver

    # Go to /assessment
    d.get(base_url.rstrip("/") + "/assessment")
    wait.until(lambda drv: drv.execute_script("return document.readyState") == "complete")

    # Optional: admin autofill to speed up
    if use_admin_autofill:
        btns = d.find_elements(By.ID, "autoFillChakraBtn")
        if btns:
            _safe_click(d, btns[0])

    # Walk forward through sections
    while True:
        _fill_required_minimum_in_active_section(d)
        nxts = d.find_elements(By.CSS_SELECTOR, ".chakra-section.active .next-btn")
        if not nxts or not nxts[0].is_displayed():
            break
        _safe_click_next(wait, d)

    # Submit (final section)
    submit = d.find_element(By.CSS_SELECTOR, ".chakra-section.active button.submit-btn")
    _scroll_center(d, submit)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".chakra-section.active button.submit-btn")))
    submit.click()

    # Wait for the redirect and the unique H1 marker.
    try:
        # First, wait for URL to contain /results (with any querystring)
        wait.until(lambda drv: "/results" in drv.current_url)
    except TimeoutException:
        # If we're on the same URL but still swaps content, continue to H1 wait.
        pass

    # Now wait for the H1 to be present/visible
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//h1[contains(normalize-space(.), 'Your Chakra & Archetype Insights')]")
    ))
