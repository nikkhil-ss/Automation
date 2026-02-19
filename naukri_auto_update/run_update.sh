#!/data/data/com.termux/files/usr/bin/bash

# Quick run script for Naukri Auto Updater
# Usage: ./run_update.sh [--once|--daemon|--status]

cd "$(dirname "$0")"

case "$1" in
    --once)
        echo "Running single update..."
        python scheduler.py --run-once
        ;;
    --daemon)
        echo "Starting daemon mode..."
        termux-wake-lock
        python scheduler.py --daemon
        ;;
    --status)
        python scheduler.py --status
        ;;
    --stop)
        echo "Stopping scheduler..."
        pkill -f "python scheduler.py"
        termux-wake-unlock
        echo "Stopped."
        ;;
    --logs)
        tail -f naukri_update.log
        ;;
    *)
        echo "Naukri Auto Updater"
        echo "==================="
        echo ""
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  --once    Run a single update now"
        echo "  --daemon  Start continuous scheduler"
        echo "  --status  Show scheduler status"
        echo "  --stop    Stop the running scheduler"
        echo "  --logs    View live logs"
        echo ""
        echo "Example:"
        echo "  $0 --daemon   # Start the scheduler"
        echo ""
        ;;
esac
