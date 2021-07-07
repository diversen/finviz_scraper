from finviz_scrapper.finviz import get_fundamentals_cleaned, get_fundamentals_df, get_fundamentals_dict_raw

symbol = 'AAL'

# Get fundamentals as a pandas dataframe, values are as found on finviz
symbol_df = get_fundamentals_df(symbol)

# Get fundamentals raw as a dict
symbol_raw_dict = get_fundamentals_dict_raw(symbol)

# Get fundamentals as a cleaned dict
# M, B, T are turned into floatts. '2M' => 2000000
# Percentages are turned into floats. '10%' => 0.1
# Empty values '-' are turned into np.nan
aapl = get_fundamentals_cleaned('aapl')
print(aapl)
