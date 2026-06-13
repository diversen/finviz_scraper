from finviz_data import finviz_data
from finviz_scraper.logging import get_log
import pandas as pd
import time
import os
from finviz_scraper.sqlite_cache import SqliteCache
from bs4 import BeautifulSoup
import random
from settings import settings


sql_cache = SqliteCache("cache")
log = get_log()
FAILED_TICKER_KEY_PREFIX = "failed_ticker:"


def _failed_ticker_key(ticker):
    return "{}{}".format(FAILED_TICKER_KEY_PREFIX, ticker)


def get_tickers_df(tickers, max_tickers=False):
    """Get tickers as a dataframe with exponential backoff on failure."""

    n = 0
    successful_tickers = 0
    failed_tickers = 0
    skipped_tickers = 0
    back_off_time = settings["back_off_time"]  # Initial backoff time in seconds

    df = pd.DataFrame()
    total_tickers = len(tickers)
    if max_tickers:
        total_tickers = min(total_tickers, max_tickers)

    def log_progress(processed_tickers):
        log.info("Processed %s out of %s tickers", processed_tickers, total_tickers)

    for ticker in tickers:
        try:
            failed_ticker_key = _failed_ticker_key(ticker)
            if sql_cache.get(failed_ticker_key):
                log.debug("Skipping previously failed ticker {}".format(ticker))
                skipped_tickers += 1
                n += 1
                log_progress(n)
                if max_tickers and n >= max_tickers:
                    break
                continue

            html = sql_cache.get(ticker)
            if not html:
                log.debug("Fetching {}".format(ticker))
                soup = finviz_data.get_soup(ticker)
                sql_cache.set(str(ticker), str(soup))

                # get random sleep interval to avoid getting blocked
                random_sleep = random.randint(
                    settings["sleep_min"], settings["sleep_max"]
                )

                time.sleep(random_sleep)  # Throttling requests
            else:
                log.debug("Fetching {} from cache".format(ticker))
                soup = BeautifulSoup(html, "html.parser")

            data = finviz_data.get_fundamentals_float(soup)
            company = finviz_data.get_company_info(soup)
            data = {**company, **data}
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            successful_tickers += 1
            sql_cache.delete(failed_ticker_key)

            # Reset backoff time after successful fetch
            back_off_time = settings["back_off_time"]

        except Exception as e:
            print(html)
            failed_tickers += 1
            sql_cache.set(_failed_ticker_key(ticker), str(e))

            log.warning(
                "Failed fetching {}, backing off for {} seconds".format(
                    ticker, back_off_time
                )
            )
            log.exception(e)
            time.sleep(back_off_time)

            # Exponential backoff
            back_off_time = back_off_time * 2

            max_back_off_time = settings["max_back_off_time"]
            if back_off_time > max_back_off_time:
                back_off_time = max_back_off_time

        n += 1
        log_progress(n)
        if max_tickers and n >= max_tickers:
            break

    log.info(
        "Fetched tickers: %s successful, %s failed, %s skipped",
        successful_tickers,
        failed_tickers,
        skipped_tickers,
    )
    df.attrs["fetch_summary"] = {
        "successful": successful_tickers,
        "failed": failed_tickers,
        "skipped": skipped_tickers,
    }

    return df


def export_to_csv(df, filename):
    """
    Export to CSV from dataframe from a given filename
    Dirs in the filename that does not exists will be created
    """
    dirname = os.path.dirname(filename)
    os.makedirs(dirname, exist_ok=True)

    df.to_csv(filename, index=False)
