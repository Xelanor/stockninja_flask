import requests
from datetime import datetime, timedelta
import json
from .utils import rateCalculator, epoch_to_date


def my_ticker_details(stocks_targets):

    QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={}"

    stock_names = []
    for stock in stocks_targets:
        stock_names.append(stock['name'])

    result = []

    stock_names.sort()

    stock_names = ",".join(stock_names)
    res = requests.get(QUERY_URL.format(stock_names))
    stocks_data = res.json()["quoteResponse"]["result"]

    for data_dict in stocks_data:
        stock_name = data_dict["symbol"]

        for target_dict in stocks_targets:

            if stock_name == target_dict['name']:

                price = data_dict["regularMarketPrice"]
                prevClose = data_dict["regularMarketPreviousClose"]

                rate = rateCalculator(price, prevClose)

                stock_dict = {
                    "stockName": stock_name,
                    "date": epoch_to_date(data_dict["regularMarketTime"]),
                    "price": data_dict["regularMarketPrice"],
                    "shortName": data_dict["shortName"],
                    "dayRange": data_dict["regularMarketDayRange"],
                    "rate": rate
                }

                result.append(stock_dict)

    return result
