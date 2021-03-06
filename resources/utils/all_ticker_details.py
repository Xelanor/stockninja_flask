from .constants.tickers import tickers
import json
from .utils import get_current_tickers_data, rateCalculator


def fetch_all_stocks():
    result = []
    stock_names = ",".join(tickers)

    stocks_data = get_current_tickers_data(stock_names)
    negative = 0
    total = 0

    for data_dict in stocks_data:
        price = data_dict["regularMarketPrice"]
        prevClose = data_dict["regularMarketPreviousClose"]

        rate = rateCalculator(price, prevClose)
        negative += 1 if rate < 0 else 0
        total += 1

        try:
            stock_name = data_dict["symbol"]

            stock_dict = {
                "stockName": stock_name,
                "price": price,
                "shortName": data_dict["shortName"],
                "dayRange": data_dict["regularMarketDayRange"],
                "rate": rate
            }

            result.append(stock_dict)
        except:
            pass

    result.append(negative)
    result.append(total)
    return result
