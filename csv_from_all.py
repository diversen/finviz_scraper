from finviz_scraper.get_tickers import tickers_all
from finviz_scraper.finviz import get_tickers_df, export_to_csv
from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')

tickers = tickers_all()
df = get_tickers_df(tickers)

export_to_csv(df, './csv/' + today + '/all.csv')

