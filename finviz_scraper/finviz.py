from finviz_data import finviz_data
from finviz_scraper.logging import get_log
import pandas as pd
import time
import os
from sqlite_cache.sqlite_cache import SqliteCache
from bs4 import BeautifulSoup


sql_cache = SqliteCache("cache")
log = get_log()


def get_tickers_df(tickers, max_tickers=False):
    """Get tickers as a dataframe with exponential backoff on failure."""

    n = 0
    backoff_time = 0.2  # Initial backoff time in seconds
    df = pd.DataFrame()

    for ticker in tickers:
        try:
            html = sql_cache.get(ticker)
            if not html:
                log.debug("Fetching {}".format(ticker))
                soup = finviz_data.get_soup(ticker)
                sql_cache.set(str(ticker), str(soup))
                time.sleep(0.2)  # Throttling requests
            else:
                log.debug("Fetching {} from cache".format(ticker))
                soup = BeautifulSoup(html, "html.parser")

            data = finviz_data.get_fundamentals_float(soup)
            company = finviz_data.get_company_info(soup)
            data = {**company, **data}
            df = df.append(data, ignore_index=True)

            # Reset backoff time after successful fetch
            backoff_time = 0.2

        except Exception:
            log.warning(
                "Failed fetching {}, backing off for {} seconds".format(
                    ticker, backoff_time
                )
            )
            time.sleep(backoff_time)

        n += 1
        if max_tickers and n >= max_tickers:
            break

    return df


def export_to_csv(df, filename):
    """
    Export to CSV from dataframe from a given filename
    Dirs in the filename that does not exists will be created
    """
    dirname = os.path.dirname(filename)
    os.makedirs(dirname, exist_ok=True)

    df.to_csv(filename, index=False)
