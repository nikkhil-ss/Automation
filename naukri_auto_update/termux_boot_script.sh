#!/data/data/com.termux/files/usr/bin/bash

# Naukri Auto Updater - Termux Boot Script
# This script is designed to be placed in ~/.termux/boot/
# It will automatically start the scheduler when Termux boots

# Wait for system to stabilize
sleep 10

# Acquire wake lock to prevent sleep
termux-wake-lock

# Navigate to project directory
cd ~/naukri_auto_update

# Start the scheduler in daemon mode
nohup python scheduler.py --daemon > logs/boot_startup.log 2>&1 &

# Log startup
echo "$(date): Naukri Auto Updater started via boot script" >> logs/boot.log
