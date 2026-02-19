"""
Scheduler for Naukri Profile Auto Updater
Runs the profile update at specified intervals throughout the day.
Supports both cron-based (Termux) and continuous scheduling modes.
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime, timedelta
import schedule

import config
from naukri_updater import run_update_with_retry

# Config defaults (in case config.py is incomplete)
LOG_LEVEL = getattr(config, 'LOG_LEVEL', 'INFO')
LOG_FILE = getattr(config, 'LOG_FILE', 'naukri_update.log')
UPDATE_INTERVALS = getattr(config, 'UPDATE_INTERVALS', ["07:00", "08:00", "08:30", "08:45", "09:00"])
UPDATE_RESUME = getattr(config, 'UPDATE_RESUME', True)
UPDATE_HEADLINE = getattr(config, 'UPDATE_HEADLINE', False)
HEADLESS = getattr(config, 'HEADLESS', True)
MAX_RETRIES = getattr(config, 'MAX_RETRIES', 3)

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


class GracefulKiller:
    """Handle graceful shutdown on SIGTERM/SIGINT."""
    kill_now = False
    
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        
    def exit_gracefully(self, *args):
        logger.info("Shutdown signal received, stopping scheduler...")
        self.kill_now = True


def job():
    """Scheduled job to run the profile update."""
    logger.info("=" * 50)
    logger.info("Scheduled update triggered")
    logger.info("=" * 50)
    
    try:
        success = run_update_with_retry()
        if success:
            logger.info("Scheduled update completed successfully")
        else:
            logger.error("Scheduled update failed")
    except Exception as e:
        logger.error(f"Scheduled update crashed: {e}")
    
    logger.info("Next scheduled run will be at the configured interval")


def setup_schedule():
    """Setup the schedule based on configured intervals."""
    logger.info("Setting up update schedule...")
    
    for schedule_time in UPDATE_INTERVALS:
        # Handle both string times ("08:30") and integer hours (8)
        if isinstance(schedule_time, int):
            time_str = f"{schedule_time:02d}:00"
        else:
            time_str = schedule_time
        schedule.every().day.at(time_str).do(job)
        logger.info(f"Scheduled update at {time_str}")
    
    logger.info(f"Total {len(UPDATE_INTERVALS)} updates scheduled per day")


def run_scheduler():
    """Run the continuous scheduler."""
    killer = GracefulKiller()
    
    logger.info("=" * 50)
    logger.info("Naukri Auto Updater Scheduler Started")
    logger.info(f"Current time: {datetime.now()}")
    logger.info("=" * 50)
    
    setup_schedule()
    
    # Show next run time
    next_run = schedule.next_run()
    if next_run:
        logger.info(f"Next scheduled update: {next_run}")
    
    # Run pending jobs if any
    schedule.run_pending()
    
    # Main loop
    while not killer.kill_now:
        try:
            schedule.run_pending()
            
            # Log heartbeat every hour
            current_minute = datetime.now().minute
            if current_minute == 0:
                next_run = schedule.next_run()
                logger.debug(f"Scheduler heartbeat - Next run: {next_run}")
            
            time.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)
    
    logger.info("Scheduler stopped gracefully")


def run_once():
    """Run a single update immediately (useful for testing)."""
    logger.info("Running single update...")
    job()


def calculate_next_run_time():
    """Calculate and display when the next update will occur."""
    now = datetime.now()
    current_time = now.hour * 60 + now.minute  # Current time in minutes
    
    # Parse schedule times and find next one
    schedule_times = []
    for t in UPDATE_INTERVALS:
        if isinstance(t, int):
            schedule_times.append((t, 0))  # (hour, minute)
        else:
            parts = t.split(":")
            schedule_times.append((int(parts[0]), int(parts[1])))
    
    # Find next scheduled time
    future_times = [(h, m) for h, m in schedule_times if h * 60 + m > current_time]
    
    if future_times:
        next_h, next_m = future_times[0]
        next_run = now.replace(hour=next_h, minute=next_m, second=0, microsecond=0)
    else:
        # Next day's first scheduled time
        next_h, next_m = schedule_times[0]
        next_run = now.replace(hour=next_h, minute=next_m, second=0, microsecond=0) + timedelta(days=1)
    
    time_until = next_run - now
    return next_run, time_until


def print_status():
    """Print current scheduler status."""
    print("\n" + "=" * 50)
    print("NAUKRI AUTO UPDATER - STATUS")
    print("=" * 50)
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scheduled Hours: {UPDATE_INTERVALS}")
    
    next_run, time_until = calculate_next_run_time()
    print(f"Next Update: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time Until Next: {time_until}")
    
    print("\nConfiguration:")
    print(f"  - Resume Update: {UPDATE_RESUME}")
    print(f"  - Headline Update: {UPDATE_HEADLINE}")
    print(f"  - Headless Mode: {HEADLESS}")
    print(f"  - Max Retries: {MAX_RETRIES}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Naukri Profile Auto Updater Scheduler")
    parser.add_argument(
        "--run-once", 
        action="store_true", 
        help="Run a single update immediately"
    )
    parser.add_argument(
        "--status", 
        action="store_true", 
        help="Show current scheduler status"
    )
    parser.add_argument(
        "--daemon", 
        action="store_true", 
        help="Run as continuous daemon"
    )
    
    args = parser.parse_args()
    
    if args.status:
        print_status()
    elif args.run_once:
        run_once()
    elif args.daemon:
        run_scheduler()
    else:
        # Default: show status and run scheduler
        print_status()
        run_scheduler()
