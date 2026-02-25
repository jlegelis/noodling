# AGENTS.md

## Cursor Cloud specific instructions

**Product**: Music Finder — a Python CLI application that scrapes live music events from 6 Boston-area venues and outputs results to a file or sends email notifications.

**Tech stack**: Python 3.8+, requests, BeautifulSoup4, lxml, PyYAML, schedule. No database, Docker, or web server needed.

### Running the application

- Config file required: `cp config.yaml.example config.yaml` (only needed once; file output mode works out of the box).
- Run from `src/` directory: `python3 main.py` (one-time scrape) or `python3 scheduler.py` (long-running daily scheduler — avoid in cloud agents).
- Test individual scrapers: `cd src && python3 test_scrapers.py`.
- The app uses `python3`, not `python` (no `python` alias on the VM).

### Caveats

- Scrapers make live HTTP requests to external venue websites. Results depend on network access and current venue site structure.
- Email mode requires SMTP credentials in `config.yaml`. For testing, use `mode: "file"` (the default in `config.yaml.example`).
- No formal test framework (pytest, unittest) or linter is configured in the project. The test script `src/test_scrapers.py` is a manual integration test that hits live sites.
- Output files (`events_output.txt`, `scraper_diagnostics.log`) are written relative to the repo root, not `src/`.
