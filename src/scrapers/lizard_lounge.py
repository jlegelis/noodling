from typing import List, Set, Tuple
from datetime import datetime, timedelta
from .base_scraper import BaseScraper, Event
import re


class LizardLoungeScraper(BaseScraper):
    """Scraper for Lizard Lounge calendar."""

    def __init__(self, user_agent: str, timeout: int = 10):
        super().__init__(
            venue_name="Lizard Lounge",
            url="https://lizardloungeclub.com/calendar/",
            user_agent=user_agent,
            timeout=timeout
        )

    def scrape_events(self, days_ahead: int = 7) -> List[Event]:
        """Scrape events from Lizard Lounge calendar."""
        self.log_scraping_start(days_ahead)
        events = []
        soup = self.fetch_page()

        if not soup:
            self.log_scraping_result(0, "Failed to fetch page")
            return events

        # Track unique events to avoid duplicates
        seen_events: Set[Tuple[str, str]] = set()  # (date_str, title)

        # Look for calendar/event structures
        # Try multiple common calendar plugin formats

        # Approach 1: Events with data attributes
        event_items = soup.find_all(attrs={'data-date': True})
        self.logger.debug(f"[{self.venue_name}] Approach 1: Found {len(event_items)} items with data-date attribute")

        for item in event_items:
            date_str = item.get('data-date')
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%d')
            except (ValueError, TypeError):
                try:
                    event_date = datetime.strptime(date_str, '%m/%d/%Y')
                except (ValueError, TypeError):
                    continue

            # Find title - be more specific to avoid getting all text
            event_title = None

            # First try to find a link with the event name
            link = item.find('a', href=re.compile(r'/event/'))
            if link:
                event_title = link.get_text(strip=True)

            # If no link, try heading
            if not event_title:
                heading = item.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                if heading:
                    event_title = heading.get_text(strip=True)

            # If still no title, try elements with title/name class
            if not event_title:
                title_elem = item.find(class_=re.compile(r'title|name', re.IGNORECASE))
                if title_elem:
                    event_title = title_elem.get_text(strip=True)

            # Skip if no meaningful title
            if not event_title or event_title in ['', 'View', 'Details', 'Event']:
                self.logger.debug(f"[{self.venue_name}] Skipping item with no meaningful title: '{event_title}'")
                continue

            # Check for duplicates
            date_key = event_date.strftime('%Y-%m-%d')
            if (date_key, event_title) in seen_events:
                self.logger.debug(f"[{self.venue_name}] Skipping duplicate: {event_title} on {date_key}")
                continue

            seen_events.add((date_key, event_title))

            # Find time
            time_elem = item.find(class_=re.compile(r'time|hour', re.IGNORECASE))
            time_str = time_elem.get_text(strip=True) if time_elem else None

            if not time_str:
                time_match = re.search(r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))\b', item.get_text())
                time_str = time_match.group(1) if time_match else None

            # Find URL
            event_url = link.get('href', '') if link else None

            events.append(Event(
                venue=self.venue_name,
                date=event_date,
                title=event_title,
                time=time_str,
                url=event_url
            ))
            self.logger.debug(f"[{self.venue_name}] Added event: {event_title} on {date_key}")

        # Approach 2: Look for article/post format (only if approach 1 found nothing)
        if not events:
            articles = soup.find_all(['article', 'div'], class_=re.compile(r'event|post|show', re.IGNORECASE))
            self.logger.debug(f"[{self.venue_name}] Approach 2: Found {len(articles)} article/event containers")

            for article in articles:
                # Find date
                date_elem = article.find(class_=re.compile(r'date|time', re.IGNORECASE))
                if not date_elem:
                    date_elem = article.find(['time', 'span'])

                if not date_elem:
                    continue

                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)

                # Parse date
                event_date = None
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y', '%b %d, %Y']:
                    try:
                        event_date = datetime.strptime(date_text, fmt)
                        break
                    except ValueError:
                        continue

                if not event_date:
                    continue

                # Find title
                title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                event_title = title_elem.get_text(strip=True) if title_elem else None

                if not event_title or event_title in ['Event', 'View', 'Details']:
                    continue

                # Check for duplicates
                date_key = event_date.strftime('%Y-%m-%d')
                if (date_key, event_title) in seen_events:
                    continue

                seen_events.add((date_key, event_title))

                # Find time
                time_match = re.search(r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))\b', article.get_text())
                time_str = time_match.group(1) if time_match else None

                # Find URL
                link = article.find('a')
                event_url = link.get('href', '') if link else None

                events.append(Event(
                    venue=self.venue_name,
                    date=event_date,
                    title=event_title,
                    time=time_str,
                    url=event_url
                ))

        # Filter to only events within the days_ahead range
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today + timedelta(days=days_ahead)
        filtered_events = self.filter_events_by_date(events, today, end_date)

        self.log_scraping_result(
            len(filtered_events),
            f"Found {len(events)} unique events, {len(filtered_events)} within date range"
        )
        return filtered_events
