#!/bin/sh
cd "$(dirname "$0")" || exit 1

rm -rf ./cache
uv run python csv_from_sp500.py
uv run python csv_from_nasdaq.py
uv run python csv_from_other.py
uv run python csv_from_nasdaq100.py
uv run python csv_from_all.py
