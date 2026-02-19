# Configuration Template for Naukri Auto Update
# Copy this file as config.py and update with your values
# DO NOT commit config.py to version control!

# Naukri Login Credentials
NAUKRI_EMAIL = "your_email@example.com"
NAUKRI_PASSWORD = "your_password"

# Update Schedule (in hours, 24-hour format)
# The app will update your profile at these times daily
UPDATE_INTERVALS = ["07:00", "08:00", "08:30", "08:45", "09:00"]  # 7 AM, 8 AM, 8:30 AM, 8:45 AM, 9 AM

# Profile Update Options
UPDATE_RESUME = True  # Re-upload resume (increases visibility significantly)
UPDATE_HEADLINE = False  # Toggle headline update
UPDATE_PROFILE_SUMMARY = False  # Toggle profile summary update

# Resume file path
# For Termux: /data/data/com.termux/files/home/resume.pdf
# For Linux: /home/username/resume.pdf
RESUME_PATH = "/data/data/com.termux/files/home/resume.pdf"

# Alternate headlines to cycle through (if UPDATE_HEADLINE is True)
HEADLINES = [
    "Software Engineer | Python | Automation | Web Development",
    "Software Developer | Python | Full Stack | Cloud",
]

# Browser Settings
HEADLESS = True  # Run browser in headless mode (no GUI) - Required for Termux
BROWSER_TIMEOUT = 30  # Seconds to wait for page loads

# Logging
LOG_FILE = "naukri_update.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Retry Settings
MAX_RETRIES = 3
RETRY_DELAY = 60  # Seconds between retries
