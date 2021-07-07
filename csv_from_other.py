from finviz_scraper.get_tickers import tickers_other
from finviz_scraper.finviz import get_tickers_df, export_to_csv
from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')

tickers = tickers_other()
df = get_tickers_df(tickers)

export_to_csv(df, './csv/' + today + '/other.csv')

