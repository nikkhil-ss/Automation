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
echo "[1/6] Updating package lists..."
pkg update -y

# Upgrade existing packages
echo "[2/6] Upgrading existing packages..."
pkg upgrade -y

# Install required packages
echo "[3/6] Installing required packages..."
pkg install -y python git cronie termux-services

# Install pip if not available
echo "[4/6] Setting up pip..."
pip install --upgrade pip

# Install Python dependencies
echo "[5/6] Installing Python dependencies..."
pip install requests schedule

# Create necessary directories
echo "[6/6] Creating directories..."
mkdir -p ~/naukri_auto_update
mkdir -p ~/naukri_auto_update/logs

# Setup cron for scheduling
echo "Setting up cron service..."
sv-enable crond 2>/dev/null || true

echo ""
echo "============================================"
echo "Setup complete!"
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
