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
from finviz_scraper.mail import send_report


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
    try:
        tickers = fetch_tickers()
    except Exception:
        log.exception("Failed to fetch %s ticker list", name)
        raise

    log.info("Beginning %s index with %s tickers", name, len(tickers))
    try:
        df = get_tickers_df(tickers)
    except Exception:
        log.exception("Failed processing %s index", name)
        raise

    output_path = f"{output_dir}/{name}.csv"
    try:
        export_to_csv(df, output_path)
    except Exception:
        log.exception("Failed exporting %s CSV to %s", name, output_path)
        raise

    return df


def fetch_summary_line(summary: dict[str, int]) -> str:
    return (
        "Fetched tickers: "
        f"{summary['successful']} successful, "
        f"{summary['failed']} failed, "
        f"{summary['skipped']} skipped"
    )


def export_combined(index_dfs: list[pd.DataFrame], output_dir: str) -> int:
    combined_df = pd.concat(index_dfs, ignore_index=True)
    if "Ticker" in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset="Ticker", keep="first")

    output_path = f"{output_dir}/combined.csv"
    try:
        export_to_csv(combined_df, output_path)
    except Exception:
        log.exception("Failed exporting combined CSV to %s", output_path)
        raise

    log.info("Exported combined CSV with %s rows", len(combined_df))
    return len(combined_df)


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
    fetch_summary = {"successful": 0, "failed": 0, "skipped": 0}
    for index in args.indexes:
        df = export_index(index, output_dir)
        index_dfs.append(df)
        df_fetch_summary = df.attrs.get("fetch_summary", {})
        for key in fetch_summary:
            fetch_summary[key] += df_fetch_summary.get(key, 0)

    if len(index_dfs) > 1:
        log.info(fetch_summary_line(fetch_summary))
    report_lines = [fetch_summary_line(fetch_summary)]
    if len(index_dfs) > 1:
        combined_rows = export_combined(index_dfs, output_dir)
        report_lines.append(f"Exported combined CSV with {combined_rows} rows")

    elapsed_seconds = time.monotonic() - start_time
    elapsed = format_elapsed(elapsed_seconds)
    log.info("Completed in %s", elapsed)
    report_lines.append(f"Completed in {elapsed}")
    send_report(report_lines)
