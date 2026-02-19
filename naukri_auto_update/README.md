# Naukri Profile Auto Updater

Automatically update your Naukri profile at scheduled intervals to increase visibility to recruiters. Designed to run on **Termux (Android)** or any Linux server.

## Why Update Your Profile?

Naukri shows recruiters profiles sorted by "last modified" date. By regularly updating your profile (even minor changes), your profile stays at the top of search results, increasing your chances of being contacted by recruiters.

## Features

- 🔄 **Automatic Resume Re-upload**: Re-uploads your resume to refresh the "last updated" timestamp
- 📝 **Headline Rotation**: Cycles through different headlines to keep profile fresh
- ⏰ **Scheduled Updates**: Run updates at specified times throughout the day
- 🔒 **Secure**: Credentials stored locally, never sent to third parties
- 📱 **Termux Compatible**: Runs on your Android phone 24/7
- 📊 **Logging**: Full logging of all activities for debugging

## Quick Start

### Prerequisites

- Termux app installed on Android (or any Linux environment)
- Python 3.8+
- Chrome/Chromium browser
- Your Naukri account credentials

### Installation on Termux

1. **Install Termux** from F-Droid (recommended) or Play Store

2. **Clone or copy the project**:
   ```bash
   cd ~
   git clone <your-repo-url> naukri_auto_update
   # OR copy files manually
   ```

3. **Run the setup script**:
   ```bash
   cd ~/naukri_auto_update
   chmod +x setup_termux.sh
   ./setup_termux.sh
   ```

4. **Configure your credentials**:
   ```bash
   nano config.py
   ```
   
   Update these values:
   ```python
   NAUKRI_EMAIL = "your_email@example.com"
   NAUKRI_PASSWORD = "your_password"
   RESUME_PATH = "/data/data/com.termux/files/home/resume.pdf"
   ```

5. **Copy your resume**:
   ```bash
   cp /sdcard/Download/your_resume.pdf ~/resume.pdf
   ```

6. **Test the automation**:
   ```bash
   python scheduler.py --run-once
   ```

### Running Options

#### Option 1: Continuous Scheduler (Recommended)

Run as a background process that handles all scheduling:

```bash
cd ~/naukri_auto_update
nohup python scheduler.py --daemon > scheduler_output.log 2>&1 &
```

To keep it running after closing Termux, use `termux-wake-lock`:
```bash
termux-wake-lock
```

#### Option 2: Cron Jobs

Set up cron to run at specific times:

```bash
crontab -e
```

Add these lines:
```cron
0 9 * * * cd ~/naukri_auto_update && python naukri_updater.py >> logs/cron.log 2>&1
0 12 * * * cd ~/naukri_auto_update && python naukri_updater.py >> logs/cron.log 2>&1
0 15 * * * cd ~/naukri_auto_update && python naukri_updater.py >> logs/cron.log 2>&1
0 18 * * * cd ~/naukri_auto_update && python naukri_updater.py >> logs/cron.log 2>&1
0 21 * * * cd ~/naukri_auto_update && python naukri_updater.py >> logs/cron.log 2>&1
```

## Configuration

Edit `config.py` to customize:

| Option | Description | Default |
|--------|-------------|---------|
| `NAUKRI_EMAIL` | Your Naukri login email | - |
| `NAUKRI_PASSWORD` | Your Naukri password | - |
| `UPDATE_INTERVALS` | Hours to run updates (24h format) | `[9, 12, 15, 18, 21]` |
| `UPDATE_RESUME` | Re-upload resume each time | `True` |
| `UPDATE_HEADLINE` | Rotate profile headline | `False` |
| `RESUME_PATH` | Path to your resume file | - |
| `HEADLESS` | Run browser without GUI | `True` |
| `MAX_RETRIES` | Retry attempts on failure | `3` |

## File Structure

```
naukri_auto_update/
├── config.py           # Configuration settings
├── naukri_updater.py   # Main automation script
├── scheduler.py        # Scheduling logic
├── setup_termux.sh     # Termux setup script
├── requirements.txt    # Python dependencies
├── run_update.sh       # Quick run script
├── README.md           # This file
└── logs/               # Log files directory
```

## Commands

```bash
# Run single update immediately
python scheduler.py --run-once

# Check scheduler status
python scheduler.py --status

# Run as continuous daemon
python scheduler.py --daemon

# Run the updater directly
python naukri_updater.py
```

## Troubleshooting

### Common Issues

1. **ChromeDriver version mismatch**
   ```bash
   pip install --upgrade chromedriver-autoinstaller
   ```

2. **Login fails**
   - Check your credentials in `config.py`
   - Naukri might have CAPTCHA - try logging in manually first
   - Wait a few minutes and try again

3. **Element not found**
   - Naukri may have updated their website
   - Check the log file for details
   - Update selectors in `naukri_updater.py` if needed

4. **Termux closes and stops script**
   - Use `termux-wake-lock` to prevent sleep
   - Consider using Termux:Boot to start on device boot

### Checking Logs

```bash
tail -f naukri_update.log
```

### Running in Background

```bash
# Start with nohup
nohup python scheduler.py --daemon &

# Check if running
ps aux | grep scheduler

# Stop the scheduler
pkill -f "python scheduler.py"
```

## Security Notes

- Your credentials are stored locally in `config.py`
- Never commit `config.py` to a public repository
- Consider using environment variables for sensitive data
- The script runs locally on your device only

## Keeping Termux Running

To ensure Termux keeps running:

1. **Acquire Wake Lock**:
   ```bash
   termux-wake-lock
   ```

2. **Disable Battery Optimization** for Termux in Android Settings

3. **Use Termux:Boot** (optional) to start on device boot:
   ```bash
   pkg install termux-boot
   mkdir -p ~/.termux/boot
   echo "cd ~/naukri_auto_update && python scheduler.py --daemon" > ~/.termux/boot/start_naukri.sh
   chmod +x ~/.termux/boot/start_naukri.sh
   ```

## Contributing

Feel free to submit issues and enhancement requests!

## Disclaimer

This tool is for personal use only. Use responsibly and in accordance with Naukri's terms of service. The author is not responsible for any consequences of using this automation.

## License

MIT License - Feel free to modify and distribute.
