# Simple scraper for finviz stock data

Some simple script for fetching stock data from finviz.com and export the data to CSV files.

It uses this small lib [finviz-data](https://github.com/diversen/finviz-data) for fetching and extracting the data.

## Installl

    git clone https://github.com/diversen/finviz_scraper

    cd finviz_scraper

    virtualenv venv

    source venv/bin/activate

    pip install -r requirements.txt

    cp settings.py-dist settings.py

## Example

Save sp500 as a CSV file in the folder `./csv`

    python csv_from_sp500.py

Or save nasdaq symbols as a CSV file in `./csv`:

    python csv_from_nasdaq.py
