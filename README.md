# Simple scraper for finviz fundamentals data

Some simple script for fetching stock data from finviz.com and export the data to CSV files.

It uses this small lib [finviz-data](https://github.com/diversen/finviz-data) for fetching and extracting the data.

## Install

    git clone https://github.com/diversen/finviz_scraper

    cd finviz_scraper

    uv sync

    cp settings.py-dist settings.py

## Example

Save sp500 as a CSV file in the folder `./csv`

    uv run python finviz_csv.py sp500

Or save nasdaq symbols as a CSV file in `./csv`:

    uv run python finviz_csv.py nasdaq

Save two indexes in one run:

    uv run python finviz_csv.py sp500 nasdaq100

This creates `sp500.csv`, `nasdaq100.csv`, and a de-duplicated `combined.csv`
in `./csv/YYYY-MM-DD/`.

Available indexes are `all`, `c25`, `nasdaq`, `nasdaq100`, `other`, and `sp500`.

## SMTP report

Add SMTP settings in `settings.py` to send a plain-text report when the run
finishes. Leave `host`, `from`, or `to` empty to skip sending mail.

```python
"smtp": {
    "host": "smtp.example.com",
    "port": 587,
    "username": "user@example.com",
    "password": "password",
    "from": "user@example.com",
    "to": ["recipient@example.com"],
    "subject": "Finviz scraper report",
    "use_tls": True,
    "use_ssl": False,
    "timeout": 30,
},
```
