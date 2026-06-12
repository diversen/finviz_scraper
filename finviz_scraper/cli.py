import argparse
from datetime import datetime
import time
from typing import Callable

from finviz_scraper.finviz import export_to_csv, get_tickers_df
from finviz_scraper.get_tickers import (
    tickers_all,
    tickers_c25,
    tickers_nasdaq,
    tickers_nasdaq100,
    tickers_other,
    tickers_sp500,
)
from finviz_scraper.logging import get_log


log = get_log()


TICKER_SOURCES: dict[str, Callable[[], list[str]]] = {
    "all": tickers_all,
    "c25": tickers_c25,
    "nasdaq": tickers_nasdaq,
    "nasdaq100": tickers_nasdaq100,
    "other": tickers_other,
    "sp500": tickers_sp500,
}


def export_index(name: str) -> None:
    fetch_tickers = TICKER_SOURCES[name]
    today = datetime.today().strftime("%Y-%m-%d")
    df = get_tickers_df(fetch_tickers())
    export_to_csv(df, f"./csv/{today}/{name}.csv")


def format_elapsed(seconds: float) -> str:
    total_seconds = round(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def main() -> None:
    start_time = time.monotonic()
    parser = argparse.ArgumentParser(
        description="Export Finviz fundamentals data for a ticker index."
    )
    parser.add_argument("indexes", choices=sorted(TICKER_SOURCES), nargs="+")
    args = parser.parse_args()
    for index in args.indexes:
        export_index(index)
    elapsed_seconds = time.monotonic() - start_time
    log.info("Completed in %s", format_elapsed(elapsed_seconds))
