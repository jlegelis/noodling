from typing import List
from datetime import datetime, timedelta
from .base_scraper import BaseScraper, Event
import re
import json


class MadMonkfishScraper(BaseScraper):
    """Scraper for The Mad Monkfish jazz schedule."""

    def __init__(self, user_agent: str, timeout: int = 10):
        super().__init__(
            venue_name="The Mad Monkfish",
            url="https://www.themadmonkfish.com/jazz-schedule/",
            user_agent=user_agent,
            timeout=timeout
        )

    def scrape_events(self, days_ahead: int = 7) -> List[Event]:
        """Scrape events from The Mad Monkfish jazz schedule."""
        self.log_scraping_start(days_ahead)
        events = []
        soup = self.fetch_page()

        if not soup:
            self.log_scraping_result(0, "Failed to fetch page")
            return events

        # First try: Look for JSON-LD structured data
        scripts = soup.find_all('script', type='application/ld+json')
        self.logger.debug(f"[{self.venue_name}] Found {len(scripts)} JSON-LD scripts")

        json_events_found = 0
        for script in scripts:
            try:
                if script.string:
                    data = json.loads(script.string)

                    # Check if this is event data
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get('@type') == 'Event':
                                event = self._parse_json_ld_event(item)
                                if event:
                                    events.append(event)
                                    json_events_found += 1
                    elif isinstance(data, dict) and data.get('@type') == 'Event':
                        event = self._parse_json_ld_event(data)
                        if event:
                            events.append(event)
                            json_events_found += 1

            except json.JSONDecodeError as e:
                self.logger.debug(f"[{self.venue_name}] Error parsing JSON-LD: {e}")

        self.logger.debug(f"[{self.venue_name}] Found {json_events_found} events from JSON-LD")

        # Second try: Parse from text content (looking for patterns like "2/5 Matt Savage Quartet 7pm")
        if not events:
            page_text = soup.get_text()
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]

            # Pattern for dates like "2/5", "2/14"
            date_pattern = re.compile(r'\b(\d{1,2})/(\d{1,2})\b')

            current_year = datetime.now().year
            current_month = datetime.now().month

            for line in lines:
                # Look for date at start of line
                date_match = date_pattern.match(line)

                if date_match:
                    month = int(date_match.group(1))
                    day = int(date_match.group(2))

                    try:
                        event_date = datetime(current_year, month, day)

                        # Extract the rest of the line as event info
                        event_info = line[date_match.end():].strip()

                        if event_info:
                            # Try to extract time
                            time_match = re.search(r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm))\b', event_info, re.IGNORECASE)
                            time_str = time_match.group(1) if time_match else None

                            # Clean up title (remove time if found)
                            if time_match:
                                title = event_info[:time_match.start()].strip() + ' ' + event_info[time_match.end():].strip()
                                title = title.strip()
                            else:
                                title = event_info

                            if title:
                                events.append(Event(
                                    venue=self.venue_name,
                                    date=event_date,
                                    title=title,
                                    time=time_str,
                                    genre="Jazz"
                                ))
                                self.logger.debug(f"[{self.venue_name}] Added event from text: {title}")

                    except ValueError:
                        continue

        # Filter to only events within the days_ahead range
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today + timedelta(days=days_ahead)
        filtered_events = self.filter_events_by_date(events, today, end_date)

        self.log_scraping_result(
            len(filtered_events),
            f"Found {json_events_found} from JSON-LD, {len(events) - json_events_found} from text parsing"
        )
        return filtered_events

    def _parse_json_ld_event(self, data: dict) -> Event:
        """Parse a JSON-LD event object."""
        try:
            title = data.get('name', 'Event')

            # Parse date
            start_date_str = data.get('startDate')
            if start_date_str:
                # Try to parse ISO format
                event_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                event_date = event_date.replace(tzinfo=None)  # Remove timezone
            else:
                return None

            # Extract time if available
            time_str = None
            if 'T' in start_date_str:
                time_str = event_date.strftime('%I:%M %p')

            # Get URL if available
            event_url = data.get('url')

            return Event(
                venue=self.venue_name,
                date=event_date,
                title=title,
                time=time_str,
                genre="Jazz",
                url=event_url
            )
        except Exception as e:
            self.logger.debug(f"[{self.venue_name}] Error parsing event: {e}")
            return None
