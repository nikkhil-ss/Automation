"""
Naukri Profile Auto Updater
Automatically updates your Naukri profile to increase visibility to recruiters.
Uses requests library - works perfectly on Termux without browser dependencies.
"""

import os
import sys
import time
import random
import logging
import json
import certifi
from datetime import datetime
import requests
from requests.exceptions import RequestException

import config

# Config defaults (in case config.py is incomplete)
LOG_LEVEL = getattr(config, 'LOG_LEVEL', 'INFO')
LOG_FILE = getattr(config, 'LOG_FILE', 'naukri_update.log')
HEADLESS = getattr(config, 'HEADLESS', True)
BROWSER_TIMEOUT = getattr(config, 'BROWSER_TIMEOUT', 30)
MAX_RETRIES = getattr(config, 'MAX_RETRIES', 3)
RETRY_DELAY = getattr(config, 'RETRY_DELAY', 60)
UPDATE_RESUME = getattr(config, 'UPDATE_RESUME', True)
UPDATE_HEADLINE = getattr(config, 'UPDATE_HEADLINE', False)
RESUME_PATH = getattr(config, 'RESUME_PATH', '')
HEADLINES = getattr(config, 'HEADLINES', [])
NAUKRI_EMAIL = getattr(config, 'NAUKRI_EMAIL', '')
NAUKRI_PASSWORD = getattr(config, 'NAUKRI_PASSWORD', '')

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class NaukriUpdater:
    """Handles Naukri profile automation tasks using HTTP requests."""
    
    # API Endpoints
    LOGIN_URL = "https://www.naukri.com/central-login-services/v1/login"
    PROFILE_URL = "https://www.naukri.com/mnjuser/profile"
    RESUME_UPLOAD_URL = "https://www.naukri.com/mnjuser/profile"
    PROFILE_API_URL = "https://www.naukri.com/central-profileservice/v1/profile"
    HEADLINE_UPDATE_URL = "https://www.naukri.com/central-profileservice/v1/profile/resumeHeadline"
    
    # Headers to mimic browser
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Origin": "https://www.naukri.com",
        "Referer": "https://www.naukri.com/nlogin/login",
        "appid": "109",
        "systemid": "109",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.session.verify = certifi.where()  # Use certifi SSL certificates
        self.headline_index = 0
        self.auth_token = None
        
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to appear more human-like."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        
    def login(self):
        """Login to Naukri account."""
        logger.info("Attempting to login to Naukri...")
        
        if not NAUKRI_EMAIL or not NAUKRI_PASSWORD:
            logger.error("Email or password not configured!")
            return False
        
        if NAUKRI_EMAIL == "your_email@example.com":
            logger.error("Please update config.py with your actual Naukri credentials!")
            return False
        
        try:
            # First, get the login page to obtain any necessary cookies
            self.session.get(
                "https://www.naukri.com/nlogin/login",
                timeout=BROWSER_TIMEOUT
            )
            self.random_delay(1, 2)
            
            # Login payload - Naukri requires these specific fields
            login_data = {
                "username": NAUKRI_EMAIL,
                "password": NAUKRI_PASSWORD,
                "resFormat": "json"
            }
            
            # Update headers for login request
            login_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json",
                "Origin": "https://www.naukri.com",
                "Referer": "https://www.naukri.com/nlogin/login",
                "appid": "109",
                "systemid": "Naukri",
                "gid": "LOCATION,ENTITY,CLUSTER,COLLEGE,COURSE,BRANCH_NEW,INSTITUTE,COMPANY_GROUP,SALARY,SKILLS,DESIGNATION,DEPARTMENT,INDUSTRY,EDUCATION,EXPERIENCE,FRESHER,JOB_TYPE,SOURCE,FUNCTION,COMPANY_TYPE,COMPANY_SIZE,CERTIFICATION,CANDIDATE_SOURCE,JOB_LOCATION,JOB_ROLE"
            }
            
            response = self.session.post(
                self.LOGIN_URL,
                json=login_data,
                headers=login_headers,
                timeout=BROWSER_TIMEOUT
            )
            
            logger.info(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.debug(f"Login response: {json.dumps(data, indent=2)}")
                except:
                    pass
                
                # Check cookies for auth tokens
                auth_cookies = [c.name for c in self.session.cookies]
                logger.info(f"Cookies received: {auth_cookies}")
                
                if self.session.cookies:
                    logger.info("Login successful!")
                    return True
                else:
                    logger.warning("Login completed but no cookies received")
                    return True  # Try to continue anyway
                    
            elif response.status_code == 401:
                logger.error("Invalid credentials! Please check your email and password in config.py")
                return False
            elif response.status_code == 400:
                logger.error("Bad request - validation error")
                try:
                    error_data = response.json()
                    logger.error(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    logger.error(f"Response: {response.text[:500]}")
                return False
            elif response.status_code == 403:
                logger.error("Access forbidden - account may be locked or CAPTCHA required")
                logger.info("Try logging in manually via browser first, then retry")
                return False
            else:
                logger.error(f"Login failed with status {response.status_code}")
                try:
                    logger.error(f"Response: {response.text[:500]}")
                except:
                    pass
                return False
                
        except RequestException as e:
            logger.error(f"Login request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Login failed with error: {e}")
            return False
            
    def update_resume(self):
        """Re-upload resume to increase profile visibility."""
        if not UPDATE_RESUME:
            logger.info("Resume update disabled in config")
            return True
            
        logger.info("Updating resume...")
        
        try:
            # Check if resume file exists
            if not RESUME_PATH:
                logger.warning("Resume path not configured - skipping resume upload")
                return True
                
            if not os.path.exists(RESUME_PATH):
                logger.warning(f"Resume file not found: {RESUME_PATH} - skipping resume upload")
                return True
            
            # Determine file type
            file_ext = os.path.splitext(RESUME_PATH)[1].lower()
            content_types = {
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            content_type = content_types.get(file_ext, 'application/octet-stream')
            
            # Read the file
            with open(RESUME_PATH, 'rb') as f:
                file_content = f.read()
            
            logger.info(f"Uploading resume: {os.path.basename(RESUME_PATH)} ({len(file_content)} bytes)")
            
            # Prepare multipart form data
            file_name = os.path.basename(RESUME_PATH)
            files = {
                'file': (file_name, file_content, content_type)
            }
            
            # Remove Content-Type header for multipart upload
            headers = dict(self.session.headers)
            headers.pop('Content-Type', None)
            headers['Referer'] = 'https://www.naukri.com/mnjuser/profile'
            
            self.random_delay(1, 2)
            
            # Try the upload
            response = self.session.post(
                "https://www.naukri.com/mnjuser/profile?action=uploadResumeAttach",
                files=files,
                headers=headers,
                timeout=BROWSER_TIMEOUT * 2
            )
            
            logger.info(f"Resume upload response status: {response.status_code}")
            
            if response.status_code in [200, 201, 302]:
                logger.info("Resume uploaded successfully!")
                return True
            else:
                logger.warning(f"Resume upload returned status {response.status_code}")
                return True  # Don't fail the whole update for resume issues
                
        except Exception as e:
            logger.error(f"Resume update failed: {e}")
            return True  # Continue with other updates
            
    def update_headline(self):
        """Update profile headline to refresh profile."""
        if not UPDATE_HEADLINE or not HEADLINES:
            logger.info("Headline update disabled or no headlines configured")
            return True
            
        logger.info("Updating headline...")
        
        try:
            # Get next headline from rotation
            new_headline = HEADLINES[self.headline_index % len(HEADLINES)]
            self.headline_index += 1
            
            payload = {
                "resumeHeadline": new_headline
            }
            
            self.random_delay(1, 2)
            
            response = self.session.put(
                self.HEADLINE_UPDATE_URL,
                json=payload,
                timeout=BROWSER_TIMEOUT
            )
            
            logger.info(f"Headline update response status: {response.status_code}")
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Headline updated to: {new_headline}")
                return True
            else:
                logger.warning(f"Headline update returned status {response.status_code}")
                return True  # Don't fail for headline issues
                
        except Exception as e:
            logger.error(f"Headline update failed: {e}")
            return True
            
    def touch_profile(self):
        """
        Access profile to update the 'last active' timestamp.
        This helps increase visibility even without major changes.
        """
        logger.info("Touching profile to update timestamp...")
        
        try:
            self.random_delay(1, 2)
            
            # Access profile page
            response = self.session.get(
                self.PROFILE_URL,
                timeout=BROWSER_TIMEOUT
            )
            
            logger.info(f"Profile page response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("Profile page accessed successfully")
                
                # Check if we're still logged in
                if "login" in response.url.lower():
                    logger.warning("Session expired - redirect to login page detected")
                    return False
            
            # Also hit the API endpoint
            self.random_delay(0.5, 1)
            
            response = self.session.get(
                self.PROFILE_API_URL,
                timeout=BROWSER_TIMEOUT
            )
            
            logger.info(f"Profile API response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("Profile API accessed - timestamp should be updated")
                return True
            else:
                logger.warning(f"Profile API returned status {response.status_code}")
                return True  # Consider partial success
                
        except Exception as e:
            logger.error(f"Profile touch failed: {e}")
            return False
            
    def update_profile(self):
        """Main method to perform all profile updates."""
        logger.info("=" * 50)
        logger.info(f"Starting profile update at {datetime.now()}")
        logger.info("=" * 50)
        
        try:
            # Login
            if not self.login():
                logger.error("Unable to login, aborting update")
                return False
            
            self.random_delay(2, 4)
            
            success = True
            
            # Touch profile first (always do this)
            if not self.touch_profile():
                logger.warning("Profile touch failed")
                success = False
            
            self.random_delay(1, 2)
            
            # Update resume if enabled
            if UPDATE_RESUME:
                self.update_resume()  # Don't fail on resume issues
                    
            self.random_delay(1, 2)
            
            # Update headline if enabled
            if UPDATE_HEADLINE:
                self.update_headline()  # Don't fail on headline issues
            
            logger.info("=" * 50)
            logger.info(f"Profile update completed. Success: {success}")
            logger.info("=" * 50)
            return success
            
        except Exception as e:
            logger.error(f"Profile update failed with error: {e}")
            return False
            
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources."""
        try:
            self.session.close()
            logger.debug("Session closed")
        except Exception as e:
            logger.warning(f"Error closing session: {e}")


def run_update_with_retry():
    """Run the update process with retry logic."""
    
    for attempt in range(MAX_RETRIES):
        updater = NaukriUpdater()
        try:
            logger.info(f"Update attempt {attempt + 1} of {MAX_RETRIES}")
            
            if updater.update_profile():
                logger.info("Profile update successful!")
                return True
            else:
                logger.warning(f"Update attempt {attempt + 1} failed")
                
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} crashed: {e}")
            
        if attempt < MAX_RETRIES - 1:
            logger.info(f"Waiting {RETRY_DELAY} seconds before retry...")
            time.sleep(RETRY_DELAY)
            
    logger.error("All update attempts failed")
    return False


if __name__ == "__main__":
    print("Naukri Profile Auto Updater")
    print("=" * 40)
    run_update_with_retry()
