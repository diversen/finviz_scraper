# finviz_scraper/get_tickers.py

from __future__ import annotations

import hashlib
import os
import time
from io import StringIO
from pathlib import Path
from typing import List

import pandas as pd
import requests

from finviz_scraper.logging import get_log


# ---------- helpers ----------

log = get_log()

# Identify your script + contact (recommended for automated access).
_UA = "finviz_scraper/1.0 (contact: you@example.com) requests/2.x"

# Simple disk cache (1 file per URL)
_CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "finviz_scraper"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours

# Reuse a session (connection pooling) + shared headers
_session = requests.Session()
_session.headers.update(
    {
        "User-Agent": _UA,
        "Accept-Encoding": "gzip",
    }
)

# Gentle pacing to avoid request bursts
_last_request_ts = 0.0
_MIN_INTERVAL_SECONDS = 1.5

NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"
NASDAQ100_URL = "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies"


def _cache_path(url: str) -> Path:
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return _CACHE_DIR / f"{h}.html"


def _fetch_html(url: str) -> str:
    """
    Fetch HTML with:
      - 24h on-disk caching
      - polite pacing between requests
      - retries with exponential backoff (and Retry-After if provided)
    """
    global _last_request_ts

    # 1) Cache
    p = _cache_path(url)
    if p.exists():
        age = time.time() - p.stat().st_mtime
        if age < _CACHE_TTL_SECONDS:
            return p.read_text(encoding="utf-8", errors="ignore")

    # 2) Pacing (avoid bursts)
    now = time.time()
    wait = _MIN_INTERVAL_SECONDS - (now - _last_request_ts)
    if wait > 0:
        time.sleep(wait)

    # 3) Retry with backoff
    backoff = 5.0
    last_response: requests.Response | None = None
    last_error: requests.RequestException | None = None

    for _ in range(5):
        try:
            r = _session.get(url, timeout=30)
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(int(backoff))
            backoff = min(backoff * 2, 120)
            continue

        last_response = r
        _last_request_ts = time.time()

        if r.status_code == 200:
            text = r.text
            p.write_text(text, encoding="utf-8", errors="ignore")
            return text

        if r.status_code in (403, 429):
            ra = r.headers.get("Retry-After")
            if ra and ra.isdigit():
                sleep_s = int(ra)
            else:
                sleep_s = int(backoff)
                backoff = min(backoff * 2, 120)

            time.sleep(sleep_s)
            continue

        r.raise_for_status()

    # Out of retries; raise something meaningful
    if p.exists():
        return p.read_text(encoding="utf-8", errors="ignore")
    if last_response is not None:
        last_response.raise_for_status()
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Failed to fetch {url} (no response)")


def _normalize_symbol(s: str) -> str:
    # Normalize common dot tickers to dash (e.g., BRK.B -> BRK-B) for Yahoo/finviz style.
    return s.strip().replace(".", "-")


# ---------- NASDAQ Trader sources ----------


def tickers_nasdaq() -> List[str]:
    """
    Downloads list of tickers currently listed on NASDAQ (from nasdaqlisted.txt).
    """
    raw = _fetch_html(NASDAQ_LISTED_URL)
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
    Downloads list of tickers from otherlisted.txt (NYSE/AMEX etc.) on NASDAQ Trader.
    """
    raw = _fetch_html(OTHER_LISTED_URL)
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
    tables = pd.read_html(StringIO(html), flavor="lxml")
    # Find the table that has a 'Symbol' column.
    df = next((t for t in tables if "Symbol" in t.columns), None)
    if df is None:
        raise RuntimeError("Could not find S&P 500 constituents table (no 'Symbol' column).")
    tickers = [_normalize_symbol(s) for s in df["Symbol"].astype(str).tolist()]
    return sorted(tickers)


def tickers_nasdaq100() -> List[str]:
    """Downloads list of tickers currently listed in the Nasdaq-100 from Wikipedia."""
    html = _fetch_html(NASDAQ100_URL)
    tables = pd.read_html(StringIO(html), flavor="lxml")
    # Prefer a table with a 'Ticker' column; some revisions use 'Ticker' or 'Symbol'.
    df = next((t for t in tables if any(c in t.columns for c in ("Ticker", "Symbol"))), None)
    if df is None:
        raise RuntimeError("Could not find Nasdaq-100 table with 'Ticker' or 'Symbol' column.")
    col = "Ticker" if "Ticker" in df.columns else "Symbol"
    tickers = [_normalize_symbol(s) for s in df[col].astype(str).tolist()]
    return sorted(tickers)


def tickers_c25() -> List[str]:
    """Downloads list of tickers currently listed in the OMX Copenhagen 25 from Wikipedia."""
    html = _fetch_html("https://en.wikipedia.org/wiki/OMX_Copenhagen_25")
    tables = pd.read_html(StringIO(html), flavor="lxml")
    # Common column names: 'Ticker symbol', sometimes 'Symbol'.
    df = next((t for t in tables if any(c in t.columns for c in ("Ticker symbol", "Symbol"))), None)
    if df is None:
        raise RuntimeError("Could not find C25 table with 'Ticker symbol' or 'Symbol'.")
    col = "Ticker symbol" if "Ticker symbol" in df.columns else "Symbol"
    # Wikipedia often has spaces in Danish tickers; replace with hyphen, then normalize dots.
    tickers: List[str] = []
    for s in df[col].astype(str).tolist():
        s = s.strip().replace(" ", "-")
        s = _normalize_symbol(s)
        tickers.append(s)
    return sorted(tickers)


# ---------- Combined ----------

def tickers_all() -> List[str]:
    sources = [
        ("sp500", tickers_sp500),
        ("nasdaq", tickers_nasdaq),
        ("other", tickers_other),
        ("c25", tickers_c25),
    ]
    ticker_groups: list[str] = []
    for name, fetch_tickers in sources:
        try:
            ticker_groups.extend(fetch_tickers())
        except Exception:
            log.exception("Failed to fetch %s ticker list while building all", name)
            raise

    # Combine, de-duplicate, and sort
    return sorted(set(ticker_groups))
