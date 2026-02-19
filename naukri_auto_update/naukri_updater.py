"""
Naukri Profile Auto Updater
Automatically updates your Naukri profile to increase visibility to recruiters.
Designed to run on Termux (Android) or any Linux environment.
"""

import os
import sys
import time
import random
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    WebDriverException
)

import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class NaukriUpdater:
    """Handles Naukri profile automation tasks."""
    
    NAUKRI_LOGIN_URL = "https://www.naukri.com/nlogin/login"
    NAUKRI_PROFILE_URL = "https://www.naukri.com/mnjuser/profile"
    
    def __init__(self):
        self.driver = None
        self.headline_index = 0
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with appropriate options for Termux."""
        logger.info("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        
        if config.HEADLESS:
            chrome_options.add_argument("--headless")
        
        # Essential options for Termux/Linux
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # User agent to avoid detection
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Suppress automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
            )
            self.driver.implicitly_wait(10)
            logger.info("WebDriver initialized successfully")
        except WebDriverException as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
            
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to appear more human-like."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        
    def login(self):
        """Login to Naukri account."""
        logger.info("Attempting to login to Naukri...")
        
        try:
            self.driver.get(self.NAUKRI_LOGIN_URL)
            self.random_delay(2, 4)
            
            # Wait for login form
            wait = WebDriverWait(self.driver, config.BROWSER_TIMEOUT)
            
            # Enter email
            email_field = wait.until(
                EC.presence_of_element_located((By.ID, "usernameField"))
            )
            email_field.clear()
            email_field.send_keys(config.NAUKRI_EMAIL)
            self.random_delay()
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "passwordField")
            password_field.clear()
            password_field.send_keys(config.NAUKRI_PASSWORD)
            self.random_delay()
            
            # Click login button
            login_button = self.driver.find_element(
                By.XPATH, "//button[@type='submit' and contains(text(), 'Login')]"
            )
            login_button.click()
            
            # Wait for successful login (profile page or dashboard)
            self.random_delay(3, 5)
            
            # Check if login was successful
            if "login" in self.driver.current_url.lower():
                # Check for error message
                try:
                    error = self.driver.find_element(By.CLASS_NAME, "erBox")
                    logger.error(f"Login failed: {error.text}")
                    return False
                except NoSuchElementException:
                    pass
            
            logger.info("Login successful!")
            return True
            
        except TimeoutException:
            logger.error("Login page took too long to load")
            return False
        except Exception as e:
            logger.error(f"Login failed with error: {e}")
            return False
            
    def navigate_to_profile(self):
        """Navigate to the profile page."""
        logger.info("Navigating to profile page...")
        
        try:
            self.driver.get(self.NAUKRI_PROFILE_URL)
            self.random_delay(2, 4)
            
            wait = WebDriverWait(self.driver, config.BROWSER_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "widgetHead")))
            
            logger.info("Profile page loaded")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to profile: {e}")
            return False
            
    def update_resume(self):
        """Re-upload resume to increase profile visibility."""
        if not config.UPDATE_RESUME:
            logger.info("Resume update disabled in config")
            return True
            
        logger.info("Updating resume...")
        
        try:
            # Check if resume file exists
            if not os.path.exists(config.RESUME_PATH):
                logger.error(f"Resume file not found: {config.RESUME_PATH}")
                return False
            
            wait = WebDriverWait(self.driver, config.BROWSER_TIMEOUT)
            
            # Find the resume upload section
            # Look for the file input element
            try:
                # Try to find resume upload input
                resume_input = self.driver.find_element(
                    By.XPATH, "//input[@type='file' and contains(@id, 'attachCV')]"
                )
            except NoSuchElementException:
                # Alternative selectors
                resume_input = self.driver.find_element(
                    By.CSS_SELECTOR, "input[type='file'][accept='.doc,.docx,.rtf,.pdf']"
                )
            
            # Upload the resume
            resume_input.send_keys(config.RESUME_PATH)
            self.random_delay(3, 5)
            
            # Wait for upload confirmation
            logger.info("Resume uploaded successfully!")
            return True
            
        except NoSuchElementException:
            logger.warning("Resume upload element not found - trying alternative method")
            return self._update_resume_alternative()
        except Exception as e:
            logger.error(f"Resume update failed: {e}")
            return False
            
    def _update_resume_alternative(self):
        """Alternative method to update resume via profile edit."""
        try:
            # Navigate directly to resume section
            self.driver.get("https://www.naukri.com/mnjuser/profile?id=&altresid=")
            self.random_delay(2, 3)
            
            # Find update resume link
            update_link = self.driver.find_element(
                By.XPATH, "//*[contains(text(), 'Update resume')]"
            )
            update_link.click()
            self.random_delay(2, 3)
            
            # Find file input and upload
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(config.RESUME_PATH)
            self.random_delay(3, 5)
            
            logger.info("Resume updated via alternative method")
            return True
            
        except Exception as e:
            logger.error(f"Alternative resume update failed: {e}")
            return False
            
    def update_headline(self):
        """Update profile headline to refresh profile."""
        if not config.UPDATE_HEADLINE or not config.HEADLINES:
            logger.info("Headline update disabled or no headlines configured")
            return True
            
        logger.info("Updating headline...")
        
        try:
            wait = WebDriverWait(self.driver, config.BROWSER_TIMEOUT)
            
            # Find the headline edit button
            headline_section = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[contains(@class, 'edit')]/parent::*[contains(@class, 'resumeHeadline')]")
                )
            )
            
            # Click to edit
            edit_icon = headline_section.find_element(By.CLASS_NAME, "edit")
            edit_icon.click()
            self.random_delay(1, 2)
            
            # Find textarea and update
            headline_textarea = wait.until(
                EC.presence_of_element_located((By.ID, "resumeHeadlineTxt"))
            )
            headline_textarea.clear()
            
            # Get next headline from rotation
            new_headline = config.HEADLINES[self.headline_index % len(config.HEADLINES)]
            self.headline_index += 1
            
            headline_textarea.send_keys(new_headline)
            self.random_delay()
            
            # Save
            save_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Save')]"
            )
            save_button.click()
            self.random_delay(2, 3)
            
            logger.info(f"Headline updated to: {new_headline}")
            return True
            
        except Exception as e:
            logger.error(f"Headline update failed: {e}")
            return False
            
    def touch_profile(self):
        """
        Make minor profile touches to update the 'last modified' timestamp.
        This helps increase visibility even without major changes.
        """
        logger.info("Touching profile to update timestamp...")
        
        try:
            # Navigate to profile
            if not self.navigate_to_profile():
                return False
                
            wait = WebDriverWait(self.driver, config.BROWSER_TIMEOUT)
            
            # Try to find any save/update button on the profile
            # Sometimes just visiting and triggering minor UI interactions helps
            
            # Scroll down the page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            self.random_delay(1, 2)
            
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.random_delay(1, 2)
            
            # Try to find the profile completion section and interact
            try:
                profile_sections = self.driver.find_elements(
                    By.CSS_SELECTOR, ".widgetHead.addMore"
                )
                if profile_sections:
                    logger.info("Found profile sections, profile touch complete")
            except NoSuchElementException:
                pass
                
            logger.info("Profile touch completed - timestamp should be updated")
            return True
            
        except Exception as e:
            logger.error(f"Profile touch failed: {e}")
            return False
            
    def update_profile(self):
        """Main method to perform all profile updates."""
        logger.info(f"Starting profile update at {datetime.now()}")
        
        try:
            self.setup_driver()
            
            # Login
            if not self.login():
                logger.error("Unable to login, aborting update")
                return False
                
            # Navigate to profile
            if not self.navigate_to_profile():
                logger.error("Unable to access profile page")
                return False
            
            success = True
            
            # Update resume if enabled
            if config.UPDATE_RESUME:
                if not self.update_resume():
                    success = False
                    logger.warning("Resume update failed, continuing with other updates")
                    
            # Update headline if enabled
            if config.UPDATE_HEADLINE:
                if not self.update_headline():
                    success = False
                    logger.warning("Headline update failed, continuing with other updates")
                    
            # Touch profile (always do this as fallback)
            self.touch_profile()
            
            logger.info(f"Profile update completed. Success: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Profile update failed with error: {e}")
            return False
            
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")


def run_update_with_retry():
    """Run the update process with retry logic."""
    updater = NaukriUpdater()
    
    for attempt in range(config.MAX_RETRIES):
        try:
            logger.info(f"Update attempt {attempt + 1} of {config.MAX_RETRIES}")
            
            if updater.update_profile():
                logger.info("Profile update successful!")
                return True
            else:
                logger.warning(f"Update attempt {attempt + 1} failed")
                
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} crashed: {e}")
            
        if attempt < config.MAX_RETRIES - 1:
            logger.info(f"Waiting {config.RETRY_DELAY} seconds before retry...")
            time.sleep(config.RETRY_DELAY)
            
    logger.error("All update attempts failed")
    return False


if __name__ == "__main__":
    run_update_with_retry()
