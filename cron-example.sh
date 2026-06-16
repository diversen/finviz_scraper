#!/bin/sh
cd "$(dirname "$0")" || exit 1

rm -rf ./cache
.venv/bin/python finviz_csv.py sp500 nasdaq other nasdaq100 all
