from typing import List
from datetime import datetime, timedelta
from .base_scraper import BaseScraper, Event
import re
import json


class BeehiveBostonScraper(BaseScraper):
    """
    Scraper for Beehive Boston calendar.

    NOTE: Beehive's main website uses Wix/JavaScript rendering, but they also
    have a Tockify calendar at https://tockify.com/beehive/monthly which embeds
    event data in the HTML as JSON. We scrape from the Tockify calendar instead.
    """

    def __init__(self, user_agent: str, timeout: int = 10):
        super().__init__(
            venue_name="Beehive Boston",
            url="https://tockify.com/beehive/monthly",  # Using Tockify instead of main site
            user_agent=user_agent,
            timeout=timeout
        )

    def scrape_events(self, days_ahead: int = 7) -> List[Event]:
        """Scrape events from Beehive Boston Tockify calendar."""
        self.log_scraping_start(days_ahead)
        events = []
        soup = self.fetch_page()

        if not soup:
            self.log_scraping_result(0, "Failed to fetch page")
            return events

        # Approach 1: Extract from window.tkf bootdata JSON
        scripts = soup.find_all('script')

        for script in scripts:
            if script.string and 'window.tkf' in script.string:
                self.logger.debug(f"[{self.venue_name}] Found window.tkf script")

                # Extract the JSON data from the JavaScript
                # Look for pattern: window.tkf = {...}
                match = re.search(r'window\.tkf\s*=\s*({.+?});?\s*(?:window\.|</script>|$)',
                                script.string, re.DOTALL)

                if match:
                    try:
                        tkf_json = match.group(1)
                        tkf_data = json.loads(tkf_json)

                        # Events are in bootdata.events array
                        if 'bootdata' in tkf_data and 'events' in tkf_data['bootdata']:
                            event_list = tkf_data['bootdata']['events']
                            self.logger.debug(f"[{self.venue_name}] Found {len(event_list)} events in bootdata")

                            for event_data in event_list:
                                event = self._parse_tockify_event(event_data)
                                if event:
                                    events.append(event)

                    except json.JSONDecodeError as e:
                        self.logger.error(f"[{self.venue_name}] Error parsing window.tkf JSON: {e}")
                    except Exception as e:
                        self.logger.error(f"[{self.venue_name}] Error processing tkf data: {e}")

        # Approach 2: Try JSON-LD structured data (fallback)
        if not events:
            self.logger.debug(f"[{self.venue_name}] Trying JSON-LD approach")
            json_ld_scripts = soup.find_all('script', type='application/ld+json')

            for script in json_ld_scripts:
                try:
                    if script.string:
                        data = json.loads(script.string)

                        # Handle both single events and arrays
                        events_to_process = []
                        if isinstance(data, list):
                            events_to_process = data
                        elif isinstance(data, dict):
                            events_to_process = [data]

                        for item in events_to_process:
                            if isinstance(item, dict) and item.get('@type') == 'Event':
                                event = self._parse_json_ld_event(item)
                                if event:
                                    events.append(event)

                except json.JSONDecodeError as e:
                    self.logger.debug(f"[{self.venue_name}] Error parsing JSON-LD: {e}")

        # Filter to only events within the days_ahead range
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today + timedelta(days=days_ahead)
        filtered_events = self.filter_events_by_date(events, today, end_date)

        self.log_scraping_result(
            len(filtered_events),
            f"Extracted {len(events)} events from Tockify calendar, {len(filtered_events)} within date range"
        )
        return filtered_events

    def _parse_tockify_event(self, data: dict) -> Event:
        """Parse a Tockify event object from the bootdata."""
        try:
            # Extract title
            title = data.get('summary', {}).get('title', 'Event')

            # Extract start date/time
            start_info = data.get('when', {}).get('start', {})

            # Tockify uses millisecond timestamps
            timestamp_ms = start_info.get('millis')
            if timestamp_ms:
                event_date = datetime.fromtimestamp(timestamp_ms / 1000.0)
            else:
                # Fallback: try to parse date string
                date_str = start_info.get('date')
                if date_str:
                    event_date = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    return None

            # Extract time if available
            time_str = None
            if 'time' in start_info:
                time_str = start_info['time']
            elif timestamp_ms:
                # Format time from timestamp
                time_str = event_date.strftime('%I:%M %p').lstrip('0')

            # Extract URL if available
            event_url = None
            if 'content' in data and 'exturl' in data['content']:
                event_url = data['content']['exturl']

            # Extract genre/description if available
            genre = None
            if 'content' in data and 'description' in data['content']:
                description = data['content']['description']
                # Extract genre keywords if present
                if description:
                    # Look for common genre words
                    genre_keywords = ['jazz', 'blues', 'folk', 'rock', 'classical', 'soul', 'funk']
                    desc_lower = description.lower()
                    for keyword in genre_keywords:
                        if keyword in desc_lower:
                            genre = keyword.capitalize()
                            break

            self.logger.debug(f"[{self.venue_name}] Parsed event: {title} on {event_date.strftime('%Y-%m-%d')}")

            return Event(
                venue=self.venue_name,
                date=event_date,
                title=title,
                time=time_str,
                genre=genre,
                url=event_url
            )

        except Exception as e:
            self.logger.debug(f"[{self.venue_name}] Error parsing Tockify event: {e}")
            return None

    def _parse_json_ld_event(self, data: dict) -> Event:
        """Parse a JSON-LD event object (fallback method)."""
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
                time_str = event_date.strftime('%I:%M %p').lstrip('0')

            # Get URL if available
            event_url = data.get('url')

            return Event(
                venue=self.venue_name,
                date=event_date,
                title=title,
                time=time_str,
                url=event_url
            )
        except Exception as e:
            self.logger.debug(f"[{self.venue_name}] Error parsing JSON-LD event: {e}")
            return None
