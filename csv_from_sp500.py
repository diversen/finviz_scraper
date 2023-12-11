from finviz_scraper.get_tickers import tickers_sp500
from finviz_scraper.finviz import get_tickers_df, export_to_csv
from datetime import datetime

today = datetime.today().strftime("%Y-%m-%d")

tickers = tickers_sp500()
df = get_tickers_df(tickers)

export_to_csv(df, "./csv/" + today + "/sp500.csv")
