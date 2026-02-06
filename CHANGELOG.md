# Changelog

## Version 1.3 - Improved Reliability & UX (Current)

### New Features

#### Automatic Retry Logic
- **Smart retries**: Up to 5 retry attempts for failed HTTP requests
- **Exponential backoff**: Wait time increases between retries (1s, 2s, 4s, 8s, 10s max)
- **Connection resilience**: Handles temporary network issues automatically
- **Intelligent error handling**: Skips retries for client errors (4xx status codes)
- **Detailed logging**: Shows attempt numbers for debugging

#### Consolidated Venue Display
- **Grouped events**: Multiple events at same venue on same date are grouped together
- **Cleaner layout**: Venue name shown once with bullet points for multiple events
- **Applies everywhere**: Console output, HTML emails, and plain text emails
- **Better readability**: Easier to scan and see which venues have multiple shows

### Impact
- Significantly reduced "0 events" errors from temporary connection issues
- Improved user experience with cleaner, more organized event listings

---

## Version 1.2 - All Venues Working

### New Features

#### Beehive Boston Now Working
- **Switched to Tockify calendar**: Changed from Wix-based main site to Tockify embed
- **JSON extraction**: Extracts event data from embedded `window.tkf` JavaScript object
- **Rich event data**: Includes timestamps, titles, descriptions, and URLs
- **No headless browser needed**: Works with standard HTTP scraping

#### Scraper Improvements
- **Lizard Lounge**: Fixed duplicate events and empty "Event" entries
- **The Burren**: Fixed empty event titles, now shows actual band names and room designations
- **Plough and Stars**: Improved parsing to handle compact calendar format
- **The Mad Monkfish**: Added JSON-LD parsing and text fallback

### Bug Fixes
- Eliminated duplicate events across all scrapers
- Removed placeholder/generic event titles
- Fixed date headers appearing as events in The Burren
- Added deduplication logic to prevent the same event appearing multiple times

### Venue Status
- ✅ All 6 venues now working successfully
- 🎉 46+ events scraped across all venues

---

## Version 1.1 - Enhanced Diagnostics

### New Features

#### Output Modes
- **File output mode**: Write results to a text file instead of (or in addition to) email
- **Flexible configuration**: Choose "file", "email", or "both" in config.yaml
- **Summary table**: Per-venue status showing event counts and errors
- **Organized output**: Events grouped by date with full details

#### Diagnostic Logging
- **Comprehensive logging**: All scraping activity logged to `scraper_diagnostics.log`
- **HTTP diagnostics**: Request/response details, status codes, headers
- **Page structure analysis**: Automatic detection of calendar elements and page structure
- **Error tracking**: Detailed error messages with stack traces
- **Per-venue logging**: Easy to identify which venue has issues

#### Error Handling Improvements
- **Per-venue status tracking**: Continue scraping even if one venue fails
- **Detailed error messages**: Know exactly what went wrong and where
- **Graceful degradation**: App continues working even if some venues are down

### Configuration Changes

**New `output` section in config.yaml:**
```yaml
output:
  mode: "file"  # or "email" or "both"
  output_file: "events_output.txt"
```

### File Changes

**Modified Files:**
- `src/main.py` - Added output mode handling and file writing
- `src/scheduler.py` - Updated to use new return signature
- `src/scrapers/base_scraper.py` - Added comprehensive logging
- `config.yaml` - Added output configuration section
- `config.yaml.example` - Updated with output section

**Documentation Updates:**
- `README.md` - Updated with new features
- `QUICKSTART.md` - Updated workflow for file-first testing
- `CHANGELOG.md` - This file

### Benefits

1. **Easier Testing**: Use file mode to test without configuring email
2. **Better Debugging**: Detailed logs help diagnose scraping issues
3. **Venue Monitoring**: See at a glance which venues are working
4. **Flexible Workflow**: Test with files, then enable email when ready

### Migration Guide

If you have an existing `config.yaml`:

1. Add the new `output` section at the top:
   ```yaml
   output:
     mode: "file"
     output_file: "events_output.txt"
   ```

2. Start with file mode for testing
3. Change to "email" or "both" when ready

---

## Version 1.0 - Initial Release

### Features

- Web scraping for 6 Boston music venues
- HTML email notifications
- Daily scheduling
- Configurable SMTP settings
- Clean event formatting
- Basic error handling

### Supported Venues

1. Plough and Stars
2. The Burren
3. Beehive Boston
4. The Mad Monkfish
5. Wally's Cafe
6. Lizard Lounge
