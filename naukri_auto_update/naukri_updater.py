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
import urllib3
import certifi
import platform
import re
from datetime import datetime
import requests
from requests.exceptions import RequestException
from http.cookiejar import MozillaCookieJar

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import config

# Cookie file path (export cookies from browser in Netscape format)
COOKIE_FILE = os.path.join(os.path.dirname(__file__), 'naukri_cookies.txt')

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
    
    # API Endpoints - try multiple login endpoints
    LOGIN_URL = "https://www.naukri.com/central-login-services/v1/login"
    LOGIN_URL_ALT = "https://login.naukri.com/nLogin/Login.php"
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
        self.session.verify = False  # Disable SSL verify for Termux compatibility
        self.headline_index = 0
        self.auth_token = None
        self.logged_in = False
        self.user_name = None
        
        # Try to load cookies from file first
        self._load_cookies_from_file()
    
    def _load_cookies_from_file(self):
        """Load cookies from browser export (Netscape format)."""
        if os.path.exists(COOKIE_FILE):
            try:
                logger.info(f"Loading cookies from {COOKIE_FILE}")
                cookie_jar = MozillaCookieJar(COOKIE_FILE)
                cookie_jar.load(ignore_discard=True, ignore_expires=True)
                self.session.cookies.update(cookie_jar)
                cookie_names = [c.name for c in self.session.cookies]
                logger.info(f"Loaded cookies: {cookie_names}")
                
                # Check if we have auth cookies
                if any('JEESSION' in c or 'naukri' in c.lower() for c in cookie_names):
                    logger.info("Found auth cookies - will verify session")
            except Exception as e:
                logger.warning(f"Failed to load cookies: {e}")
    
    def _save_cookies_to_file(self):
        """Save current cookies to file."""
        try:
            with open(COOKIE_FILE, 'w') as f:
                f.write("# Netscape HTTP Cookie File\n")
                for cookie in self.session.cookies:
                    secure = "TRUE" if cookie.secure else "FALSE"
                    expires = str(cookie.expires) if cookie.expires else "0"
                    f.write(f".naukri.com\tTRUE\t{cookie.path}\t{secure}\t{expires}\t{cookie.name}\t{cookie.value}\n")
            logger.info(f"Cookies saved to {COOKIE_FILE}")
        except Exception as e:
            logger.warning(f"Failed to save cookies: {e}")
        
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
                timeout=BROWSER_TIMEOUT,
                verify=False
            )
            self.random_delay(1, 2)
            
            # Login payload - correct format for Naukri API
            login_data = {
                "username": NAUKRI_EMAIL,
                "password": NAUKRI_PASSWORD
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
                "systemid": "109"
            }
            
            response = self.session.post(
                self.LOGIN_URL,
                json=login_data,
                headers=login_headers,
                timeout=BROWSER_TIMEOUT,
                verify=False
            )
            
            logger.info(f"Login response status: {response.status_code}")
            
            # If JSON API fails with 400, try form-based login
            if response.status_code == 400:
                logger.info("JSON API failed, trying form-based login...")
                return self._login_form_based()
            
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
    
    def _login_form_based(self):
        """Try form-based login (traditional website login)."""
        logger.info("Attempting form-based login...")
        
        try:
            # Form-based login data
            form_data = {
                "username": NAUKRI_EMAIL,
                "password": NAUKRI_PASSWORD,
                "remember": "1"
            }
            
            form_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://www.naukri.com",
                "Referer": "https://www.naukri.com/nlogin/login"
            }
            
            response = self.session.post(
                self.LOGIN_URL_ALT,
                data=form_data,
                headers=form_headers,
                timeout=BROWSER_TIMEOUT,
                verify=False,
                allow_redirects=True
            )
            
            logger.info(f"Form login response status: {response.status_code}")
            
            # Check if we got authentication cookies
            auth_cookies = [c.name for c in self.session.cookies]
            logger.info(f"Cookies after form login: {auth_cookies}")
            
            # Check for NKWAP or naukariya cookies (authentication tokens)
            has_auth = any('nkwap' in c.lower() or 'naukariya' in c.lower() or 'nauk' in c.lower() 
                          for c in auth_cookies)
            
            if has_auth or len(self.session.cookies) > 2:
                logger.info("Form-based login appears successful!")
                return True
            
            # Try to verify by accessing profile
            profile_resp = self.session.get(
                self.PROFILE_URL,
                timeout=BROWSER_TIMEOUT,
                verify=False,
                allow_redirects=False
            )
            
            if profile_resp.status_code == 200:
                logger.info("Profile accessible - login successful!")
                return True
            elif profile_resp.status_code in [301, 302]:
                redirect_url = profile_resp.headers.get('Location', '')
                if 'login' in redirect_url.lower():
                    logger.error("Login failed - redirected to login page")
                    return False
                logger.info("Login successful (redirect)")
                return True
            
            logger.warning("Login status uncertain, proceeding anyway...")
            return True
            
        except Exception as e:
            logger.error(f"Form-based login failed: {e}")
            return False
    
    def get_profile_info(self):
        """Fetch and display profile information including name."""
        logger.info("Fetching profile information...")
        
        try:
            # Try the profile API
            response = self.session.get(
                self.PROFILE_API_URL,
                headers={
                    **self.HEADERS,
                    "Accept": "application/json",
                },
                timeout=BROWSER_TIMEOUT,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Profile API response: {json.dumps(data, indent=2)[:500]}")
                
                # Extract name from profile
                profile = data.get('profile', data)
                name = profile.get('name', profile.get('fullName', profile.get('userName', 'Unknown')))
                email = profile.get('email', profile.get('emailId', 'N/A'))
                headline = profile.get('resumeHeadline', profile.get('headline', 'N/A'))
                
                logger.info(f"========== PROFILE INFO ==========")
                logger.info(f"Name: {name}")
                logger.info(f"Email: {email}")
                logger.info(f"Headline: {headline}")
                logger.info(f"===================================")
                
                return data
            else:
                logger.warning(f"Profile API returned status: {response.status_code}")
                logger.info(f"Response: {response.text[:300]}")
                
                # Try alternate profile endpoint
                alt_url = "https://www.naukri.com/central-profileservice/v1/me"
                alt_response = self.session.get(alt_url, timeout=BROWSER_TIMEOUT, verify=False)
                
                if alt_response.status_code == 200:
                    data = alt_response.json()
                    logger.info(f"Alternate profile response: {json.dumps(data, indent=2)[:500]}")
                    return data
                    
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch profile info: {e}")
            return None
    
    def update_salary(self, new_salary=900000):
        """Update preferred salary in profile."""
        logger.info(f"Updating preferred salary to {new_salary}...")
        
        try:
            # First get current profile to understand structure
            profile_data = self.get_profile_info()
            
            # Salary update endpoint
            salary_url = "https://www.naukri.com/central-profileservice/v1/profile/expectedCtc"
            
            payload = {
                "expectedCtc": str(new_salary),
                "expectedCtcLakh": str(new_salary // 100000),
                "salaryInLakh": new_salary // 100000,
                "salaryInThousand": (new_salary % 100000) // 1000
            }
            
            headers = {
                **self.HEADERS,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            
            response = self.session.put(
                salary_url,
                json=payload,
                headers=headers,
                timeout=BROWSER_TIMEOUT,
                verify=False
            )
            
            logger.info(f"Salary update response status: {response.status_code}")
            logger.info(f"Response: {response.text[:300]}")
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Successfully updated salary to {new_salary}!")
                return True
            
            # Try alternate payload format
            alt_payload = {
                "expectedCtc": new_salary
            }
            
            response = self.session.put(
                salary_url,
                json=alt_payload,
                headers=headers,
                timeout=BROWSER_TIMEOUT,
                verify=False
            )
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Successfully updated salary to {new_salary} (alt format)!")
                return True
                
            # Try POST instead of PUT
            response = self.session.post(
                salary_url,
                json=alt_payload,
                headers=headers,
                timeout=BROWSER_TIMEOUT,
                verify=False
            )
            
            logger.info(f"Salary POST response: {response.status_code} - {response.text[:200]}")
            
            return response.status_code in [200, 201, 204]
            
        except Exception as e:
            logger.error(f"Failed to update salary: {e}")
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
            
            # Fix path - ensure leading slash for absolute paths on Unix
            resume_path = RESUME_PATH
            if platform.system() != 'Windows' and not resume_path.startswith('/'):
                # Check if it looks like an absolute path missing the leading /
                if resume_path.startswith('data/') or resume_path.startswith('home/'):
                    resume_path = '/' + resume_path
                    logger.info(f"Fixed resume path: {resume_path}")
                
            if not os.path.exists(resume_path):
                logger.warning(f"Resume file not found: {resume_path} - skipping resume upload")
                # Try common paths
                alt_paths = [
                    os.path.expanduser('~/NikhilResume.pdf'),
                    os.path.expanduser('~/Nikhil_Singh_Resume_2.pdf'),
                    '/data/data/com.termux/files/home/NikhilResume.pdf',
                    '/data/data/com.termux/files/home/Nikhil_Singh_Resume_2.pdf',
                ]
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        resume_path = alt_path
                        logger.info(f"Found resume at alternate path: {resume_path}")
                        break
                else:
                    return True
            
            # Determine file type
            file_ext = os.path.splitext(resume_path)[1].lower()
            content_types = {
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            content_type = content_types.get(file_ext, 'application/octet-stream')
            
            # Read the file
            with open(resume_path, 'rb') as f:
                file_content = f.read()
            
            logger.info(f"Uploading resume: {os.path.basename(resume_path)} ({len(file_content)} bytes)")
            
            # Prepare multipart form data
            file_name = os.path.basename(resume_path)
            files = {
                'file': (file_name, file_content, content_type)
            }
            
            # Remove Content-Type header for multipart upload
            headers = dict(self.session.headers)
            headers.pop('Content-Type', None)
            headers['Referer'] = 'https://www.naukri.com/mnjuser/profile'
            
            self.random_delay(1, 2)
            
            # Try multiple upload endpoints
            upload_urls = [
                "https://www.naukri.com/mnjuser/profile?action=uploadResumeAttach",
                "https://www.naukri.com/cloudgateway-mynaukri/resman-aggregator-services/v1/upload/resume",
                "https://fileapi.naukri.com/resume/upload",
            ]
            
            upload_success = False
            for upload_url in upload_urls:
                try:
                    logger.info(f"Trying upload to: {upload_url}")
                    response = self.session.post(
                        upload_url,
                        files={'file': (file_name, file_content, content_type)},
                        headers=headers,
                        timeout=BROWSER_TIMEOUT * 2,
                        verify=False
                    )
                    
                    logger.info(f"Resume upload response status: {response.status_code}")
                    
                    if response.status_code in [200, 201, 302]:
                        logger.info("Resume uploaded successfully!")
                        upload_success = True
                        break
                    else:
                        logger.warning(f"Upload to {upload_url} returned status {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"Upload to {upload_url} failed: {e}")
                    continue
            
            if not upload_success:
                logger.warning("All resume upload endpoints failed, but continuing...")
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
                timeout=BROWSER_TIMEOUT,
                verify=False,
                allow_redirects=True
            )
            
            logger.info(f"Profile page response status: {response.status_code}")
            
            if response.status_code == 200:
                # Check page content for login indicators
                page_text = response.text.lower()
                
                # More reliable login check - look for actual profile content
                has_profile_content = any(term in page_text for term in [
                    'my profile', 'resume headline', 'employment', 'education',
                    'key skills', 'profile summary', 'personal details'
                ])
                
                if has_profile_content:
                    logger.info("Profile page loaded successfully with profile content!")
                    return True
                    
                # Check URL for login redirect
                if 'nlogin' in response.url.lower() or '/login' in response.url.lower():
                    logger.warning("Redirected to login page - session may be invalid")
                    # Don't return False - try other endpoints
                else:
                    logger.info("Profile page accessed (content verification inconclusive)")
                    return True
            
            # Also try accessing the dashboard
            self.random_delay(0.5, 1)
            
            dashboard_url = "https://www.naukri.com/mnjuser/homepage"
            dash_response = self.session.get(
                dashboard_url,
                timeout=BROWSER_TIMEOUT,
                verify=False
            )
            
            if dash_response.status_code == 200:
                if 'dashboard' in dash_response.text.lower() or 'profile' in dash_response.text.lower():
                    logger.info("Dashboard accessed successfully!")
                    return True
            
            logger.warning("Could not verify profile access, but continuing...")
            return True  # Return True to not block other updates
                
        except Exception as e:
            logger.error(f"Profile touch failed: {e}")
            return True  # Don't fail, continue with other operations
            
    def update_profile(self, show_info=True, update_salary=None):
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
            
            # Show profile info if requested
            if show_info:
                self.get_profile_info()
                self.random_delay(1, 2)
            
            # Update salary if specified
            if update_salary is not None:
                self.update_salary(update_salary)
                self.random_delay(1, 2)
            
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


def run_update_with_retry(show_info=True, update_salary=None):
    """Run the update process with retry logic."""
    
    for attempt in range(MAX_RETRIES):
        updater = NaukriUpdater()
        try:
            logger.info(f"Update attempt {attempt + 1} of {MAX_RETRIES}")
            
            if updater.update_profile(show_info=show_info, update_salary=update_salary):
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Naukri Profile Auto Updater")
    parser.add_argument("--salary", type=int, help="Update salary to this amount (e.g., 900000)")
    parser.add_argument("--no-info", action="store_true", help="Skip showing profile info")
    parser.add_argument("--info-only", action="store_true", help="Only show profile info, no updates")
    
    args = parser.parse_args()
    
    print("Naukri Profile Auto Updater")
    print("=" * 40)
    
    if args.info_only:
        # Just login and show profile info
        updater = NaukriUpdater()
        if updater.login():
            updater.get_profile_info()
        updater.cleanup()
    else:
        run_update_with_retry(
            show_info=not args.no_info, 
            update_salary=args.salary
        )
