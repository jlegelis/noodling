#!/usr/bin/env python3
"""
Music Finder - Boston Live Music Event Scraper and Notifier
"""

import yaml
import os
import sys
import logging
from typing import List
from datetime import datetime
from collections import defaultdict

from scrapers import (
    PloughAndStarsScraper,
    TheBurrenScraper,
    BeehiveBostonScraper,
    MadMonkfishScraper,
    WallysCafeScraper,
    LizardLoungeScraper
)
from scrapers.base_scraper import Event
from email_sender import EmailSender


def load_config(config_path: str = 'config.yaml') -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        print("Please create a config.yaml file based on config.yaml.example")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file: {e}")
        sys.exit(1)


def scrape_all_venues(config: dict) -> tuple[List[Event], dict]:
    """
    Scrape events from all configured venues.
    
    Returns:
        tuple: (list of events, dict of venue status with keys: venue_name -> {'count': int, 'error': str or None})
    """
    scraping_config = config.get('scraping', {})
    user_agent = scraping_config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    timeout = scraping_config.get('timeout', 10)
    days_ahead = scraping_config.get('days_ahead', 7)

    # Initialize all scrapers
    scrapers = [
        PloughAndStarsScraper(user_agent, timeout),
        TheBurrenScraper(user_agent, timeout),
        BeehiveBostonScraper(user_agent, timeout),
        MadMonkfishScraper(user_agent, timeout),
        WallysCafeScraper(user_agent, timeout),
        LizardLoungeScraper(user_agent, timeout)
    ]

    all_events = []
    venue_status = {}  # venue_name -> {'count': int, 'error': str or None}

    print(f"\n{'='*60}")
    print(f"Scraping events for the next {days_ahead} days...")
    print(f"{'='*60}\n")

    for scraper in scrapers:
        print(f"Scraping {scraper.venue_name}...", end=' ')
        try:
            events = scraper.scrape_events(days_ahead)
            all_events.extend(events)
            venue_status[scraper.venue_name] = {'count': len(events), 'error': None}
            print(f"✓ Found {len(events)} events")
        except Exception as e:
            error_msg = f"Error scraping {scraper.venue_name}: {type(e).__name__}: {e}"
            print(f"✗ Error: {e}")
            scraper.logger.error(error_msg, exc_info=True)
            venue_status[scraper.venue_name] = {'count': 0, 'error': str(e)}

    print(f"\n{'='*60}")
    print(f"Total events found: {len(all_events)}")
    print(f"{'='*60}\n")

    return all_events, venue_status


def send_daily_email(config: dict, events: List[Event]) -> bool:
    """Send daily email with event information."""
    email_config = config.get('email', {})
    
    # Validate required email config
    required_email_keys = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password', 'recipients', 'subject']
    missing_keys = [key for key in required_email_keys if key not in email_config]
    if missing_keys:
        logger = logging.getLogger('scraper')
        logger.error(f"Missing required email configuration keys: {', '.join(missing_keys)}")
        print(f"Error: Missing required email configuration keys: {', '.join(missing_keys)}")
        return False

    sender = EmailSender(
        smtp_server=email_config['smtp_server'],
        smtp_port=email_config['smtp_port'],
        sender_email=email_config['sender_email'],
        sender_password=email_config['sender_password'],
        recipients=email_config['recipients'],
        subject=email_config['subject']
    )

    return sender.send_email(events)


def write_events_to_file(events: List[Event], venue_status: dict, output_file: str, logger: logging.Logger) -> bool:
    """Write events to a text file for review."""
    try:
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("Boston Live Music Events\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Write summary table with all venues
            f.write("Summary by Venue\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Venue':<50} {'Events':>10} {'Status':>10}\n")
            f.write("-" * 80 + "\n")
            
            # Sort venues alphabetically for consistent output
            for venue in sorted(venue_status.keys()):
                status_info = venue_status[venue]
                count = status_info['count']
                error = status_info.get('error')
                
                if error:
                    status_str = "ERROR"
                elif count == 0:
                    status_str = "0 events"
                else:
                    status_str = "OK"
                
                f.write(f"{venue:<50} {count:>10} {status_str:>10}\n")
            
            f.write("-" * 80 + "\n")
            f.write(f"{'Total':<50} {len(events):>10}\n")
            f.write("=" * 80 + "\n\n")
            
            if not events:
                f.write("No events found for the upcoming days.\n")
            else:
                # Group events by date, then by venue
                events_by_date = defaultdict(lambda: defaultdict(list))
                for event in sorted(events, key=lambda e: (e.date, e.venue)):
                    date_str = event.date.strftime('%A, %B %d, %Y')
                    events_by_date[date_str][event.venue].append(event)

                # Write events grouped by date and venue
                for date_str in sorted(events_by_date.keys(), key=lambda d: datetime.strptime(d, '%A, %B %d, %Y')):
                    f.write(f"\n{date_str}\n")
                    f.write("-" * 80 + "\n")

                    for venue in sorted(events_by_date[date_str].keys()):
                        venue_events = events_by_date[date_str][venue]

                        if len(venue_events) == 1:
                            event = venue_events[0]
                            f.write(f"\n  {venue}: {event.title}\n")
                            if event.time:
                                f.write(f"    Time: {event.time}\n")
                            if event.genre:
                                f.write(f"    Genre: {event.genre}\n")
                            if event.url:
                                f.write(f"    URL: {event.url}\n")
                        else:
                            f.write(f"\n  {venue}:\n")
                            for event in venue_events:
                                f.write(f"    • {event.title}\n")
                                if event.time:
                                    f.write(f"      Time: {event.time}\n")
                                if event.genre:
                                    f.write(f"      Genre: {event.genre}\n")
                                if event.url:
                                    f.write(f"      URL: {event.url}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"Total events: {len(events)}\n")
                f.write("=" * 80 + "\n")
        
        logger.info(f"Events written to file: {output_path}")
        print(f"\n✓ Events written to file: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error writing events to file: {type(e).__name__}: {e}", exc_info=True)
        print(f"\n✗ Failed to write events to file: {e}")
        return False


def main():
    """Main entry point."""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    # Initialize logging by creating a scraper instance (this sets up the logger)
    # We need to do this before logging, so create a temporary scraper
    from scrapers.base_scraper import BaseScraper
    _temp_scraper = BaseScraper(
        venue_name="Music Finder",
        url="",
        user_agent="Mozilla/5.0",
        timeout=10
    )
    logger = _temp_scraper.logger
    
    log_file = os.path.join(parent_dir, 'scraper_diagnostics.log')
    logger.info("=" * 80)
    logger.info("Music Finder - Starting scraping session")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 80)

    # Load configuration
    config_path = os.path.join(parent_dir, 'config.yaml')
    config = load_config(config_path)
    logger.info(f"Configuration loaded from: {config_path}")
    
    # Validate required config sections
    required_sections = ['scraping', 'email', 'schedule']
    missing_sections = [section for section in required_sections if section not in config]
    if missing_sections:
        logger.error(f"Missing required configuration sections: {', '.join(missing_sections)}")
        print(f"Error: Missing required configuration sections: {', '.join(missing_sections)}")
        sys.exit(1)

    # Scrape all venues
    events, venue_status = scrape_all_venues(config)

    # Print events to console (grouped by date and venue)
    if events:
        print("\nUpcoming Events:")
        print("-" * 60)

        # Group events by date first, then by venue
        events_by_date = defaultdict(lambda: defaultdict(list))
        for event in sorted(events, key=lambda e: (e.date, e.venue)):
            date_str = event.date.strftime('%A, %B %d, %Y')
            events_by_date[date_str][event.venue].append(event)

        # Print events grouped by date and venue
        for date_str in sorted(events_by_date.keys(), key=lambda d: datetime.strptime(d, '%A, %B %d, %Y')):
            print(f"\n{date_str}")

            for venue in sorted(events_by_date[date_str].keys()):
                venue_events = events_by_date[date_str][venue]

                if len(venue_events) == 1:
                    # Single event - simple format
                    event = venue_events[0]
                    print(f"  {venue}: {event.title}")
                    if event.time:
                        print(f"    Time: {event.time}")
                    if event.genre:
                        print(f"    Genre: {event.genre}")
                else:
                    # Multiple events - consolidated format
                    print(f"  {venue}:")
                    for event in venue_events:
                        print(f"    • {event.title}")
                        if event.time:
                            print(f"      Time: {event.time}")
                        if event.genre:
                            print(f"      Genre: {event.genre}")
    else:
        print("\nNo events found.")

    # Determine output mode from config
    output_config = config.get('output', {})
    output_mode = output_config.get('mode', 'file').lower()
    output_file = output_config.get('output_file', 'events_output.txt')
    
    logger.info(f"Output mode: {output_mode}")
    
    # Handle output based on mode
    email_success = True
    file_success = True
    
    if output_mode in ['email', 'both']:
        print("\n" + "=" * 60)
        print("Sending email notification...")
        print("=" * 60 + "\n")
        
        email_success = send_daily_email(config, events)
        
        if email_success:
            print("\n✓ Email sent successfully!")
        else:
            print("\n✗ Failed to send email. Check your configuration.")
            logger.warning("Email sending failed")
    
    if output_mode in ['file', 'both']:
        print("\n" + "=" * 60)
        print("Writing events to file...")
        print("=" * 60 + "\n")
        
        file_success = write_events_to_file(events, venue_status, output_file, logger)
    
    # Exit with error code if both failed (only relevant if mode is 'both')
    if output_mode == 'both' and not email_success and not file_success:
        logger.error("Both email and file output failed")
        sys.exit(1)
    elif output_mode == 'email' and not email_success:
        logger.error("Email output failed")
        sys.exit(1)
    elif output_mode == 'file' and not file_success:
        logger.error("File output failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
