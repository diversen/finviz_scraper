# Simple scraper for finviz stock data

A simple scrapper for finviz data which will cache data in a sqlite database. 

Export data to CSV files. 

It may stop working when [https://finviz.com/](finviz) modifies HTML layout.

## Installl

    git clone https://github.com/diversen/finviz-scrapper

    cd finviz-scrapper

    virtualenv venv

    source venv/bin/activate

    pip install -r requirements.txt

## Example

Se test.py which fetches a single symbol (stock)

    python test.py

Save sp500 as a CSV file in `./csv/`

    python csv_from_sp500.py

Or save nasdaq symbols as a CSV file in `./csv`:

    python csv_from_nasdaq.py



