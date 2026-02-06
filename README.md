# Music Finder

A Python application that scrapes live music events from Boston area venues and sends daily email notifications with upcoming shows.

## Features

- Scrapes events from 6 Boston area music venues
- Multiple output modes: email, file, or both
- Sends formatted HTML and plain text email notifications
- File output for diagnostics and testing
- Detailed logging with diagnostic information
- Configurable scheduling for daily automated emails
- Clean, organized event listings by date and venue
- Robust error handling with per-venue status tracking
- Comprehensive logging for troubleshooting

## Supported Venues

1. **Plough and Stars** - Events Calendar
2. **The Burren** - Music Schedule (Front Room & Back Room)
3. **Beehive Boston** - Tockify Calendar (switched from main site)
4. **The Mad Monkfish** - Jazz Schedule
5. **Wally's Cafe** - Live Music Schedule
6. **Lizard Lounge** - Calendar

**All 6 venues are now working!** ✅

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your email settings in `config.yaml`:
```bash
cp config.yaml config.yaml
```

4. Edit `config.yaml` with your settings:
   - **Output Mode**: Choose "file", "email", or "both"
   - **Email Configuration**: Update SMTP settings and credentials
   - **Recipients**: Add email addresses to receive notifications
   - **Schedule**: Set the time for daily emails (24-hour format)
   - **Scraping**: Adjust days ahead to look for events

## Configuration

### Email Settings (Gmail Example)

For Gmail, you need to use an App Password:

1. Enable 2-factor authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use this app password in `config.yaml`

Example configuration:
```yaml
output:
  mode: "file"  # Change to "email" or "both" when configured
  output_file: "events_output.txt"

email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  sender_email: "your-email@gmail.com"
  sender_password: "your-app-specific-password"
  recipients:
    - "recipient1@example.com"
    - "recipient2@example.com"
  subject: "Today's Live Music in Boston"
```

### Other Email Providers

For other providers, update the SMTP server and port:

- **Outlook/Hotmail**: `smtp.office365.com`, port 587
- **Yahoo**: `smtp.mail.yahoo.com`, port 587
- **Custom SMTP**: Use your provider's settings

## Usage

### One-Time Run

To scrape venues and output results:

```bash
cd src
python main.py
```

This will:
1. Scrape all configured venues
2. Display events in the console
3. Output based on `config.yaml` mode:
   - `mode: "file"` - Write to text file (good for testing)
   - `mode: "email"` - Send email to configured recipients
   - `mode: "both"` - Write to file AND send email

The output file includes a summary table showing events found per venue and any errors.

### Scheduled Daily Emails

To run the scheduler that sends emails daily at the configured time:

```bash
cd src
python scheduler.py
```

The scheduler will:
1. Run an initial scrape immediately
2. Schedule daily scrapes at the time specified in `config.yaml`
3. Continue running until stopped with Ctrl+C

### Running as a Background Service

#### Option 1: Using nohup (Unix/Linux/Mac)

```bash
cd src
nohup python scheduler.py > ../logs/music_finder.log 2>&1 &
```

#### Option 2: Using screen (Unix/Linux/Mac)

```bash
screen -S music_finder
cd src
python scheduler.py
# Press Ctrl+A then D to detach
```

To reattach:
```bash
screen -r music_finder
```

#### Option 3: Using systemd (Linux)

Create a service file at `/etc/systemd/system/music-finder.service`:

```ini
[Unit]
Description=Music Finder - Boston Live Music Scraper
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Music Finder/src
ExecStart=/usr/bin/python3 /path/to/Music Finder/src/scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable music-finder
sudo systemctl start music-finder
```

#### Option 4: Using cron (Unix/Linux/Mac)

Edit your crontab:
```bash
crontab -e
```

Add a line to run daily at 9 AM:
```
0 9 * * * cd /path/to/Music\ Finder/src && /usr/bin/python3 main.py >> ../logs/music_finder.log 2>&1
```

## Project Structure

```
Music Finder/
├── README.md
├── requirements.txt
├── config.yaml
├── music_venues_to_crawl.md
└── src/
    ├── __init__.py
    ├── main.py              # Main script for one-time runs
    ├── scheduler.py         # Scheduler for daily automated runs
    ├── email_sender.py      # Email notification handler
    └── scrapers/
        ├── __init__.py
        ├── base_scraper.py          # Base scraper class and Event model
        ├── plough_and_stars.py      # Plough and Stars scraper
        ├── the_burren.py            # The Burren scraper
        ├── beehive_boston.py        # Beehive Boston scraper
        ├── mad_monkfish.py          # Mad Monkfish scraper
        ├── wallys_cafe.py           # Wally's Cafe scraper
        └── lizard_lounge.py         # Lizard Lounge scraper
```

## Customization

### Adding More Venues

To add a new venue:

1. Create a new scraper in `src/scrapers/` following the pattern of existing scrapers
2. Inherit from `BaseScraper` and implement the `scrape_events()` method
3. Add the scraper to `src/scrapers/__init__.py`
4. Import and instantiate it in `src/main.py`

Example:
```python
from .base_scraper import BaseScraper, Event

class NewVenueScraper(BaseScraper):
    def __init__(self, user_agent: str, timeout: int = 10):
        super().__init__(
            venue_name="New Venue Name",
            url="https://venue-website.com/events",
            user_agent=user_agent,
            timeout=timeout
        )

    def scrape_events(self, days_ahead: int = 7) -> List[Event]:
        # Implement scraping logic
        pass
```

### Modifying Email Format

Edit the `format_events_html()` or `format_events_plain()` methods in `src/email_sender.py` to customize the email layout and styling.

## Troubleshooting

### Diagnostic Logging

The app creates a `scraper_diagnostics.log` file with detailed information about:
- Each HTTP request and response
- Page structure analysis
- Parsing attempts and results
- Error messages with stack traces

Check this log file when scrapers aren't finding events.

### No Events Found

- Check `scraper_diagnostics.log` for detailed error messages
- Check `events_output.txt` (if using file mode) for per-venue status
- Verify the venue websites are accessible in your browser
- Check if the venue has changed their website structure
- Increase the `timeout` value in `config.yaml`
- Run with `mode: "file"` to see the summary table without sending emails

### Email Not Sending

- Verify SMTP credentials in `config.yaml`
- For Gmail, ensure you're using an App Password, not your regular password
- Check that 2-factor authentication is enabled (required for Gmail App Passwords)
- Verify your firewall allows outbound connections on the SMTP port
- Check for typos in email addresses

### Scheduler Not Running

- Ensure the scheduler.py process is running (`ps aux | grep scheduler`)
- Check logs for error messages
- Verify the scheduled time format in config.yaml is correct (24-hour format, e.g., "09:00")

## Notes

- Web scraping depends on the structure of venue websites, which may change over time
- Some venues may have generic schedules rather than specific events (e.g., Wally's Cafe)
- The scraper respects website structures and doesn't overload servers
- Rate limiting and polite scraping practices are built in

## License

This project is for personal use. Please respect the terms of service of the venues being scraped.

## Contributing

Feel free to submit issues or pull requests to improve the scrapers or add new venues.
