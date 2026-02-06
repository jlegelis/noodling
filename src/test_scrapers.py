#!/usr/bin/env python3
"""
Test script for individual venue scrapers.
Useful for debugging scraper issues.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers import (
    PloughAndStarsScraper,
    TheBurrenScraper,
    BeehiveBostonScraper,
    MadMonkfishScraper,
    WallysCafeScraper,
    LizardLoungeScraper
)


def test_scraper(scraper, venue_name):
    """Test a single scraper."""
    print(f"\n{'='*60}")
    print(f"Testing {venue_name}")
    print(f"{'='*60}")

    try:
        events = scraper.scrape_events(days_ahead=7)
        print(f"✓ Successfully scraped {len(events)} events\n")

        if events:
            print("Sample events:")
            for event in events[:5]:  # Show first 5 events
                print(f"\n  Date: {event.date.strftime('%A, %B %d, %Y')}")
                print(f"  Title: {event.title}")
                if event.time:
                    print(f"  Time: {event.time}")
                if event.genre:
                    print(f"  Genre: {event.genre}")
                if event.url:
                    print(f"  URL: {event.url}")

            if len(events) > 5:
                print(f"\n  ... and {len(events) - 5} more events")
        else:
            print("No events found (this might be normal if there are no upcoming events)")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Test all scrapers."""
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    timeout = 10

    scrapers = [
        (PloughAndStarsScraper(user_agent, timeout), "Plough and Stars"),
        (TheBurrenScraper(user_agent, timeout), "The Burren"),
        (BeehiveBostonScraper(user_agent, timeout), "Beehive Boston"),
        (MadMonkfishScraper(user_agent, timeout), "The Mad Monkfish"),
        (WallysCafeScraper(user_agent, timeout), "Wally's Cafe"),
        (LizardLoungeScraper(user_agent, timeout), "Lizard Lounge")
    ]

    print("\nMusic Finder - Scraper Test Suite")
    print("="*60)

    for scraper, name in scrapers:
        test_scraper(scraper, name)

    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
