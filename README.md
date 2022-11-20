# Simple scraper for finviz stock data

A simple scraper for finviz data which will cache data in a sqlite database.

Export data to CSV files. 

## Installl

    git clone https://github.com/diversen/finviz_scraper

    cd finviz_scraper

    virtualenv venv

    source venv/bin/activate

    pip install -r requirements.txt

## Example

Se test_get_fundamentals.py which fetches a single symbol in some different ways

    python test_get_fundamentals.py

Save sp500 as a CSV file in the folder `./csv`

    python csv_from_sp500.py

Or save nasdaq symbols as a CSV file in `./csv`:

    python csv_from_nasdaq.py

