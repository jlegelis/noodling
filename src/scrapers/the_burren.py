from typing import List, Set, Tuple
from datetime import datetime, timedelta
from .base_scraper import BaseScraper, Event
import re


class TheBurrenScraper(BaseScraper):
    """Scraper for The Burren music schedule."""

    def __init__(self, user_agent: str, timeout: int = 10):
        super().__init__(
            venue_name="The Burren",
            url="https://www.burren.com/music.html",
            user_agent=user_agent,
            timeout=timeout
        )

    def scrape_events(self, days_ahead: int = 7) -> List[Event]:
        """Scrape events from The Burren schedule."""
        self.log_scraping_start(days_ahead)
        events = []
        soup = self.fetch_page()

        if not soup:
            self.log_scraping_result(0, "Failed to fetch page")
            return events

        # Track unique events to avoid duplicates
        seen_events: Set[Tuple[str, str, str]] = set()  # (date_str, time, title)

        # Look for date headers like "MONDAY FEBRUARY 2, 2026"
        date_pattern = re.compile(
            r'(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)\s+'
            r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+'
            r'(\d{1,2}),?\s*(\d{4})',
            re.IGNORECASE
        )

        current_date = None
        current_room = None

        # Process the page content
        page_text = soup.get_text()
        lines = page_text.split('\n')
        self.logger.debug(f"[{self.venue_name}] Processing {len(lines)} lines of text")

        dates_found = 0
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if this line contains a date
            date_match = date_pattern.search(line)

            if date_match:
                # Parse the date
                month_str = date_match.group(2)
                day_str = date_match.group(3)
                year_str = date_match.group(4)

                try:
                    current_date = datetime.strptime(
                        f"{month_str} {day_str} {year_str}",
                        "%B %d %Y"
                    )
                    dates_found += 1
                    current_room = None  # Reset room on new date
                    self.logger.debug(f"[{self.venue_name}] Found date: {current_date.strftime('%Y-%m-%d')}")
                except ValueError:
                    pass

            # Look for room designation
            elif re.search(r'(FRONT ROOM|BACK ROOM)', line, re.IGNORECASE):
                room_match = re.search(r'(FRONT ROOM|BACK ROOM)', line, re.IGNORECASE)
                current_room = room_match.group(1)
                self.logger.debug(f"[{self.venue_name}]   Room: {current_room}")

            # Look for time pattern (e.g., "7pm:", "8:30pm")
            elif current_date:
                time_match = re.search(r'^(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)):\s*$', line)

                if time_match:
                    time_str = time_match.group(1)

                    # Look ahead for the band/event name on subsequent lines
                    event_title_parts = []
                    j = i + 1
                    while j < len(lines) and j < i + 5:  # Look ahead up to 5 lines
                        next_line = lines[j].strip()

                        # Stop if we hit another time, date, or room
                        if (date_pattern.search(next_line) or
                            re.search(r'^\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM):', next_line, re.IGNORECASE) or
                            re.search(r'(FRONT ROOM|BACK ROOM)', next_line, re.IGNORECASE)):
                            break

                        # Skip empty lines
                        if not next_line:
                            j += 1
                            continue

                        # Add non-empty lines that look like event names
                        # Skip date headers and navigation text
                        if (len(next_line) > 1 and
                            next_line not in ['THE BURREN', 'Music'] and
                            not date_pattern.search(next_line)):  # Don't include date headers as event titles
                            event_title_parts.append(next_line)
                            j += 1
                            # Usually the band name is just one or two lines
                            if len(event_title_parts) >= 2:
                                break
                        else:
                            j += 1

                    if event_title_parts:
                        event_title = ' '.join(event_title_parts)

                        # Add room if known
                        if current_room:
                            event_title = f"{event_title} ({current_room})"

                        # Check for duplicates
                        date_key = current_date.strftime('%Y-%m-%d')
                        event_key = (date_key, time_str, event_title)

                        if event_key not in seen_events:
                            seen_events.add(event_key)

                            events.append(Event(
                                venue=self.venue_name,
                                date=current_date,
                                title=event_title,
                                time=time_str
                            ))
                            self.logger.debug(f"[{self.venue_name}]   Event: {time_str} - {event_title}")

            i += 1

        # Alternative approach: look for specific CSS classes
        band_elements = soup.find_all(class_=re.compile(r'BAND|HEADER', re.IGNORECASE))
        self.logger.debug(f"[{self.venue_name}] Alternative approach: Found {len(band_elements)} BAND/HEADER elements")

        for elem in band_elements:
            # Try to find associated date and time
            parent = elem.parent
            if parent:
                parent_text = parent.get_text()
                date_match = date_pattern.search(parent_text)
                time_match = re.search(r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))\b', parent_text)

                if date_match:
                    try:
                        event_date = datetime.strptime(
                            f"{date_match.group(2)} {date_match.group(3)} {date_match.group(4)}",
                            "%B %d %Y"
                        )
                        event_title = elem.get_text(strip=True)
                        time_str = time_match.group(1) if time_match else None

                        # Skip if title is just a date header
                        if date_pattern.search(event_title):
                            continue

                        # Check for duplicates
                        date_key = event_date.strftime('%Y-%m-%d')
                        event_key = (date_key, time_str or '', event_title)

                        if event_key not in seen_events:
                            seen_events.add(event_key)

                            events.append(Event(
                                venue=self.venue_name,
                                date=event_date,
                                title=event_title,
                                time=time_str
                            ))
                    except ValueError:
                        continue

        # Filter to only events within the days_ahead range
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today + timedelta(days=days_ahead)
        filtered_events = self.filter_events_by_date(events, today, end_date)

        details = f"Found {dates_found} dates, {len(events)} unique events, {len(band_elements)} BAND/HEADER elements"
        self.log_scraping_result(len(filtered_events), details)
        return filtered_events
