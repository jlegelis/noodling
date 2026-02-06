from typing import List
from datetime import datetime, timedelta
from .base_scraper import BaseScraper, Event
import re


class PloughAndStarsScraper(BaseScraper):
    """Scraper for Plough and Stars calendar."""

    def __init__(self, user_agent: str, timeout: int = 10):
        super().__init__(
            venue_name="Plough and Stars",
            url="https://calendar.ploughandstars.com/events/calendar",
            user_agent=user_agent,
            timeout=timeout
        )

    def scrape_events(self, days_ahead: int = 7) -> List[Event]:
        """Scrape events from Plough and Stars calendar."""
        self.log_scraping_start(days_ahead)
        events = []
        soup = self.fetch_page()

        if not soup:
            self.log_scraping_result(0, "Failed to fetch page")
            return events

        # Get the full text content and split by lines
        page_text = soup.get_text()
        lines = page_text.split('\n')

        current_year = datetime.now().year

        # Pattern for dates like "Sun Feb 1"
        date_pattern = re.compile(
            r'^(Sun|Mon|Tue|Wed|Thu|Fri|Sat)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})',
            re.IGNORECASE
        )

        # Pattern for times like "7pm", "10pm", "4-6pm"
        time_pattern = re.compile(r'(\d{1,2}(?:-\d{1,2})?(?::\d{2})?\s*(?:am|pm))', re.IGNORECASE)

        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }

        self.logger.debug(f"[{self.venue_name}] Processing {len(lines)} lines")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts with a date
            date_match = date_pattern.match(line)

            if date_match:
                dow = date_match.group(1)
                month_str = date_match.group(2)
                day_str = date_match.group(3)

                month_num = month_map.get(month_str.lower()[:3])
                if not month_num:
                    continue

                try:
                    event_date = datetime(current_year, month_num, int(day_str))
                except ValueError:
                    continue

                # Get the rest of the line after the date
                event_text = line[date_match.end():].strip()

                if not event_text:
                    self.logger.debug(f"[{self.venue_name}] Date {event_date.strftime('%Y-%m-%d')} has no events")
                    continue

                self.logger.debug(f"[{self.venue_name}] Date {event_date.strftime('%Y-%m-%d')}: '{event_text}'")

                # Find all time mentions and their associated event names
                time_matches = list(time_pattern.finditer(event_text))

                if not time_matches:
                    # No time found, but there's event text
                    events.append(Event(
                        venue=self.venue_name,
                        date=event_date,
                        title=event_text
                    ))
                    self.logger.debug(f"[{self.venue_name}]   Event (no time): {event_text}")
                else:
                    # Process each time and extract the event name
                    for i, time_match in enumerate(time_matches):
                        time_str = time_match.group(1)

                        # Get the event name: text between this time and the next time (or end)
                        start_pos = time_match.end()
                        if i + 1 < len(time_matches):
                            end_pos = time_matches[i + 1].start()
                        else:
                            end_pos = len(event_text)

                        event_title = event_text[start_pos:end_pos].strip()

                        if event_title:
                            events.append(Event(
                                venue=self.venue_name,
                                date=event_date,
                                title=event_title,
                                time=time_str
                            ))
                            self.logger.debug(f"[{self.venue_name}]   Event: {time_str} - {event_title}")

        self.logger.debug(f"[{self.venue_name}] Total events before filtering: {len(events)}")

        # Filter to only events within the days_ahead range
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today + timedelta(days=days_ahead)
        filtered_events = self.filter_events_by_date(events, today, end_date)

        self.log_scraping_result(len(filtered_events), f"Extracted {len(events)} total events")
        return filtered_events
