from datetime import datetime
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


def _export(fetch_tickers: Callable[[], list[str]], name: str) -> None:
    today = datetime.today().strftime("%Y-%m-%d")
    df = get_tickers_df(fetch_tickers())
    export_to_csv(df, f"./csv/{today}/{name}.csv")


def all_tickers() -> None:
    _export(tickers_all, "all")


def c25() -> None:
    _export(tickers_c25, "c25")


def nasdaq() -> None:
    _export(tickers_nasdaq, "nasdaq")


def nasdaq100() -> None:
    _export(tickers_nasdaq100, "nasdaq100")


def other() -> None:
    _export(tickers_other, "other")


def sp500() -> None:
    _export(tickers_sp500, "sp500")
