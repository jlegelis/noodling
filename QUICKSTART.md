# Quick Start Guide

Get Music Finder up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Output

Copy the example config:
```bash
cp config.yaml.example config.yaml
```

The default mode is `file` which writes results to a text file - perfect for testing!

**For testing (default):**
- Leave `mode: "file"` in config.yaml
- Results will be written to `events_output.txt`

**For email (when ready):**
Edit `config.yaml` and update:
- `mode`: Change to `"email"` or `"both"`
- `sender_email`: Your Gmail address
- `sender_password`: Your Gmail App Password (see below)
- `recipients`: Email addresses to receive notifications

### Getting a Gmail App Password

1. Go to your Google Account settings
2. Enable 2-factor authentication if not already enabled
3. Visit: https://myaccount.google.com/apppasswords
4. Select "Mail" and "Other (Custom name)"
5. Generate the password
6. Copy the 16-character password into `config.yaml`

## Step 3: Test the Scrapers

```bash
cd src
python test_scrapers.py
```

This will test each venue scraper and show you what events it finds.

## Step 4: Run Your First Scrape

```bash
cd src
python main.py
```

This will:
- Scrape all venues
- Display events in the console
- Write results to `events_output.txt` (if using file mode)

Check the output file to see:
- Summary table with events per venue
- Any errors encountered
- Full event listings organized by date

When you're ready to send emails, change `mode: "email"` in config.yaml and run again!

## Step 5: Set Up Daily Automation

Choose one of these methods:

### Option A: Run the Scheduler (Recommended)

```bash
cd src
python scheduler.py
```

Keep this running in a terminal. It will send emails daily at the time configured in `config.yaml`.

### Option B: Use Cron (Mac/Linux)

```bash
crontab -e
```

Add this line (replace with your actual path):
```
0 9 * * * cd /path/to/Music\ Finder/src && python3 main.py
```

This runs daily at 9 AM.

## Troubleshooting

### Check the Diagnostics

The app creates two helpful files:
- `events_output.txt` - Summary table and full event listings
- `scraper_diagnostics.log` - Detailed scraping diagnostics

Look at these files to understand what's happening!

### Email Not Sending?

- Make sure you're using an App Password, not your regular Gmail password
- Check that 2-factor authentication is enabled on your Google account
- Verify there are no typos in your email configuration
- Try `mode: "file"` first to verify scraping works before adding email

### No Events Found?

- Check `events_output.txt` to see which venues had errors
- Look at `scraper_diagnostics.log` for detailed error messages
- This is normal if there are currently no upcoming events at the venues
- Try increasing `days_ahead` in `config.yaml` to look further ahead
- Run `test_scrapers.py` to test each venue individually

### Scraper Errors?

- Check `scraper_diagnostics.log` for specific error messages
- Venue websites may change their structure over time
- Check if the venue website is accessible in your browser
- Some venues may be temporarily down
- The log shows HTTP status codes and page structure

## What's Next?

- Customize the email format in `src/email_sender.py`
- Add more venues by creating new scrapers in `src/scrapers/`
- Adjust the schedule in `config.yaml`
- Set up a background service (see README.md)

## Support

For more detailed information, see the full README.md file.
