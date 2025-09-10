# finviz_scraper/get_tickers.py

from __future__ import annotations

import io
import ftplib
from typing import List

import pandas as pd
import requests


# ---------- helpers ----------

_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def _fetch_html(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": _UA}, timeout=30)
    r.raise_for_status()
    return r.text


def _normalize_symbol(s: str) -> str:
    # Normalize common dot tickers to dash (e.g., BRK.B -> BRK-B) for Yahoo/finviz style.
    return s.strip().replace(".", "-")


# ---------- NASDAQ FTP sources ----------

def _ftp_retrieve_bytes(path: str, filename: str) -> bytes:
    ftp = ftplib.FTP("ftp.nasdaqtrader.com", timeout=30)
    try:
        ftp.login()
        ftp.cwd(path)
        buf = io.BytesIO()
        ftp.retrbinary(f"RETR {filename}", buf.write)
        return buf.getvalue()
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()


def tickers_nasdaq() -> List[str]:
    """
    Downloads list of tickers currently listed on NASDAQ (from nasdaqlisted.txt).
    """
    raw = _ftp_retrieve_bytes("SymbolDirectory", "nasdaqlisted.txt").decode(errors="ignore")
    symbols: List[str] = []
    for line in raw.splitlines():
        # Skip footer line and header
        if line.startswith("File Creation Time") or line.startswith("Symbol|"):
            continue
        parts = line.split("|")
        if not parts or not parts[0] or parts[0] == "Symbol":
            continue
        sym = parts[0].strip()
        if sym:
            symbols.append(_normalize_symbol(sym))
    return symbols


def tickers_other() -> List[str]:
    """
    Downloads list of tickers from otherlisted.txt (NYSE/AMEX etc.) on NASDAQ FTP.
    """
    raw = _ftp_retrieve_bytes("SymbolDirectory", "otherlisted.txt").decode(errors="ignore")
    symbols: List[str] = []
    for line in raw.splitlines():
        if line.startswith("File Creation Time") or line.startswith("ACT Symbol|"):
            continue
        parts = line.split("|")
        if not parts or not parts[0] or parts[0] == "ACT Symbol":
            continue
        sym = parts[0].strip()
        if sym:
            symbols.append(_normalize_symbol(sym))
    return symbols


# ---------- Wikipedia sources ----------

def tickers_sp500() -> List[str]:
    """Downloads list of tickers currently listed in the S&P 500 from Wikipedia."""
    html = _fetch_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    tables = pd.read_html(html, flavor="lxml")
    # Find the table that has a 'Symbol' column.
    df = next((t for t in tables if "Symbol" in t.columns), None)
    if df is None:
        raise RuntimeError("Could not find S&P 500 constituents table (no 'Symbol' column).")
    tickers = [_normalize_symbol(s) for s in df["Symbol"].astype(str).tolist()]
    return sorted(tickers)


def tickers_nasdaq100() -> List[str]:
    """Downloads list of tickers currently listed in the Nasdaq-100 from Wikipedia."""
    html = _fetch_html("https://en.wikipedia.org/wiki/Nasdaq-100")
    tables = pd.read_html(html, flavor="lxml")
    # Prefer a table with a 'Ticker' column; some revisions use 'Ticker' or 'Symbol'.
    df = next(
        (t for t in tables if any(c in t.columns for c in ("Ticker", "Symbol"))),
        None,
    )
    if df is None:
        raise RuntimeError("Could not find Nasdaq-100 table with 'Ticker' or 'Symbol' column.")
    col = "Ticker" if "Ticker" in df.columns else "Symbol"
    tickers = [_normalize_symbol(s) for s in df[col].astype(str).tolist()]
    return sorted(tickers)


def tickers_c25() -> List[str]:
    """Downloads list of tickers currently listed in the OMX Copenhagen 25 from Wikipedia."""
    html = _fetch_html("https://en.wikipedia.org/wiki/OMX_Copenhagen_25")
    tables = pd.read_html(html, flavor="lxml")
    # Common column names: 'Ticker symbol', sometimes 'Symbol'.
    df = next(
        (t for t in tables if any(c in t.columns for c in ("Ticker symbol", "Symbol"))),
        None,
    )
    if df is None:
        raise RuntimeError("Could not find C25 table with 'Ticker symbol' or 'Symbol'.")
    col = "Ticker symbol" if "Ticker symbol" in df.columns else "Symbol"
    # Wikipedia often has spaces in Danish tickers; replace with hyphen, then normalize dots.
    tickers = []
    for s in df[col].astype(str).tolist():
        s = s.strip().replace(" ", "-")
        s = _normalize_symbol(s)
        tickers.append(s)
    return sorted(tickers)


# ---------- Combined ----------

def tickers_all() -> List[str]:
    sp500 = tickers_sp500()
    nasdaq = tickers_nasdaq()
    others = tickers_other()
    c25 = tickers_c25()
    # Combine, de-duplicate, and sort
    return sorted(set(sp500 + nasdaq + others + c25))
