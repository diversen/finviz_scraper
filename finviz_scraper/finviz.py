from finviz_data import finviz_data
from finviz_scraper.logging import get_log
import pandas as pd
import time
import traceback
import os
from sqlite_cache.sqlite_cache import SqliteCache
from bs4 import BeautifulSoup


sql_cache = SqliteCache("cache")

log = get_log()


def get_tickers_df(tickers, max_n=False, show_traceback=False):
    """Get tickers as a dataframe"""

    n = 0
    df = pd.DataFrame()
    for ticker in tickers:
        try:
            html = sql_cache.get(ticker)
            if not html:
                log.debug("Fetching {}".format(ticker))
                soup = finviz_data.get_soup(ticker)
                sql_cache.set(str(ticker), str(soup))
                data = finviz_data.get_fundamentals_float(soup)

            else:
                log.debug("Fetching {} from cache".format(ticker))
                soup = BeautifulSoup(html, "html.parser")
                data = finviz_data.get_fundamentals_float(soup)

            time.sleep(0.2)
            if not data:
                log.debug("No data in {}".format(ticker))
                log.debug("---")
                continue

            df = df.append(data, ignore_index=True)

        except Exception as e:
            if show_traceback:
                log.warning("Failed fetching {}".format(ticker))
                tb = traceback.format_exc()
                log.warning(tb)
                log.debug("---")
            else:
                log.debug(e)
                log.debug("---")

        n += 1
        if max_n and n > max_n:
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
