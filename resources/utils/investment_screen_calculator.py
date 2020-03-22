from collections import defaultdict
import json
from .utils import get_current_tickers_data


def fetch_prices_of_stocks(stocks_list):
    stocks_list = ",".join(list(set(stocks_list)))
    stocks_data = get_current_tickers_data(stocks_list)
    prices = {}

    for stock in stocks_data:
        stockName = stock['symbol']
        prices[stockName] = stock['regularMarketPrice']

    return prices


def calculate_total_current_equity(my_stocks, current_prices):
    total = 0

    for stockName, investments in my_stocks.items():
        current_price = float(current_prices[stockName])

        for investment in investments:
            total += current_price * float(investment['remaining'])

    return total


def calculate_purchased_value(my_stocks):
    total = 0

    for stockName, investments in my_stocks.items():
        for investment in investments:
            purchased_price = float(investment['price'])
            remaining = float(investment['remaining'])
            total += purchased_price * remaining

    return total


def calculate_stock_values(my_stocks, current_prices):
    result = defaultdict(dict)

    for stockName, investments in my_stocks.items():
        total_current_value = 0
        total_purchased_value = 0
        total_purchased_remaining = 0
        total_informed_count = 0
        result[stockName]["transactions"] = []

        # Hissenin güncel fiyatı
        current_price = float(current_prices[stockName])
        for investment in investments:
            purchased_price = float(investment['price'])  # Alış fiyatı
            remaining = float(investment['remaining'])  # Alınan miktar
            informed_count = float(investment['informCount'])  # Alınan miktar
            current_value = current_price * remaining  # Güncel toplam
            purchased_value = purchased_price * remaining  # Alış toplam

            total_current_value += current_value
            total_purchased_value += purchased_value
            total_purchased_remaining += remaining  # Toplam adet
            total_informed_count += informed_count  # Toplam haber sayısı

            investment_dict = {
                "id": str(investment['id']),
                "remaining": remaining,
                "informCount": int(informed_count),
                "current_value": round(current_price * remaining, 2),
                "date": str(investment['createdAt']),
                "profit_loss": round(current_value - purchased_value, 2),
                "purchased_price": purchased_price,
                "profit_rate": round((current_value - purchased_value) / purchased_value * 100, 2),
            }

            result[stockName]["transactions"].append(investment_dict)

        result[stockName]["unit_cost"] = round(
            total_purchased_value / total_purchased_remaining, 2)
        result[stockName]["remaining"] = round(total_purchased_remaining)
        result[stockName]["current_value"] = round(total_current_value, 2)
        result[stockName]["profit_loss"] = round(
            total_current_value - total_purchased_value, 2)
        result[stockName]["profit_rate"] = round(
            (total_current_value - total_purchased_value) / total_purchased_value * 100, 2)
        result[stockName]["informCount"] = int(total_informed_count)

    return result


def investment_screen_data(investments):
    stock_data = defaultdict(list)
    stock_names = []
    total_profit = 0

    for investment in investments:
        stockName = investment['name']
        if not investment['kind'] == "buy":
            if 'profit' in investment:
                total_profit += investment['profit']
            continue

        if investment['remaining'] <= 0:
            continue

        stock_data[stockName].append(investment)
        stock_names.append(stockName)

    current_prices = fetch_prices_of_stocks(stock_names)

    total_equity = calculate_total_current_equity(stock_data, current_prices)
    purchased_values = calculate_purchased_value(stock_data)
    potential_profit_loss = total_equity - purchased_values
    all_stocks_transactions_data = calculate_stock_values(
        stock_data, current_prices)

    result_dict = {
        "total_equity": round(total_equity, 2),
        "potential_profit_loss": round(potential_profit_loss, 2),
        "total_profit": round(total_profit, 2),
        "stock_values": all_stocks_transactions_data
    }

    return result_dict
