import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import urllib.error

from sqlite_cache.sqlite_cache import SqliteCache
import time
import logging
import traceback
import os

sql_cache = SqliteCache('cache')


def get_fundamentals_df(symbol):
    """
    From: https://gist.github.com/shashankvemuri/b791e316efa18c8707fb912f69760b09
    get the fundamentals as pandas dataframe by a symbol, e.g. 'AAPL'
    """

    html = sql_cache.get(symbol)

    # In cache but 404
    if html == '404':
        raise Exception('404 from cache: ' + str(symbol))

    # not in cache
    elif not html:
        try:

            time.sleep(1)
            url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            html = soup(webpage, "html.parser")
            sql_cache.set(symbol, str(html))
            print("Got ticker from finviz:", symbol)

        except urllib.error.HTTPError as HTTPError:
            if HTTPError.code == 404:
                sql_cache.set(symbol, str(HTTPError.code))
                raise Exception("Got 404 from finviz: " + symbol)
            else:
                raise(HTTPError)

    else:
        print("Got ticker from cache: " + symbol)

    # Find fundamentals table
    fundamentals = pd.read_html(
        str(html), attrs={'class': 'snapshot-table2'})[0]

    # Clean up fundamentals dataframe
    fundamentals.columns = ['0', '1', '2', '3',
                            '4', '5', '6', '7', '8', '9', '10', '11']
    colOne = []
    colLength = len(fundamentals)
    for k in np.arange(0, colLength, 2):
        val = fundamentals[f'{k}']
        colOne.append(val)
    attrs = pd.concat(colOne, ignore_index=True)

    colTwo = []
    colLength = len(fundamentals)
    for k in np.arange(1, colLength, 2):
        val = fundamentals[f'{k}']
        colTwo.append(val)
    vals = pd.concat(colTwo, ignore_index=True)

    fundamentals = pd.DataFrame()
    fundamentals['Attributes'] = attrs
    fundamentals['Values'] = vals
    fundamentals = fundamentals.set_index('Attributes')
    return fundamentals


def _convertable_to_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_fundamentals_dict_raw(symbol):

    df = get_fundamentals_df(symbol)

    values_dict = df.to_dict()
    values_dict = values_dict["Values"]

    return values_dict


def _sanitize_value(value):
    value = value.strip()
    if value == '-':
        value = np.nan
        return value

    if value.endswith('%'):
        value = value.replace("%", "")
        if _convertable_to_float(value):
            value = float(value) / 100
            value = str(value)

    if value.endswith('M'):
        value = value.replace("M", "")
        value = str(float(value) * 1000000)

    if value.endswith('B'):
        value = value.replace("B", "")
        value = str(float(value) * 1000000000)

    if value.endswith('T'):
        value = value.replace("T", "")
        value = str(float(value) * 1000000000000)

    if _convertable_to_float(value):
        return float(value)
    else:
        return value


def get_fundamentals_cleaned(symbol):

    ticker = get_fundamentals_dict_raw(symbol)

    week_range_52 = ticker['52W Range'].split('-')
    ticker['52 low'] = week_range_52[0]
    ticker['52 high'] = week_range_52[1]

    for key, value in ticker.items():
        ticker[key] = _sanitize_value(value)

    ticker['Ticker'] = symbol
    return ticker


def get_tickers_df(tickers, max_n=False, show_tracekack=False):
    """ Get tickers as a dataframe """

    n = 0
    df = pd.DataFrame()
    for ticker in tickers:
        try:
            data = get_fundamentals_cleaned(ticker)

            if not data:
                print('No data in {}'.format(ticker))
                continue

            df = df.append(data, ignore_index=True)

        except Exception as e:

            if show_tracekack:
                logging.warning('Failed fetching {}'.format(ticker))
                tb = traceback.format_exc()
                logging.warning(tb)
            else:
                print(e)

        n += 1
        if max_n and n > max_n:
            break

    df['Price Feature'] = df['Price']
    return df


def export_to_csv(df, filename):
    """
    Export to CSV from dataframe from a given filename
    Dirs in the filename that does not exists will be created
    """
    dirname = os.path.dirname(filename)
    os.makedirs(dirname, exist_ok=True)

    df.to_csv(filename, index=False)
