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

Available indexes are `all`, `c25`, `nasdaq`, `nasdaq100`, `other`, and `sp500`.
