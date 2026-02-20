# Cookie-Based Authentication Setup

Since Naukri uses advanced bot protection (Akamai), automated login may not work reliably. 
You can bypass this by exporting cookies from your browser after logging in manually.

## Steps to Export Cookies

### Option 1: Using Browser Extension (Recommended)

1. **Install a cookie export extension:**
   - Chrome: "EditThisCookie" or "Cookie-Editor"
   - Firefox: "Cookie Quick Manager" or "Cookie-Editor"

2. **Login to Naukri manually** in your browser

3. **Export cookies:**
   - Click the extension icon
   - Export cookies in "Netscape" format
   - Save as `naukri_cookies.txt` in the same folder as this script

### Option 2: Using Browser DevTools

1. Login to Naukri in your browser
2. Open DevTools (F12)
3. Go to Application > Cookies > naukri.com
4. Copy all cookie names and values
5. Create `naukri_cookies.txt` with format:
   ```
   # Netscape HTTP Cookie File
   .naukri.com	TRUE	/	FALSE	0	COOKIE_NAME	COOKIE_VALUE
   ```

### Option 3: Using the Python script

If you have Chrome with profile saved:
```python
# On Windows, run this to extract Chrome cookies
python extract_cookies.py
```

## Cookie File Location

Place the `naukri_cookies.txt` file in:
- **Windows:** Same folder as naukri_updater.py
- **Termux:** `/data/data/com.termux/files/home/naukri_auto_update/`

## Troubleshooting

If cookies expire (usually after 1-2 weeks):
1. Login to Naukri manually in browser
2. Re-export cookies
3. Copy to Termux: `scp -P 8022 naukri_cookies.txt u0_a510@192.168.1.117:~/naukri_auto_update/`
