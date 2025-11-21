"""
Selenium tests for Carousel Management functionality.

Tests cover:
- Creating new carousel slides
- Editing existing slides
- Deleting slides
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from helpers import (
    wait_for_element,
    wait_for_clickable,
    safe_click,
    safe_send_keys,
    wait_for_page_load,
)
from conftest import BASE_URL
import time


class TestCarouselManagement:
    """Test suite for carousel management features."""
    
    def test_create_new_slide(self, logged_in_driver):
        """Test 1: Test if admin can create a new carousel slide.
        
        Steps:
        1. Login as admin and go to /adminportal
        2. Click on "Content Management" tab
        3. Click on "Carousel" tab (should be active by default)
        4. Switch to iframe containing carousel management
        5. Fill in form fields:
           - Title: "Selenium Test Slide"
           - Description: "This is for testing creating slide in the carousel"
           - Button Text: "Take assessment quiz"
           - Button URL: https://coachshante.com/intro
        6. Choose Image Source: Upload Image
        7. Click on "choose File" and upload selenium-test.jpeg from /tests folder
        8. Click on "Add New Slide" button
        9. Verify the new slide appears in the review area (table)
        """
        driver = logged_in_driver
        
        # Step 1: Navigate to adminportal
        driver.get(f"{BASE_URL}/adminportal")
        wait_for_page_load(driver)
        time.sleep(2)
        
        # Step 2: Click on "Content Management" link
        content_mgmt_link = wait_for_clickable(
            driver,
            By.XPATH,
            "//a[contains(text(), 'Content Management')]"
        )
        if not content_mgmt_link:
            # Try alternative selector
            content_mgmt_link = wait_for_clickable(
                driver,
                By.CSS_SELECTOR,
                "a[href='/content-management']"
            )
        
        assert content_mgmt_link is not None, "Content Management link not found"
        content_mgmt_link.click()
        wait_for_page_load(driver)
        time.sleep(2)
        
        # Step 3: Click on "Carousel" tab (should be active by default, but click to ensure)
        carousel_tab = wait_for_clickable(
            driver,
            By.CSS_SELECTOR,
            "button.tab[data-target='panel-carousel']"
        )
        assert carousel_tab is not None, "Carousel tab not found"
        carousel_tab.click()
        time.sleep(2)  # Wait for tab to activate and iframe to load
        
        # Step 4: Switch to iframe containing carousel management
        # First, navigate directly to carousel management to ensure fresh CSRF token
        # This helps maintain session and CSRF token validity
        driver.get(f"{BASE_URL}/adminportal/carouselmanagement")
        wait_for_page_load(driver)
        time.sleep(2)  # Wait for page to fully load with CSRF token
        
        # Verify CSRF token is present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "_csrf"))
            )
            csrf_input = driver.find_element(By.NAME, "_csrf")
            csrf_value = csrf_input.get_attribute("value")
            assert csrf_value, "CSRF token is empty"
            print(f"✓ CSRF token found: {csrf_value[:20]}...")
        except TimeoutException:
            pytest.fail("CSRF token not found on carousel management page")
        
        # Now navigate back to content-management and switch to iframe
        driver.get(f"{BASE_URL}/content-management")
        wait_for_page_load(driver)
        time.sleep(2)
        
        # Click on Carousel tab
        carousel_tab = wait_for_clickable(
            driver,
            By.CSS_SELECTOR,
            "button.tab[data-target='panel-carousel']"
        )
        assert carousel_tab is not None, "Carousel tab not found"
        carousel_tab.click()
        time.sleep(3)  # Wait for tab to activate and iframe to load
        
        # Switch to iframe
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='Carousel Manager']"))
            )
            driver.switch_to.frame(iframe)
            print("✓ Switched to carousel management iframe")
        except TimeoutException:
            pytest.fail("Carousel management iframe not found")
        
        # Wait for form to be visible in iframe and verify CSRF token
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "title"))
            )
            # Wait for CSRF token to be present in the iframe
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "_csrf"))
            )
            # Verify CSRF token has a value
            csrf_input = driver.find_element(By.NAME, "_csrf")
            csrf_value = csrf_input.get_attribute("value")
            assert csrf_value, "CSRF token in iframe is empty"
            print(f"✓ CSRF token in iframe: {csrf_value[:20]}...")
            time.sleep(1)  # Additional wait to ensure CSRF token is fully loaded
        except TimeoutException:
            pytest.fail("Carousel form or CSRF token not found in iframe")
        
        # Step 5: Fill in form fields
        # Title
        title_input = wait_for_element(driver, By.ID, "title")
        assert title_input is not None, "Title input not found"
        title_input.clear()
        title_input.send_keys("Selenium Test Slide")
        time.sleep(0.5)
        
        # Description
        description_input = wait_for_element(driver, By.ID, "description")
        assert description_input is not None, "Description input not found"
        description_input.clear()
        description_input.send_keys("This is for testing creating slide in the carousel")
        time.sleep(0.5)
        
        # Button Text
        button_text_input = wait_for_element(driver, By.ID, "buttonText")
        assert button_text_input is not None, "Button Text input not found"
        button_text_input.clear()
        button_text_input.send_keys("Take assessment quiz")
        time.sleep(0.5)
        
        # Button URL
        button_url_input = wait_for_element(driver, By.ID, "buttonUrl")
        assert button_url_input is not None, "Button URL input not found"
        button_url_input.clear()
        button_url_input.send_keys("https://coachshante.com/intro")
        time.sleep(0.5)
        
        # Step 6: Choose Image Source: Upload Image (should be selected by default)
        upload_radio = wait_for_element(driver, By.CSS_SELECTOR, "input[type='radio'][name='imageOption'][value='upload']")
        assert upload_radio is not None, "Upload Image radio button not found"
        if not upload_radio.is_selected():
            upload_radio.click()
            time.sleep(0.5)
        
        # Step 7: Click on "choose File" and upload image
        # Get the absolute path to the test image
        test_image_path = os.path.join(os.path.dirname(__file__), "selenium-test.jpeg")
        test_image_absolute = os.path.abspath(test_image_path)
        
        assert os.path.exists(test_image_absolute), f"Test image not found at {test_image_absolute}"
        
        image_upload_input = wait_for_element(driver, By.ID, "imageUpload")
        assert image_upload_input is not None, "Image upload input not found"
        
        # Send the file path to the file input
        image_upload_input.send_keys(test_image_absolute)
        print(f"✓ Uploaded image: {test_image_absolute}")
        time.sleep(1)
        
        # Step 8: Click on "Add New Slide" button
        add_slide_button = wait_for_clickable(
            driver,
            By.CSS_SELECTOR,
            "form[action*='/carousel/create'] button[type='submit']"
        )
        if not add_slide_button:
            # Try alternative selector
            add_slide_button = wait_for_clickable(
                driver,
                By.XPATH,
                "//button[contains(text(), 'Add New Slide')]"
            )
        
        assert add_slide_button is not None, "Add New Slide button not found"
        
        # Scroll button into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_slide_button)
        time.sleep(0.5)
        
        print("Clicking Add New Slide button...")
        add_slide_button.click()
        time.sleep(3)  # Wait for form submission and page reload
        
        # Step 9: Verify the new slide appears in the review area (table)
        # Wait for table to load/update
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
        except TimeoutException:
            pytest.fail("Slides table not found after creating slide")
        
        time.sleep(2)  # Additional wait for table to update
        
        # Check if the new slide appears in the table
        table = driver.find_element(By.TAG_NAME, "table")
        table_text = table.text
        
        assert "Selenium Test Slide" in table_text, (
            f"New slide 'Selenium Test Slide' not found in table. Table content: {table_text[:200]}"
        )
        
        print("✓ New slide 'Selenium Test Slide' found in the table")
        
        # Switch back to default content
        driver.switch_to.default_content()
        print("✓ Test completed: New slide created successfully")
    
    def test_edit_slide(self, logged_in_driver):
        """Test 2: Test if admin can edit a carousel slide.
        
        Steps:
        1. Navigate to Content Management -> Carousel tab
        2. Switch to iframe
        3. In the preview area (table), find the first slide
        4. Click on "Edit" button in Actions column
        5. In Edit Slide window, delete current title and change it to "Selenium test edit slide"
        6. Click on "Update Slide" button
        7. Verify the slide was updated
        """
        driver = logged_in_driver
        
        # Step 1: Navigate directly to carousel management first to ensure fresh CSRF token
        driver.get(f"{BASE_URL}/adminportal/carouselmanagement")
        wait_for_page_load(driver)
        time.sleep(2)
        
        # Verify CSRF token is present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "_csrf"))
            )
            csrf_input = driver.find_element(By.NAME, "_csrf")
            csrf_value = csrf_input.get_attribute("value")
            assert csrf_value, "CSRF token is empty"
            print(f"✓ CSRF token found: {csrf_value[:20]}...")
        except TimeoutException:
            pytest.fail("CSRF token not found on carousel management page")
        
        # Now navigate to Content Management -> Carousel
        driver.get(f"{BASE_URL}/content-management")
        wait_for_page_load(driver)
        time.sleep(2)
        
        # Click on Carousel tab
        carousel_tab = wait_for_clickable(
            driver,
            By.CSS_SELECTOR,
            "button.tab[data-target='panel-carousel']"
        )
        assert carousel_tab is not None, "Carousel tab not found"
        carousel_tab.click()
        time.sleep(3)  # Wait for tab to activate and iframe to load
        
        # Step 2: Switch to iframe
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='Carousel Manager']"))
            )
            driver.switch_to.frame(iframe)
            print("✓ Switched to carousel management iframe")
        except TimeoutException:
            pytest.fail("Carousel management iframe not found")
        
        # Wait for table to be visible and verify CSRF tokens
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            # Wait for CSRF tokens in edit/delete forms to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "_csrf"))
            )
            # Verify CSRF token has a value
            csrf_inputs = driver.find_elements(By.NAME, "_csrf")
            assert len(csrf_inputs) > 0, "No CSRF tokens found in forms"
            for csrf_input in csrf_inputs:
                csrf_value = csrf_input.get_attribute("value")
                assert csrf_value, "CSRF token in form is empty"
            print(f"✓ Found {len(csrf_inputs)} CSRF token(s) in iframe forms")
            time.sleep(1)  # Additional wait to ensure CSRF tokens are loaded
        except TimeoutException:
            pytest.fail("Slides table or CSRF tokens not found")
        
        # Step 3: Find the first slide's Edit button
        # The Edit button is in a form within the Actions column
        edit_buttons = driver.find_elements(
            By.XPATH,
            "//form[contains(@action, '/edit')]//button[contains(text(), 'Edit') or contains(text(), '🖊️')]"
        )
        
        if not edit_buttons:
            # Try alternative selector
            edit_buttons = driver.find_elements(
                By.CSS_SELECTOR,
                "form[action*='/edit'] button[type='submit']"
            )
        
        if not edit_buttons:
            pytest.skip("No slides found to edit")
        
        # Get the first slide's title before editing (for verification)
        first_row = edit_buttons[0].find_element(By.XPATH, "./ancestor::tr")
        original_title_cell = first_row.find_elements(By.TAG_NAME, "td")[1]  # Title is in second column
        original_title = original_title_cell.text.strip()
        print(f"Original slide title: {original_title}")
        
        # Step 4: Click on Edit button
        edit_button = edit_buttons[0]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_button)
        time.sleep(0.5)
        
        print("Clicking Edit button...")
        edit_button.click()
        time.sleep(3)  # Wait for edit page to load in iframe
        
        # After clicking Edit, the iframe should navigate to the edit page
        # Wait for the edit form to appear in the iframe (we're still in iframe context)
        edit_form_found = False
        
        # Wait for edit form to be visible in iframe - try multiple approaches
        try:
            # Try waiting for the title input in the iframe
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "title"))
            )
            edit_form_found = True
            print("✓ Edit form title input found in iframe")
        except TimeoutException:
            pass
        
        if not edit_form_found:
            # Try waiting for h2 with "Edit Slide" text
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Edit Slide')]"))
                )
                edit_form_found = True
                print("✓ Edit Slide heading found in iframe")
            except TimeoutException:
                pass
        
        if not edit_form_found:
            # Check what's actually in the iframe
            try:
                # Try to find any form elements
                forms = driver.find_elements(By.TAG_NAME, "form")
                if forms:
                    print(f"⚠ Found {len(forms)} form(s) but title input not found")
                    # Try to get page source snippet for debugging
                    page_text = driver.page_source[:500]
                    print(f"Page content snippet: {page_text}")
                
                # Also check if we're still showing the table (edit didn't work)
                table = driver.find_elements(By.TAG_NAME, "table")
                if table:
                    print("⚠ Still showing table after clicking Edit - edit form didn't load")
            except Exception as e:
                print(f"⚠ Error checking page content: {e}")
            
            # Switch to default content to check parent URL
            driver.switch_to.default_content()
            current_url = driver.current_url
            driver.switch_to.frame(iframe)  # Switch back to iframe for context
            pytest.fail(f"Edit slide form not found in iframe. Parent URL: {current_url}")
        
        # Also wait for the form to be fully loaded with CSRF token
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "_csrf"))
            )
            print("✓ CSRF token found in edit form")
        except TimeoutException:
            print("⚠ CSRF token not found in edit form, but continuing...")
        
        # Step 5: Delete current title and change it
        title_input = wait_for_element(driver, By.ID, "title")
        assert title_input is not None, "Title input not found in edit form"
        
        # Clear and set new title
        title_input.clear()
        time.sleep(0.3)
        title_input.send_keys("Selenium test edit slide")
        print("✓ Updated title to 'Selenium test edit slide'")
        time.sleep(0.5)
        
        # Step 6: Click on "Update Slide" button
        update_button = wait_for_clickable(
            driver,
            By.CSS_SELECTOR,
            "form[action*='/update'] button[type='submit']"
        )
        if not update_button:
            # Try alternative selector
            update_button = wait_for_clickable(
                driver,
                By.XPATH,
                "//button[contains(text(), 'Update Slide')]"
            )
        
        assert update_button is not None, "Update Slide button not found"
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", update_button)
        time.sleep(0.5)
        
        print("Clicking Update Slide button...")
        update_button.click()
        time.sleep(3)  # Wait for update to process and redirect
        
        # Step 7: Verify the slide was updated
        # Should redirect back to carousel management page
        # Navigate back to carousel management to verify
        driver.get(f"{BASE_URL}/content-management")
        wait_for_page_load(driver)
        time.sleep(2)
        
        carousel_tab = wait_for_clickable(
            driver,
            By.CSS_SELECTOR,
            "button.tab[data-target='panel-carousel']"
        )
        carousel_tab.click()
        time.sleep(2)
        
        # Switch to iframe again
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='Carousel Manager']"))
        )
        driver.switch_to.frame(iframe)
        time.sleep(2)
        
        # Check if updated title appears in table
        table = driver.find_element(By.TAG_NAME, "table")
        table_text = table.text
        
        assert "Selenium test edit slide" in table_text, (
            f"Updated slide title 'Selenium test edit slide' not found in table. Table content: {table_text[:200]}"
        )
        
        print("✓ Slide title updated successfully")
        
        # Switch back to default content
        driver.switch_to.default_content()
        print("✓ Test completed: Slide edited successfully")
    
    ######################################### Test delete slide is already passed ##############################################
    def test_delete_slide(self, logged_in_driver):
        """Test 3: Test if admin can delete a carousel slide.
        
        Steps:
        1. Navigate to Content Management -> Carousel tab
        2. Switch to iframe
        3. In Carousel Management window, under preview area (table)
        4. Find the first slide's Delete button in Actions column
        5. Click on Delete button
        6. Confirm deletion (handle confirmation dialog)
        7. Verify the slide was deleted
        """
        driver = logged_in_driver
        
        # Step 1: Navigate directly to carousel management first to ensure fresh CSRF token
        driver.get(f"{BASE_URL}/adminportal/carouselmanagement")
        wait_for_page_load(driver)
        time.sleep(2)
        
        # Verify CSRF token is present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "_csrf"))
            )
            csrf_input = driver.find_element(By.NAME, "_csrf")
            csrf_value = csrf_input.get_attribute("value")
            assert csrf_value, "CSRF token is empty"
            print(f"✓ CSRF token found: {csrf_value[:20]}...")
        except TimeoutException:
            pytest.fail("CSRF token not found on carousel management page")
        
        # Now navigate to Content Management -> Carousel
        driver.get(f"{BASE_URL}/content-management")
        wait_for_page_load(driver)
        time.sleep(2)
        
        # Click on Carousel tab
        carousel_tab = wait_for_clickable(
            driver,
            By.CSS_SELECTOR,
            "button.tab[data-target='panel-carousel']"
        )
        assert carousel_tab is not None, "Carousel tab not found"
        carousel_tab.click()
        time.sleep(3)  # Wait for tab to activate and iframe to load
        
        # Step 2: Switch to iframe
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='Carousel Manager']"))
            )
            driver.switch_to.frame(iframe)
            print("✓ Switched to carousel management iframe")
        except TimeoutException:
            pytest.fail("Carousel management iframe not found")
        
        # Wait for table to be visible and verify CSRF tokens
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            # Wait for CSRF tokens in delete forms to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "_csrf"))
            )
            # Verify CSRF token has a value
            csrf_inputs = driver.find_elements(By.NAME, "_csrf")
            assert len(csrf_inputs) > 0, "No CSRF tokens found in forms"
            for csrf_input in csrf_inputs:
                csrf_value = csrf_input.get_attribute("value")
                assert csrf_value, "CSRF token in form is empty"
            print(f"✓ Found {len(csrf_inputs)} CSRF token(s) in iframe forms")
            time.sleep(1)  # Additional wait to ensure CSRF tokens are loaded
        except TimeoutException:
            pytest.fail("Slides table or CSRF tokens not found")
        
        # Get count of slides before deletion
        table_rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        slides_count_before = len(table_rows)
        
        if slides_count_before == 0:
            pytest.skip("No slides found to delete")
        
        print(f"Found {slides_count_before} slide(s) before deletion")
        
        # Get the first slide's title for verification
        first_row = table_rows[0]
        title_cell = first_row.find_elements(By.TAG_NAME, "td")[1]
        slide_title = title_cell.text.strip()
        print(f"Deleting slide: {slide_title}")
        
        # Step 3 & 4: Find and click Delete button
        delete_buttons = driver.find_elements(
            By.XPATH,
            "//form[contains(@action, '/delete')]//button[contains(text(), 'Delete') or contains(text(), '🗑️')]"
        )
        
        if not delete_buttons:
            # Try alternative selector
            delete_buttons = driver.find_elements(
                By.CSS_SELECTOR,
                "form[action*='/delete'] button[type='submit']"
            )
        
        if not delete_buttons:
            pytest.fail("Delete button not found")
        
        delete_button = delete_buttons[0]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_button)
        time.sleep(0.5)
        
        # Step 5: Handle confirmation dialog
        # Override confirm dialog to auto-accept
        driver.execute_script("window.confirm = function() { return true; };")
        
        print("Clicking Delete button...")
        delete_button.click()
        time.sleep(3)  # Wait for deletion to process and page to reload
        
        # Handle any alert that might appear
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            print(f"✓ Handled alert: {alert_text}")
        except:
            pass
        
        # Step 6: Verify the slide was deleted
        # Wait for table to update
        time.sleep(2)
        
        # Get count of slides after deletion
        table_rows_after = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        slides_count_after = len(table_rows_after)
        
        # The count should decrease by 1
        assert slides_count_after < slides_count_before, (
            f"Slide count did not decrease. Before: {slides_count_before}, After: {slides_count_after}"
        )
        
        # Verify the deleted slide title is no longer in the table
        table = driver.find_element(By.TAG_NAME, "table")
        table_text = table.text
        
        assert slide_title not in table_text, (
            f"Deleted slide '{slide_title}' still appears in table"
        )
        
        print(f"✓ Slide '{slide_title}' deleted successfully. Count: {slides_count_before} -> {slides_count_after}")
        
        # Switch back to default content
        driver.switch_to.default_content()
        print("✓ Test completed: Slide deleted successfully")

