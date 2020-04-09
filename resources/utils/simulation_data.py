import pandas_datareader as web
from constants.tickers import valuable_tickers

prices = web.DataReader(["AGHOL.IS"], "yahoo",
                        start="2019-3-27", end="2020-3-29")['Close']

print(prices)
