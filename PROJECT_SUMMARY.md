# Music Finder - Project Summary

## Overview

A complete Python application that automatically scrapes live music events from 6 Boston area venues and sends daily HTML email notifications.

## What's Included

### Core Application Files

1. **src/main.py** - Main script for one-time event scraping and email sending
2. **src/scheduler.py** - Automated daily scheduler
3. **src/email_sender.py** - Email notification system with HTML and plain text formatting
4. **src/test_scrapers.py** - Testing utility for debugging individual scrapers

### Venue Scrapers

Each venue has a custom scraper that handles its unique website structure:

1. **Plough and Stars** - Calendar-based scraper
2. **The Burren** - Front Room/Back Room schedule parser
3. **Beehive Boston** - Event calendar scraper
4. **The Mad Monkfish** - Jazz schedule scraper
5. **Wally's Cafe** - Recurring schedule generator
6. **Lizard Lounge** - Calendar scraper

All scrapers inherit from a base class (`base_scraper.py`) that provides:
- HTTP request handling with user agent
- Event data model
- Date filtering utilities
- Error handling

### Configuration

- **config.yaml** - Main configuration (email, SMTP, schedule, scraping settings)
- **config.yaml.example** - Template for initial setup
- **requirements.txt** - Python dependencies

### Documentation

- **README.md** - Comprehensive documentation
- **QUICKSTART.md** - 5-minute setup guide
- **PROJECT_SUMMARY.md** - This file
- **music_venues_to_crawl.md** - List of venues (your original file)

### Development Files

- **.gitignore** - Protects sensitive config files from git
- **src/__init__.py** & **src/scrapers/__init__.py** - Python package files

## Project Structure

```
Music Finder/
├── README.md                    # Full documentation
├── QUICKSTART.md               # Quick setup guide
├── PROJECT_SUMMARY.md          # This file
├── requirements.txt            # Python dependencies
├── config.yaml                 # Your configuration (not in git)
├── config.yaml.example         # Configuration template
├── music_venues_to_crawl.md   # Venue list
├── .gitignore                  # Git ignore rules
└── src/
    ├── __init__.py
    ├── main.py                 # Main execution script
    ├── scheduler.py            # Daily automation
    ├── email_sender.py         # Email handler
    ├── test_scrapers.py        # Testing utility
    └── scrapers/
        ├── __init__.py
        ├── base_scraper.py     # Base class and Event model
        ├── plough_and_stars.py
        ├── the_burren.py
        ├── beehive_boston.py
        ├── mad_monkfish.py
        ├── wallys_cafe.py
        └── lizard_lounge.py
```

## Key Features

### Web Scraping
- Handles diverse website structures (calendars, schedules, listings)
- Robust HTML parsing with BeautifulSoup
- Configurable user agent and timeout
- Date extraction from multiple formats
- Error handling per venue (one failure doesn't break others)

### Email Notifications
- Beautiful HTML emails with styled event listings
- Plain text fallback for compatibility
- Events grouped by date
- Includes venue, title, time, genre, and links
- Multiple recipient support

### Scheduling
- Daily automated execution
- Configurable send time
- Continuous background operation
- Initial run on startup
- Graceful shutdown handling

### Configuration
- YAML-based configuration
- Email settings (SMTP, credentials, recipients)
- Scraping parameters (user agent, timeout, days ahead)
- Schedule settings (daily send time)

## Technology Stack

- **Python 3.8+**
- **requests** - HTTP library for web scraping
- **beautifulsoup4** - HTML parsing
- **lxml** - Fast XML/HTML parser
- **python-dateutil** - Date parsing utilities
- **pyyaml** - YAML configuration
- **schedule** - Job scheduling

## Usage Modes

### 1. One-Time Run
```bash
cd src && python main.py
```
Scrapes all venues and sends one email immediately.

### 2. Continuous Scheduler
```bash
cd src && python scheduler.py
```
Runs continuously, sending emails daily at configured time.

### 3. Testing Mode
```bash
cd src && python test_scrapers.py
```
Tests each scraper individually without sending emails.

## Customization Points

### Easy Customizations
- Add/remove recipient email addresses in config.yaml
- Change send time in config.yaml
- Adjust days to look ahead in config.yaml
- Modify email subject line in config.yaml

### Medium Customizations
- Edit HTML email template in `src/email_sender.py`
- Modify event display format
- Add custom CSS styling to emails

### Advanced Customizations
- Add new venue scrapers in `src/scrapers/`
- Modify scraping logic for existing venues
- Implement additional features (filtering by genre, etc.)
- Add database storage for historical tracking

## Setup Requirements

1. Python 3.8 or higher
2. Gmail account with App Password (or other SMTP service)
3. Internet connection for scraping
4. (Optional) Server or computer for continuous operation

## Deployment Options

1. **Local Development** - Run manually as needed
2. **Background Process** - Use nohup or screen
3. **Cron Job** - Schedule via crontab
4. **Systemd Service** - Linux system service
5. **Cloud VM** - AWS EC2, DigitalOcean, etc.
6. **Docker Container** - Containerized deployment

## Maintenance

### Regular Tasks
- Monitor email delivery
- Check for venue website changes
- Update scrapers if websites change structure

### Periodic Tasks
- Update Python dependencies: `pip install -r requirements.txt --upgrade`
- Review and update venue list
- Add new venues as discovered

## Future Enhancement Ideas

- Add database for event history
- Create web dashboard for viewing events
- Add filtering (by genre, venue, date range)
- Implement event deduplication
- Add support for more cities
- Create mobile app companion
- Add social media integration
- Implement event recommendations
- Add calendar export (ICS format)

## Notes

- Web scraping depends on website structure (may break if sites change)
- Some venues show generic schedules vs. specific events
- Rate limiting is built in (polite scraping)
- Email sending uses standard SMTP (works with most providers)
- All times are in local system timezone

## Support

For issues or questions:
1. Check README.md for detailed documentation
2. Run test_scrapers.py to debug scraping issues
3. Verify config.yaml settings
4. Check email credentials and SMTP settings

## Success Criteria

✓ Scrapes 6 Boston area music venues
✓ Extracts event details (date, time, title, genre, URL)
✓ Sends formatted HTML emails
✓ Supports multiple recipients
✓ Runs on configurable schedule
✓ Handles errors gracefully
✓ Easy to configure and deploy
✓ Well documented
✓ Extensible architecture

---

Created: February 3, 2026
Version: 1.0
