import pandas as pd
import ftplib
import io


# copied from yahoo_fin
def tickers_nasdaq():
    '''
    Downloads list of tickers currently listed in the NASDAQ
    '''

    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")

    r = io.BytesIO()
    ftp.retrbinary('RETR nasdaqlisted.txt', r.write)

    info = r.getvalue().decode()
    splits = info.split("|")

    tickers = [x for x in splits if "\r\n" in x]
    tickers = [x.split("\r\n")[1]
               for x in tickers if "NASDAQ" not in x != "\r\n"]
    tickers = [ticker for ticker in tickers if "File" not in ticker]
    tickers = [ticker for ticker in tickers if len(ticker)]

    ftp.close()

    return tickers


def tickers_sp500():
    '''Downloads list of tickers currently listed in the S&P 500 '''
    # get list of all S&P 500 stocks
    sp500 = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    sp_tickers = sorted(sp500.Symbol.tolist())

    for i, ticker in enumerate(sp_tickers):
        if '.' in ticker:
            sp_tickers[i] = ticker.replace('.', '-')

    return sp_tickers

def tickers_nasdaq100():
    '''Downloads list of tickers currently listed in the S&P 500 '''
    # get list of all S&P 500 stocks
    nasdaq100 = pd.read_html(
        "https://en.wikipedia.org/wiki/Nasdaq-100")[4]

    tickers = sorted(nasdaq100.Ticker.tolist())
    for i, ticker in enumerate(tickers):
        if '.' in ticker:
            tickers[i] = ticker.replace('.', '-')

    return tickers


def tickers_other():
    '''Downloads list of tickers currently listed in the "otherlisted.txt"
       file on "ftp.nasdaqtrader.com" '''
    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")

    r = io.BytesIO()
    ftp.retrbinary('RETR otherlisted.txt', r.write)

    info = r.getvalue().decode()
    splits = info.split("|")

    tickers = [x for x in splits if "\r\n" in x]
    tickers = [x.split("\r\n")[1] for x in tickers]
    tickers = [ticker for ticker in tickers if "File" not in ticker]
    tickers = [ticker for ticker in tickers if len(ticker)]

    ftp.close()

    return tickers


def tickers_c25():
    '''Downloads list of tickers currently listed in the c25 '''
    # get list of all S&P 500 stocks
    sp500 = pd.read_html(
        "https://en.wikipedia.org/wiki/OMX_Copenhagen_25")[0]
    sp_tickers = sorted(sp500["Ticker symbol"].tolist())

    for i, ticker in enumerate(sp_tickers):
        sp_tickers[i] = ticker.replace(' ', '-')
        if '.' in ticker:
            sp_tickers[i] = ticker.replace('.', '-')

        # sp_tickers[i] += '.CO'
    return sp_tickers

def tickers_all ():
    sp500 = tickers_sp500()
    nasdaq = tickers_nasdaq()
    others = tickers_other()

    all = sp500 + nasdaq + others 

    return sorted(list(set(all)))


