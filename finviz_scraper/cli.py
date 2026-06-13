import argparse
from datetime import datetime
import time
from typing import Callable

import pandas as pd

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


def export_index(name: str, output_dir: str) -> pd.DataFrame:
    fetch_tickers = TICKER_SOURCES[name]
    tickers = fetch_tickers()
    log.info("Beginning %s index with %s tickers", name, len(tickers))
    df = get_tickers_df(tickers)
    export_to_csv(df, f"{output_dir}/{name}.csv")
    return df


def export_combined(index_dfs: list[pd.DataFrame], output_dir: str) -> None:
    combined_df = pd.concat(index_dfs, ignore_index=True)
    if "Ticker" in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset="Ticker", keep="first")

    export_to_csv(combined_df, f"{output_dir}/combined.csv")
    log.info("Exported combined CSV with %s rows", len(combined_df))


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

    today = datetime.today().strftime("%Y-%m-%d")
    output_dir = f"./csv/{today}"
    index_dfs = []
    for index in args.indexes:
        index_dfs.append(export_index(index, output_dir))
    if len(index_dfs) > 1:
        export_combined(index_dfs, output_dir)

    elapsed_seconds = time.monotonic() - start_time
    log.info("Completed in %s", format_elapsed(elapsed_seconds))
