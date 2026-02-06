# Automatic Retry Logic

## Overview

To handle temporary network issues and connection failures, the Music Finder app includes automatic retry logic in the base scraper. This ensures that transient problems don't result in missing events.

## How It Works

### Retry Parameters

- **Maximum Retries**: 5 attempts per venue
- **Backoff Strategy**: Exponential with cap
  - Attempt 1: Immediate (no wait)
  - Attempt 2: 1 second wait
  - Attempt 3: 2 seconds wait
  - Attempt 4: 4 seconds wait
  - Attempt 5: 8 seconds wait (capped at 10s max)

### Retry Flow

```
Attempt 1: Try to fetch page
  ↓ Success → Return data ✓
  ↓ Failure → Log warning

Attempt 2: Wait 1s, retry
  ↓ Success → Return data ✓
  ↓ Failure → Log warning

Attempt 3: Wait 2s, retry
  ↓ Success → Return data ✓
  ↓ Failure → Log warning

Attempt 4: Wait 4s, retry
  ↓ Success → Return data ✓
  ↓ Failure → Log warning

Attempt 5: Wait 8s, retry
  ↓ Success → Return data ✓
  ↓ Failure → Log error, return None ✗
```

### What Gets Retried

The retry logic handles these error types:

1. **Timeout Errors** (`requests.exceptions.Timeout`)
   - Server took too long to respond
   - Will retry all 5 times

2. **Connection Errors** (`requests.exceptions.ConnectionError`)
   - Network unavailable
   - DNS resolution failed
   - Host unreachable
   - Will retry all 5 times

3. **HTTP 5xx Errors** (Server Errors)
   - 500 Internal Server Error
   - 502 Bad Gateway
   - 503 Service Unavailable
   - Will retry all 5 times

4. **Other Request Exceptions**
   - Generic request failures
   - Will retry all 5 times

### What Doesn't Get Retried

These errors fail immediately without retries:

1. **HTTP 4xx Errors** (Client Errors)
   - 400 Bad Request
   - 401 Unauthorized
   - 403 Forbidden
   - 404 Not Found
   - These indicate a problem with our request, not a temporary issue

## Implementation

### Location
`src/scrapers/base_scraper.py` - `fetch_page()` method

### Code Example
```python
def fetch_page(self, url: str = None, max_retries: int = 5) -> Optional[BeautifulSoup]:
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            wait_time = min(2 ** (attempt - 1), 10)
            time.sleep(wait_time)

        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except ConnectionError:
            if attempt == max_retries:
                return None
            # Continue to next attempt
```

### Logging

Each attempt is logged with context:

**Successful first attempt:**
```
[Venue Name] Fetching page: https://...
[Venue Name] Response status: 200
[Venue Name] Successfully fetched and parsed page (attempt 1)
```

**Retry scenario:**
```
[Venue Name] Fetching page: https://...
[Venue Name] Connection error on attempt 1/5: ...
[Venue Name] Retry attempt 2/5 after 1s wait...
[Venue Name] Response status: 200
[Venue Name] Successfully fetched and parsed page (attempt 2)
```

**All retries failed:**
```
[Venue Name] Fetching page: https://...
[Venue Name] Connection error on attempt 1/5: ...
[Venue Name] Retry attempt 2/5 after 1s wait...
[Venue Name] Connection error on attempt 2/5: ...
...
[Venue Name] Retry attempt 5/5 after 8s wait...
[Venue Name] Connection error on attempt 5/5: ...
[Venue Name] All 5 attempts failed due to connection error
```

## Benefits

### 1. Resilience to Transient Issues
- Network hiccups
- Temporary DNS failures
- Brief server outages
- Load balancer issues

### 2. Automatic Recovery
- No manual intervention needed
- Scraper continues with other venues
- Maximizes successful data collection

### 3. Better User Experience
- Fewer "0 events found" errors
- More reliable daily emails
- Consistent data availability

### 4. Debugging Support
- Detailed logs show which attempts failed
- Easy to identify persistent vs transient issues
- Clear indication when retries help

## Performance Impact

### Best Case (All succeed on first try)
- No impact: runs as before
- Total time: ~5-10 seconds for 6 venues

### Worst Case (All venues need all 5 retries)
- Maximum additional time: ~15 seconds per venue
- Total time: ~90-120 seconds for 6 venues
- This scenario is extremely rare

### Typical Case
- 1-2 venues might need 1 retry
- Additional time: 1-2 seconds
- Total time: ~6-12 seconds for 6 venues

## Configuration

### Current Settings
```python
max_retries = 5  # In base_scraper.py fetch_page() method
timeout = 10      # From config.yaml
```

### To Adjust Retries
Edit `src/scrapers/base_scraper.py`:
```python
def fetch_page(self, url: str = None, max_retries: int = 5):
    # Change max_retries default value here
```

### To Adjust Timeout
Edit `config.yaml`:
```yaml
scraping:
  timeout: 10  # seconds
```

## Testing

### Manual Test
Run the scraper and check logs:
```bash
cd src
python3 main.py

# Check if retries occurred
grep -i "retry" ../scraper_diagnostics.log
```

### Simulate Connection Issues
To test retry logic, temporarily break a URL or disconnect network during scraping.

## Real-World Example

### Before Retry Logic
```
Scraping The Burren... ✗ Found 0 events
[The Burren] Connection error: No route to host
```
**Result:** Missing 21 events due to one connection blip

### After Retry Logic
```
Scraping The Burren... ✓ Found 21 events
[The Burren] Connection error on attempt 1/5: No route to host
[The Burren] Retry attempt 2/5 after 1s wait...
[The Burren] Successfully fetched and parsed page (attempt 2)
```
**Result:** All 21 events retrieved after brief retry

## Monitoring

Watch for these patterns in logs:

### Good Signs ✓
- Most venues succeed on attempt 1
- Occasional retries that succeed on attempt 2-3
- Clear recovery from transient issues

### Warning Signs ⚠️
- Frequent retries needed (every run)
- Retries often reaching attempt 4-5
- May indicate network or ISP issues

### Problem Signs ✗
- Consistent failures after all 5 retries
- Same venue always failing
- Indicates persistent problem (site down, blocked, URL changed)

## Future Enhancements

Potential improvements:
- Configurable retry count via config.yaml
- Per-venue retry configuration
- Adaptive backoff based on error type
- Circuit breaker pattern for persistently failing venues
- Exponential backoff with jitter for better load distribution

## Summary

The retry logic makes the scraper significantly more reliable by automatically handling temporary connection issues. With 5 retries and exponential backoff, the system can recover from brief network problems without manual intervention, ensuring more consistent data collection for daily music event notifications.
