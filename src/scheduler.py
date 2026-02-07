#!/usr/bin/env python3
"""
Scheduler for running the music finder daily.
"""

import schedule
import time
import yaml
import os
import logging
from main import load_config, scrape_all_venues, send_daily_email, write_events_to_file


def scheduled_job():
    """Job to run on schedule."""
    print(f"\n{'='*60}")
    print(f"Running scheduled job at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    # Initialize logger (use BaseScraper's class method; don't instantiate abstract class)
    from scrapers.base_scraper import BaseScraper
    logger = BaseScraper._get_logger()

    # Load configuration
    config_path = os.path.join(parent_dir, 'config.yaml')
    config = load_config(config_path)
    logger.info(f"Scheduled job: Configuration loaded from: {config_path}")

    # Scrape all venues
    events, venue_status = scrape_all_venues(config)

    # Determine output mode from config (same as main.py)
    output_config = config.get('output', {})
    output_mode = output_config.get('mode', 'file').lower()
    output_file = output_config.get('output_file', 'events_output.txt')
    
    logger.info(f"Scheduled job: Output mode: {output_mode}")
    
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
            logger.info("Scheduled job: Email sent successfully")
        else:
            print("\n✗ Failed to send email. Check your configuration.")
            logger.warning("Scheduled job: Email sending failed")
    
    if output_mode in ['file', 'both']:
        print("\n" + "=" * 60)
        print("Writing events to file...")
        print("=" * 60 + "\n")
        
        file_success = write_events_to_file(events, venue_status, output_file, logger)
        
        if file_success:
            logger.info("Scheduled job: Events written to file successfully")
    
    # Determine overall success
    if output_mode == 'both':
        success = email_success and file_success
    elif output_mode == 'email':
        success = email_success
    else:  # file mode
        success = file_success

    if success:
        print(f"\n✓ Daily job completed successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Scheduled job completed successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n✗ Daily job failed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.error(f"Scheduled job failed at {time.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main entry point for scheduler."""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    # Load configuration
    config_path = os.path.join(parent_dir, 'config.yaml')
    config = load_config(config_path)

    # Get scheduled time from config
    daily_time = config['schedule']['daily_time']

    print(f"{'='*60}")
    print(f"Music Finder Scheduler Started")
    print(f"{'='*60}")
    print(f"Daily email will be sent at: {daily_time}")
    print(f"Press Ctrl+C to stop the scheduler")
    print(f"{'='*60}\n")

    # Schedule the job
    schedule.every().day.at(daily_time).do(scheduled_job)

    # Run immediately on startup (optional - comment out if you don't want this)
    print("Running initial scrape...")
    scheduled_job()

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user.")
    except Exception as e:
        print(f"\n\nScheduler error: {e}")
