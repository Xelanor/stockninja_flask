from .constants.tickers import currencies
import json
from .utils import get_current_tickers_data, rateCalculator


def fetch_all_currencies():
    result = []
    currency_names = ",".join(currencies)

    currency_data = get_current_tickers_data(currency_names)
    negative = 0
    total = 0

    gold = {"price": 0, "prevClose": 0}
    dollar_tl = {"price": 0, "prevClose": 0}

    for data_dict in currency_data:
        price = data_dict["regularMarketPrice"]
        prevClose = data_dict["regularMarketPreviousClose"]
        stock_name = data_dict["symbol"]

        if stock_name == "GC=F":
            gold['price'] = price
            gold['prevClose'] = prevClose

        if stock_name == "TRY=X":
            dollar_tl['price'] = price
            dollar_tl['prevClose'] = prevClose

        rate = rateCalculator(price, prevClose)
        negative += 1 if rate < 0 else 0
        total += 1

        try:
            stock_dict = {
                "stockName": stock_name,
                "price": round(price, 4),
                "shortName": data_dict["shortName"],
                "dayRange": data_dict["regularMarketDayRange"],
                "rate": rate
            }

            result.append(stock_dict)
        except:
            pass

    gram_altin = {"price": gold['price'] / 31 * dollar_tl['price'],
                  "prevClose": gold['prevClose'] / 31 * dollar_tl['prevClose']}
    stock_dict = {
        "stockName": "Gram Altın",
        "price": round(gram_altin['price'], 4),
        "shortName": "Gram Altın",
        "dayRange": "-",
        "rate": rateCalculator(gram_altin['price'], gram_altin['prevClose'])
    }

    result.append(stock_dict)

    result = sorted(result, key=lambda k: k['stockName'])

    result.append(negative)
    result.append(total)
    return result
