import time
import contextlib
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException

ASSESSMENT_PATH = "/assessment"

# ---------------- Core waits / state ----------------
def wait_ready(wait, driver):
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")


def active_section(driver):
    return driver.find_element(By.CSS_SELECTOR, ".chakra-section.active")


def active_section_id(driver):
    return active_section(driver).get_attribute("id")


def _active(d):
    return d.find_element(By.CSS_SELECTOR, ".chakra-section.active")


# ---------------- Modal helpers ----------------
def modal_visible(driver) -> bool:
    # re-query each time to avoid staleness
    els = driver.find_elements(By.ID, "validationModal")
    return bool(els and els[0].is_displayed())


def wait_for_modal(wait, driver):
    wait.until(lambda d: modal_visible(d))


def close_modal(wait, driver):
    """Close via 'OK' then 'X' if needed, then wait until hidden."""
    for sel in ("#validationModal .validation-modal-btn",
                "#validationModal .validation-modal-close"):
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        if els:
            els[0].click()
            break
    wait.until(EC.invisibility_of_element_located((By.ID, "validationModal")))


# ---------------- Click helpers ----------------

def safe_click_input(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        label = el.find_element(By.XPATH, "ancestor::label")
    except Exception:
        label = None
    target = label or el
    try:
        target.click()
    except ElementClickInterceptedException:
        try:
            ActionChains(driver).move_to_element(target).pause(0.05).click().perform()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", target)
    t = (el.get_attribute("type") or "").lower()
    if t in ("radio", "checkbox"):
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", el)


def safe_click_button(wait, driver, css_selector):
    """Scroll, wait clickable, click; handles modal if it pops."""
    # Close modal if already visible
    if modal_visible(driver):
        close_modal(wait, driver)

    btn = driver.find_element(By.CSS_SELECTOR, css_selector)
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

    try:
        btn.click()
    except ElementClickInterceptedException:
        # If modal raced in, close and retry once
        wait_for_modal(wait, driver)
        close_modal(wait, driver)
        btn = driver.find_element(By.CSS_SELECTOR, css_selector)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        btn.click()


def safe_click_next(wait, driver):
    safe_click_button(wait, driver, ".chakra-section.active .next-btn")


# ---------------- Filling helpers ----------------
def minimal_fill_first_section(driver):
    """A concise, deterministic fill for the first section."""
    section = active_section(driver)
    section.find_element(By.ID, "fullName").send_keys("Rafael Tester")
    section.find_element(By.ID, "email").send_keys("rafael@example.com")
    section.find_element(By.ID, "contactNumber").send_keys("555-555-1234")

    safe_click_input(driver, section.find_element(By.CSS_SELECTOR, "input[name='ageBracket'][value='20-30']"))
    safe_click_input(driver, section.find_element(By.CSS_SELECTOR, "input[name='healthcareWorker'][value='no']"))

    section.find_element(By.ID, "jobTitle").send_keys("QA Engineer")
    safe_click_input(driver, section.find_element(By.CSS_SELECTOR, "input[name='experience'][value='no']"))

    safe_click_input(driver, section.find_element(By.CSS_SELECTOR, "#familiarWithFieldset input[type='checkbox']:not(#noneCheckbox)"))
    safe_click_input(driver, section.find_element(By.CSS_SELECTOR, "input[name='challenges[]'][value='physical']"))

    section.find_element(By.ID, "goals").send_keys("Improve sleep and energy.")


def fill_required_in_active_section(driver):
    """
    Fill just enough in the active section to satisfy your JS validation:
      - all enabled required inputs (text/email/tel/number/textarea)
      - at least one option for each required radio group
      - at least one option for each required checkbox group
      - conditional companions (experienceOtherText, challengeOtherText, healthcareYears)
    """
    section = active_section(driver)

    # 1) required text/email/tel/number/textarea (skip disabled)
    for el in section.find_elements(By.CSS_SELECTOR, "input[required]:not([type='radio']):not([type='checkbox']), textarea[required]"):
        if not el.is_enabled():
            continue
        t = (el.get_attribute("type") or "").lower()
        el.clear()
        if t == "email":
            el.send_keys("test@example.com")
        elif t == "tel":
            el.send_keys("555-555-1234")
        elif t == "number":
            el.send_keys("1")
        else:
            el.send_keys("ok")

    # 2) required radio groups (any group with at least one [required])
    radios = section.find_elements(By.CSS_SELECTOR, "input[type='radio'][name]")
    by_name = {}
    for r in radios:
        by_name.setdefault(r.get_attribute("name"), []).append(r)

    for name, group in by_name.items():
        has_required = any(r.get_attribute("required") is not None for r in group)
        if has_required and not any(r.is_selected() for r in group):
            for r in group:
                if r.is_enabled() and r.is_displayed():
                    safe_click_input(driver, r)
                    break

    # 3) required checkbox groups (legend contains '*')
    for fs in section.find_elements(By.CSS_SELECTOR, "fieldset"):
        legend = None
        with contextlib.suppress(Exception):
            legend = fs.find_element(By.TAG_NAME, "legend")
        if legend and "*" in (legend.text or ""):
            boxes = [b for b in fs.find_elements(By.CSS_SELECTOR, "input[type='checkbox']") if b.is_enabled() and b.is_displayed()]
            if boxes and not any(b.is_selected() for b in boxes):
                non_none = [b for b in boxes if b.get_attribute("id") != "noneCheckbox"]
                safe_click_input(driver, (non_none or boxes)[0])

    # 4) conditionals expected by your JS
    with contextlib.suppress(Exception):
        if section.find_element(By.ID, "experienceOther").is_selected():
            txt = section.find_element(By.ID, "experienceOtherText")
            if txt.is_enabled():
                txt.clear(); txt.send_keys("Other")
    with contextlib.suppress(Exception):
        chk = section.find_element(By.ID, "challengesOther")
        if chk.is_selected():
            txt = section.find_element(By.ID, "challengeOtherText")
            if txt.is_enabled():
                txt.clear(); txt.send_keys("Other")
    with contextlib.suppress(Exception):
        yes = section.find_element(By.CSS_SELECTOR, "input[name='healthcareWorker'][value='yes']")
        if yes.is_selected():
            years = section.find_element(By.NAME, "healthcareYears")
            if years.is_enabled() and not years.get_attribute("value"):
                years.clear(); years.send_keys("1")


def advance_through_all_sections_filling_minimum(driver, wait):
    """
    From current section to the last:
      - fill minimum required each time
      - click Next if visible
    """
    while True:
        fill_required_in_active_section(driver)
        next_in_active = driver.find_elements(By.CSS_SELECTOR, ".chakra-section.active .next-btn")
        if not next_in_active or not next_in_active[0].is_displayed():
            break
        safe_click_next(wait, driver)
        time.sleep(0.05)


def force_active_section_invalid(driver):
    """
    Deterministically make the active section invalid for your JS:
      - clear required text-ish fields
      - uncheck all inputs in any required radio group
      - uncheck all inputs in any required checkbox group (legend with '*')
    """
    section = active_section(driver)
    driver.execute_script("""
      const sec = arguments[0];

      // clear all required text-ish fields (enabled only)
      sec.querySelectorAll('input[required]:not([type=radio]):not([type=checkbox]), textarea[required]')
         .forEach(el => { if (!el.disabled) el.value = ''; });

      // required radio groups: if any radio in group has [required], uncheck all in that group
      const radios = Array.from(sec.querySelectorAll('input[type=radio][name]'));
      const byName = {};
      radios.forEach(r => (byName[r.name] = byName[r.name] || []).push(r));
      Object.values(byName).forEach(group => {
        const hasReq = group.some(r => r.hasAttribute('required'));
        if (hasReq) {
          group.forEach(r => {
            r.checked = false;
            r.dispatchEvent(new Event('change', {bubbles:true}));
          });
        }
      });

      // required checkbox groups: legend with '*'
      sec.querySelectorAll('fieldset').forEach(fs => {
        const legend = fs.querySelector('legend');
        if (legend && legend.textContent.includes('*')) {
          fs.querySelectorAll('input[type=checkbox]').forEach(cb => {
            cb.checked = false;
            cb.dispatchEvent(new Event('change', {bubbles:true}));
          });
        }
      });
    """, section)


# --------------- Tests -------------------

def test_assessment_requires_tos(driver, base_url, wait):
    """Without TOS, /assessment should not be accessible (redirects to /intro)."""
    driver.get(base_url.rstrip("/") + ASSESSMENT_PATH)
    wait_ready(wait, driver)
    assert "/intro" in driver.current_url or "tos" in driver.current_url.lower()


def test_navigation_and_headers(tos_accepted_driver, base_url, wait):
    d = tos_accepted_driver
    d.get(base_url.rstrip("/") + ASSESSMENT_PATH)
    wait_ready(wait, d)

    # Start on first section
    assert active_section_id(d) == "gettingToKnowYou"
    assert d.find_element(By.ID, "chakraHeader").text.strip() == "Getting To Know You"
    assert "General questions" in d.find_element(By.ID, "chakraDescription").text

    # Click Next immediately -> expect validation modal
    safe_click_button(wait, d, ".chakra-section.active .next-btn")
    wait_for_modal(wait, d)
    close_modal(wait, d)

    # Fill minimum required and proceed to root
    minimal_fill_first_section(d)
    safe_click_button(wait, d, ".chakra-section.active .next-btn")
    wait.until(lambda _: active_section_id(d) == "rootChakra")


def test_conditional_fields_enable_disable(tos_accepted_driver, base_url, wait):
    d = tos_accepted_driver
    d.get(base_url.rstrip("/") + ASSESSMENT_PATH)
    wait_ready(wait, d)

    # Make sure we are on the first section
    assert active_section_id(d) == "gettingToKnowYou"

    sec = _active(d)

    # healthcareYears: disabled -> enable with "yes" -> disabled with "no"
    hc_years = sec.find_element(By.ID, "healthcareYears")
    assert hc_years.get_attribute("disabled") is not None

    yes_radio = sec.find_element(By.CSS_SELECTOR, "input[name='healthcareWorker'][value='yes']")
    safe_click_input(d, yes_radio)
    WebDriverWait(d, 3).until(lambda _: _active(d).find_element(By.ID, "healthcareYears").is_enabled())

    no_radio = sec.find_element(By.CSS_SELECTOR, "input[name='healthcareWorker'][value='no']")
    safe_click_input(d, no_radio)
    WebDriverWait(d, 3).until(lambda _: _active(d).find_element(By.ID, "healthcareYears").get_attribute("disabled") is not None)

    # experienceOther: enable its companion only in this first section
    exp_other_radio = sec.find_element(By.ID, "experienceOther")
    exp_other_text  = sec.find_element(By.ID, "experienceOtherText")
    assert not exp_other_text.is_enabled()

    safe_click_input(d, exp_other_radio)
    # short local wait; don’t rely on a huge global timeout
    WebDriverWait(d, 3).until(lambda _: _active(d).find_element(By.ID, "experienceOtherText").is_enabled())


def test_familiar_none_behavior(tos_accepted_driver, base_url, wait):
    d = tos_accepted_driver
    d.get(base_url.rstrip("/") + ASSESSMENT_PATH)
    wait_ready(wait, d)

    others = d.find_elements(By.CSS_SELECTOR, "#familiarWithFieldset input[type='checkbox']:not(#noneCheckbox)")
    for el in others[:2]:
        safe_click_input(d, el)
        assert el.is_selected()

    none_box = d.find_element(By.ID, "noneCheckbox")
    safe_click_input(d, none_box)
    for el in others[:2]:
        assert not el.is_selected()

    # uncheck None; others selectable again
    safe_click_input(d, none_box)
    for el in others[:2]:
        safe_click_input(d, el)
        assert el.is_selected()


def test_validation_modal_when_required_missing(tos_accepted_driver, base_url, wait):
    d = tos_accepted_driver
    d.get(base_url.rstrip("/") + ASSESSMENT_PATH)
    wait_ready(wait, d)

    # Next without filling -> modal
    safe_click_button(wait, d, ".chakra-section.active .next-btn")
    wait_for_modal(wait, d)
    assert modal_visible(d)
    close_modal(wait, d)
    assert not modal_visible(d)


def test_happy_path_first_section_then_next(tos_accepted_driver, base_url, wait):
    d = tos_accepted_driver
    d.get(base_url.rstrip("/") + ASSESSMENT_PATH)
    wait_ready(wait, d)

    minimal_fill_first_section(d)
    safe_click_button(wait, d, ".chakra-section.active .next-btn")
    wait.until(lambda _: active_section_id(d) == "rootChakra")


def test_submit_requires_all_sections(tos_accepted_driver, base_url, wait):
    """
    Fill each section that allows proceeding, then on the last section
    make the state invalid and assert the validation modal at submit.
    """
    d = tos_accepted_driver
    d.get(base_url.rstrip("/") + ASSESSMENT_PATH)
    wait_ready(wait, d)

    advance_through_all_sections_filling_minimum(d, wait)   # now at last section
    force_active_section_invalid(d)

    # submit
    safe_click_button(wait, d, ".chakra-section.active button.submit-btn")
    wait_for_modal(wait, d)      # must appear
    assert modal_visible(d)
    close_modal(wait, d)


def test_full_happy_path_submits(tos_accepted_driver, base_url, wait):
    """
    Fill every section with minimal valid data, then submit (no modal expected).
    """
    d = tos_accepted_driver
    d.get(base_url.rstrip("/") + ASSESSMENT_PATH)
    wait_ready(wait, d)

    advance_through_all_sections_filling_minimum(d, wait)
    fill_required_in_active_section(d)  # ensure final section is valid

    safe_click_button(wait, d, ".chakra-section.active button.submit-btn")
    time.sleep(0.2)
    assert not modal_visible(d)