from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import logging
import os
import time


class Event:
    """Represents a music event at a venue."""

    def __init__(self, venue: str, date: datetime, title: str, time: str = None,
                 genre: str = None, url: str = None):
        self.venue = venue
        self.date = date
        self.title = title
        self.time = time
        self.genre = genre
        self.url = url

    def __repr__(self):
        return f"Event({self.venue}, {self.date.strftime('%Y-%m-%d')}, {self.title})"

    def to_dict(self) -> Dict:
        """Convert event to dictionary."""
        return {
            'venue': self.venue,
            'date': self.date.strftime('%Y-%m-%d'),
            'title': self.title,
            'time': self.time,
            'genre': self.genre,
            'url': self.url
        }


class BaseScraper(ABC):
    """Base class for venue scrapers."""

    _logger_initialized = False

    def __init__(self, venue_name: str, url: str, user_agent: str, timeout: int = 10):
        self.venue_name = venue_name
        self.url = url
        self.user_agent = user_agent
        self.timeout = timeout
        self.headers = {'User-Agent': user_agent}
        self.logger = self._get_logger()

    @classmethod
    def _get_logger(cls):
        """Get or create logger for scrapers."""
        if not cls._logger_initialized:
            # Get the project root directory (parent of src)
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_file = os.path.join(script_dir, 'scraper_diagnostics.log')
            
            # Create logger
            logger = logging.getLogger('scraper')
            logger.setLevel(logging.DEBUG)
            
            # Remove existing handlers to avoid duplicates
            logger.handlers = []
            
            # File handler
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            # Console handler (for errors and warnings)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            cls._logger_initialized = True
        
        return logging.getLogger('scraper')

    def fetch_page(self, url: str = None, max_retries: int = 5) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page with detailed diagnostics and retry logic.

        Args:
            url: URL to fetch (defaults to self.url)
            max_retries: Maximum number of retry attempts (default: 5)

        Returns:
            BeautifulSoup object or None if all retries failed
        """
        target_url = url or self.url

        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                wait_time = min(2 ** (attempt - 1), 10)  # Exponential backoff, max 10 seconds
                self.logger.info(f"[{self.venue_name}] Retry attempt {attempt}/{max_retries} after {wait_time}s wait...")
                time.sleep(wait_time)
            else:
                self.logger.info(f"[{self.venue_name}] Fetching page: {target_url}")

            try:
                self.logger.debug(f"[{self.venue_name}] Request headers: {self.headers}")
                response = requests.get(target_url, headers=self.headers, timeout=self.timeout)

                self.logger.info(f"[{self.venue_name}] Response status: {response.status_code}")
                self.logger.debug(f"[{self.venue_name}] Response headers: {dict(response.headers)}")

                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'lxml')

                # Log page structure diagnostics (only on successful fetch)
                if attempt == 1:
                    self._log_page_structure(soup, target_url)

                self.logger.info(f"[{self.venue_name}] Successfully fetched and parsed page (attempt {attempt})")
                return soup

            except requests.exceptions.Timeout as e:
                self.logger.warning(f"[{self.venue_name}] Timeout on attempt {attempt}/{max_retries}: {e}")
                if attempt == max_retries:
                    self.logger.error(f"[{self.venue_name}] All {max_retries} attempts failed due to timeout")
                    return None

            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"[{self.venue_name}] Connection error on attempt {attempt}/{max_retries}: {e}")
                if attempt == max_retries:
                    self.logger.error(f"[{self.venue_name}] All {max_retries} attempts failed due to connection error")
                    return None

            except requests.exceptions.HTTPError as e:
                status_code = response.status_code if 'response' in locals() else 'unknown'
                self.logger.warning(f"[{self.venue_name}] HTTP error on attempt {attempt}/{max_retries}: Status {status_code}, {e}")
                # Don't retry on 4xx errors (client errors)
                if 'response' in locals() and 400 <= response.status_code < 500:
                    self.logger.error(f"[{self.venue_name}] Client error {status_code}, not retrying")
                    return None
                if attempt == max_retries:
                    self.logger.error(f"[{self.venue_name}] All {max_retries} attempts failed due to HTTP error")
                    return None

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"[{self.venue_name}] Request exception on attempt {attempt}/{max_retries}: {type(e).__name__}: {e}")
                if attempt == max_retries:
                    self.logger.error(f"[{self.venue_name}] All {max_retries} attempts failed: {type(e).__name__}")
                    return None

            except Exception as e:
                self.logger.error(f"[{self.venue_name}] Unexpected error on attempt {attempt}/{max_retries}: {type(e).__name__}: {e}", exc_info=True)
                if attempt == max_retries:
                    self.logger.error(f"[{self.venue_name}] All {max_retries} attempts failed due to unexpected error")
                    return None

        return None

    def _log_page_structure(self, soup: BeautifulSoup, url: str):
        """Log diagnostic information about the page structure."""
        self.logger.debug(f"[{self.venue_name}] Page structure diagnostics:")
        self.logger.debug(f"  - Title: {soup.title.string if soup.title else 'No title'}")
        self.logger.debug(f"  - Page length: {len(soup.get_text())} characters")
        
        # Count common elements
        divs = soup.find_all('div')
        tables = soup.find_all('table')
        links = soup.find_all('a')
        self.logger.debug(f"  - Elements: {len(divs)} divs, {len(tables)} tables, {len(links)} links")
        
        # Look for common calendar/event indicators
        event_indicators = [
            ('data-date', soup.find_all(attrs={'data-date': True})),
            ('class containing "event"', soup.find_all(class_=lambda x: x and 'event' in str(x).lower())),
            ('class containing "calendar"', soup.find_all(class_=lambda x: x and 'calendar' in str(x).lower())),
            ('class containing "date"', soup.find_all(class_=lambda x: x and 'date' in str(x).lower())),
        ]
        
        for indicator_name, elements in event_indicators:
            if elements:
                self.logger.debug(f"  - Found {len(elements)} elements with {indicator_name}")
        
        # Log a sample of the HTML structure (first 500 chars)
        html_preview = str(soup)[:500]
        self.logger.debug(f"  - HTML preview (first 500 chars): {html_preview}...")

    @abstractmethod
    def scrape_events(self, days_ahead: int = 7) -> List[Event]:
        """
        Scrape events from the venue.

        Args:
            days_ahead: Number of days to look ahead for events

        Returns:
            List of Event objects
        """
        pass

    def filter_events_by_date(self, events: List[Event], start_date: datetime,
                             end_date: datetime) -> List[Event]:
        """Filter events by date range."""
        filtered = [e for e in events if start_date <= e.date <= end_date]
        self.logger.debug(f"[{self.venue_name}] Filtered {len(events)} events to {len(filtered)} within date range")
        return filtered
    
    def log_scraping_start(self, days_ahead: int):
        """Log the start of a scraping operation."""
        self.logger.info(f"[{self.venue_name}] Starting scrape for next {days_ahead} days")
    
    def log_scraping_result(self, events_found: int, parsing_details: str = ""):
        """Log the result of a scraping operation."""
        self.logger.info(f"[{self.venue_name}] Scraping complete: Found {events_found} events")
        if parsing_details:
            self.logger.debug(f"[{self.venue_name}] Parsing details: {parsing_details}")
