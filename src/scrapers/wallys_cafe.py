from typing import List
from datetime import datetime, timedelta
from .base_scraper import BaseScraper, Event


class WallysCafeScraper(BaseScraper):
    """Scraper for Wally's Cafe schedule."""

    def __init__(self, user_agent: str, timeout: int = 10):
        super().__init__(
            venue_name="Wally's Cafe",
            url="https://wallyscafe.com/live-music-schedule/",
            user_agent=user_agent,
            timeout=timeout
        )

    def scrape_events(self, days_ahead: int = 7) -> List[Event]:
        """
        Scrape events from Wally's Cafe schedule.

        Note: Based on initial inspection, Wally's Cafe shows a general schedule
        rather than specific events with artists and dates. This scraper creates
        generic recurring events based on their published schedule.
        """
        self.log_scraping_start(days_ahead)
        events = []
        soup = self.fetch_page()

        if not soup:
            self.log_scraping_result(0, "Failed to fetch page")
            return events

        # Wally's has a general schedule rather than specific events
        # We'll create recurring events for the upcoming week

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Based on the page structure, they have:
        # - Evening Music: 7-9 PM, Wed-Sat
        # - Night Music: 10 PM-Midnight, Wed-Sun (Tue at 8 PM)

        for day_offset in range(days_ahead):
            current_date = today + timedelta(days=day_offset)
            day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday

            # Evening Music (Wed-Sat = 2,3,4,5)
            if day_of_week in [2, 3, 4, 5]:
                events.append(Event(
                    venue=self.venue_name,
                    date=current_date,
                    title="Evening Music Session",
                    time="7:00 PM - 9:00 PM",
                    genre="Jazz"
                ))

            # Night Music (Wed-Sun = 2,3,4,5,6)
            if day_of_week in [2, 3, 4, 5, 6]:
                events.append(Event(
                    venue=self.venue_name,
                    date=current_date,
                    title="Night Music Session",
                    time="10:00 PM - 12:00 AM",
                    genre="Jazz"
                ))

            # Tuesday Night Music (1=Tuesday)
            if day_of_week == 1:
                events.append(Event(
                    venue=self.venue_name,
                    date=current_date,
                    title="Night Music Session",
                    time="8:00 PM - 12:00 AM",
                    genre="Jazz"
                ))

        # Try to scrape actual event details if they exist
        # Look for any specific event listings
        event_containers = soup.find_all(['div', 'article'], class_=lambda x: x and 'event' in x.lower())
        self.logger.debug(f"[{self.venue_name}] Found {len(event_containers)} event containers, created {len(events)} generic events")

        if event_containers:
            # If we find specific events, clear the generic ones and use these instead
            specific_events = []
            for container in event_containers:
                # Extract event details
                # This is a fallback in case the site structure includes specific events
                title_elem = container.find(['h1', 'h2', 'h3', 'h4'])
                if title_elem:
                    event_title = title_elem.get_text(strip=True)

                    # Try to find date and time
                    # Add parsing logic here if specific events are found

                    # For now, we'll stick with the generic schedule above

        self.log_scraping_result(len(events), f"Created {len(events)} recurring schedule events")
        return events
