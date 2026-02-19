#!/data/data/com.termux/files/usr/bin/bash

# ============================================
# Naukri Auto Updater - Termux Setup Script
# ============================================
# This script sets up all dependencies needed
# to run the Naukri profile auto-updater on Termux
# ============================================

set -e

echo "============================================"
echo "Naukri Auto Updater - Termux Setup"
echo "============================================"
echo ""

# Update package lists
echo "[1/8] Updating package lists..."
pkg update -y

# Upgrade existing packages
echo "[2/8] Upgrading existing packages..."
pkg upgrade -y

# Install required packages
echo "[3/8] Installing required packages..."
pkg install -y python chromium wget git cronie termux-services

# Install pip if not available
echo "[4/8] Setting up pip..."
pip install --upgrade pip

# Install Python dependencies
echo "[5/8] Installing Python dependencies..."
pip install selenium schedule

# Setup Chrome/Chromium driver
echo "[6/8] Setting up ChromeDriver..."

# Get Chromium version
CHROME_VERSION=$(chromium --version | grep -oP '\d+' | head -1)
echo "Detected Chromium version: $CHROME_VERSION"

# Download ChromeDriver (compatible version)
# Note: ChromeDriver for Termux needs to be compiled or use alternative
pip install chromedriver-autoinstaller

# Create necessary directories
echo "[7/8] Creating directories..."
mkdir -p ~/naukri_auto_update
mkdir -p ~/naukri_auto_update/logs

# Setup cron for scheduling
echo "[8/8] Setting up cron service..."
sv-enable crond 2>/dev/null || true

echo ""
echo "============================================"
echo "Basic setup complete!"
echo "============================================"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Copy your project files to ~/naukri_auto_update/"
echo "   cp -r /path/to/naukri_auto_update/* ~/naukri_auto_update/"
echo ""
echo "2. Edit config.py with your Naukri credentials:"
echo "   nano ~/naukri_auto_update/config.py"
echo ""
echo "3. Copy your resume file:"
echo "   cp /path/to/your/resume.pdf ~/resume.pdf"
echo ""
echo "4. Test the script:"
echo "   cd ~/naukri_auto_update && python scheduler.py --run-once"
echo ""
echo "5. Setup cron job for automatic execution:"
echo "   Run: crontab -e"
echo "   Add these lines (updates at 9 AM, 12 PM, 3 PM, 6 PM, 9 PM):"
echo ""
echo "   0 9 * * * cd ~/naukri_auto_update && python naukri_updater.py >> ~/naukri_auto_update/logs/cron.log 2>&1"
echo "   0 12 * * * cd ~/naukri_auto_update && python naukri_updater.py >> ~/naukri_auto_update/logs/cron.log 2>&1"
echo "   0 15 * * * cd ~/naukri_auto_update && python naukri_updater.py >> ~/naukri_auto_update/logs/cron.log 2>&1"
echo "   0 18 * * * cd ~/naukri_auto_update && python naukri_updater.py >> ~/naukri_auto_update/logs/cron.log 2>&1"
echo "   0 21 * * * cd ~/naukri_auto_update && python naukri_updater.py >> ~/naukri_auto_update/logs/cron.log 2>&1"
echo ""
echo "6. OR run the continuous scheduler:"
echo "   cd ~/naukri_auto_update && nohup python scheduler.py --daemon &"
echo ""
echo "============================================"
echo "Setup complete! Happy job hunting!"
echo "============================================"
