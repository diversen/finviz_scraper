#!/bin/sh
rm -rf ./cache
./venv/bin/python3.8 csv_from_sp500.py
./venv/bin/python3.8 csv_from_nasdaq.py
./venv/bin/python3.8 csv_from_other.py
./venv/bin/python3.8 csv_from_nasdaq100.py
./venv/bin/python3.8 csv_from_all.py

