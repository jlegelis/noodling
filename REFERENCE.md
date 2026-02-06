# Quick Reference Card

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Test individual scrapers
cd src && python test_scrapers.py

# Run once (output based on config.yaml)
cd src && python main.py

# Run continuously (daily schedule)
cd src && python scheduler.py
```

## Output Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `file` | Write to text file only | Testing, debugging, no email setup |
| `email` | Send email only | Production use |
| `both` | File and email | Keep records + send notifications |

**Set in config.yaml:**
```yaml
output:
  mode: "file"  # Change this
```

## Key Files

| File | Purpose |
|------|---------|
| `config.yaml` | Your configuration |
| `events_output.txt` | Results when using file mode |
| `scraper_diagnostics.log` | Detailed scraping logs |
| `src/main.py` | Main script |
| `src/scheduler.py` | Daily automation |
| `src/test_scrapers.py` | Testing utility |

## Configuration Quick Reference

```yaml
# Output
output:
  mode: "file"                    # "file", "email", or "both"
  output_file: "events_output.txt"

# Email
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  sender_email: "your@gmail.com"
  sender_password: "app-password"  # Not your regular password!
  recipients:
    - "recipient@example.com"
  subject: "Today's Live Music in Boston"

# Scraping
scraping:
  user_agent: "Mozilla/5.0..."     # Browser user agent
  timeout: 10                      # Seconds
  days_ahead: 7                    # How far to look ahead

# Schedule
schedule:
  daily_time: "09:00"              # 24-hour format
```

## Workflow

### 1. Initial Setup
```bash
pip install -r requirements.txt
cp config.yaml.example config.yaml
# config.yaml already set to mode: "file"
```

### 2. Test Scrapers
```bash
cd src
python test_scrapers.py
```

### 3. Run First Scrape
```bash
python main.py
# Check events_output.txt
# Check scraper_diagnostics.log if issues
```

### 4. Enable Email (when ready)
```yaml
# In config.yaml:
output:
  mode: "email"  # or "both"

email:
  sender_email: "your@gmail.com"
  sender_password: "your-app-password"
  recipients:
    - "your@email.com"
```

### 5. Test Email
```bash
python main.py
```

### 6. Set Up Automation
```bash
# Option A: Run scheduler
python scheduler.py

# Option B: Add to crontab
crontab -e
# Add: 0 9 * * * cd /path/to/Music\ Finder/src && python3 main.py
```

## Troubleshooting Quick Checks

### No events found?
1. Check `events_output.txt` - shows per-venue status
2. Check `scraper_diagnostics.log` - detailed errors
3. Try each venue individually: `python test_scrapers.py`
4. Increase `days_ahead` in config.yaml

### Email not sending?
1. Using Gmail App Password (not regular password)?
2. 2FA enabled on Google account?
3. Try `mode: "file"` first to verify scraping works
4. Check for typos in email config

### Scraper errors?
1. Check `scraper_diagnostics.log` for HTTP errors
2. Visit venue website in browser - is it accessible?
3. Log shows page structure - has website changed?
4. One venue failure doesn't stop others

## Gmail App Password Setup

1. Enable 2FA: https://myaccount.google.com/security
2. App Passwords: https://myaccount.google.com/apppasswords
3. Select "Mail" → "Other" → "Music Finder"
4. Copy 16-char password to config.yaml

## Output File Format

```
================================================================================
Boston Live Music Events
Generated: 2026-02-04 09:00:00
================================================================================

Summary by Venue
--------------------------------------------------------------------------------
Venue                                                Events     Status
--------------------------------------------------------------------------------
Beehive Boston                                            0    0 events
Lizard Lounge                                             5         OK
Plough and Stars                                          3         OK
The Burren                                                8         OK
The Mad Monkfish                                          2         OK
Wally's Cafe                                             14         OK
--------------------------------------------------------------------------------
Total                                                    32
================================================================================
```

## Diagnostic Log Format

```
2026-02-04 09:00:00 - scraper - INFO - [The Burren] Fetching page: https://...
2026-02-04 09:00:01 - scraper - INFO - [The Burren] Response status: 200
2026-02-04 09:00:01 - scraper - DEBUG - [The Burren] Page structure diagnostics:
2026-02-04 09:00:01 - scraper - DEBUG -   - Elements: 234 divs, 2 tables, 156 links
2026-02-04 09:00:01 - scraper - INFO - [The Burren] Scraping complete: Found 8 events
```

## Support

- Full docs: `README.md`
- Quick start: `QUICKSTART.md`
- Changes: `CHANGELOG.md`
- This guide: `REFERENCE.md`
