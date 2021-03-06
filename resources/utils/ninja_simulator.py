import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
from pprint import pprint
import matplotlib.pyplot as plt
import json
from statistics import mean

from .constants.tickers import valuable_tickers
from .utils import epoch_to_date, calculate_williams_index, calculate_triple_index, calculate_aroon_index, calculate_ninja_index, calculate_rsi_index


class Simulation:
    def __init__(self, stock_name, money, buy_conditions, sell_conditions):
        self.today = ""
        self.stock_name = stock_name
        self.initial_money = money
        self.money = money
        self.portfolio = {stock_name: 0}
        self.transaction_log = []
        self.moneys = []
        self.buy_conditions = buy_conditions
        self.sell_conditions = sell_conditions

    def get_prices_yearly(self):
        values = {"prices": [], "dates": []}
        df = pd.read_csv("prices.csv", index_col="Date",
                         parse_dates=True)[self.stock_name]

        values['prices'] = df.tolist()
        timestamps = df.index.values.tolist()

        for timestamp in timestamps:
            date = epoch_to_date(int(str(timestamp)[:-9]))
            values['dates'].append(date)

        self.today = values['dates'][0]

        return values

    def get_prices_monthly(self):
        values = {"prices": [], "dates": []}
        QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/chart/{}?range=32d&interval=1d&indicators=quote&includeTimestamps=true".format(
            self.stock_name)

        res = requests.get(QUERY_URL)
        stocks_data = res.json()["chart"]["result"][0]

        values['prices'] = stocks_data["indicators"]["quote"][0]["close"]

        for i in range(len(values['prices'])):  # Handle null values
            if values['prices'][i] == None:
                values['prices'][i] = values['prices'][i-1]

        if values['prices'][-1] == None:
            del values['prices'][-1]
        timestamps = stocks_data["timestamp"]

        for timestamp in timestamps:
            date = epoch_to_date(timestamp)
            values['dates'].append(date)

        self.today = values['dates'][0]

        return values

    def transaction(self, amount, price, t_type, info):
        data = {
            "amount": amount, "price": price, "date": self.today, "type": t_type, "info": info
        }
        self.transaction_log.append(data)

    def buy(self, amount, price, info):
        self.money -= amount * price
        self.portfolio[self.stock_name] += amount
        self.transaction(amount, price, "buy", info)
        self.money = 0

    def sell(self, amount, price, info):
        self.money += amount * price
        self.portfolio[self.stock_name] -= amount
        self.transaction(amount, price, "sell", info)

    def calculate_consecutive_days(self, data):
        data = data[::-1]

        # If positive increasing else decreasing
        first_event = data[0] - data[1]
        first_event = True if first_event >= 0 else False

        days = 1

        for i in range(1, len(data) - 1):
            event = True if data[i] - data[i + 1] >= 0 else False

            if event == first_event:
                days += 1
            else:
                break

        return days, first_event

    def price_condition(self, conditions):
        if not 'price' in conditions:
            return True

        price_enabled = conditions['price']['checked']
        if not price_enabled:
            return True  # Buy

        price_day = conditions['price']['priceDay']
        price_percentage_lower = conditions['price']['pricePercentageLower']
        price_percentage_upper = conditions['price']['pricePercentageUpper']
        price_condition = conditions['price']['priceCondition']

        if price_condition == "Yüksek":
            if not ((self.current_price > self.prices_until_today[-1 * (price_day + 1)] * (price_percentage_lower + 100) / 100)
                    and (self.current_price < self.prices_until_today[-1 * (price_day + 1)] * (price_percentage_upper + 100) / 100)):
                return False  # Dont buy
        elif price_condition == "Sıralı Düşük":
            # If state positive increasing else decreasing
            days, state = self.calculate_consecutive_days(
                self.prices_until_today[-10:])
            if state:
                return False
            if days < price_day:
                return False
            if not ((self.current_price < self.prices_until_today[-1 * (price_day + 1)] * (-1 * price_percentage_lower + 100) / 100)
                    and (self.current_price > self.prices_until_today[-1 * (price_day + 1)] * (-1 * price_percentage_upper + 100) / 100)):
                return False  # Dont buy
        elif price_condition == "Sıralı Yüksek":
            # If state positive increasing else decreasing
            days, state = self.calculate_consecutive_days(
                self.prices_until_today[-10:])
            if not state:
                return False
            if days < price_day:
                return False
            if not ((self.current_price > self.prices_until_today[-1 * (price_day + 1)] * (price_percentage_lower + 100) / 100)
                    and (self.current_price < self.prices_until_today[-1 * (price_day + 1)] * (price_percentage_upper + 100) / 100)):
                return False  # Dont buy
        elif price_condition == "Düşük":
            if not ((self.current_price < self.prices_until_today[-1 * (price_day + 1)] * (-1 * price_percentage_lower + 100) / 100)
                    and (self.current_price > self.prices_until_today[-1 * (price_day + 1)] * (-1 * price_percentage_upper + 100) / 100)):
                return False  # Dont buy

        return True

    def calculate_triple_index(self, historic_data, data_scope, short, medium, long_):
        short = int(short)
        long_ = int(long_)
        short_data = historic_data[-1 * (data_scope + short):]
        medium_data = historic_data[-1 * (data_scope + medium):]
        long_data = historic_data[-1 * (data_scope + long_):]

        triple_index_values = {"short_list": [],
                               "medium_list": [], "long_list": []}

        for i in range(0, data_scope):
            try:
                triple_index_values["short_list"].append(
                    mean(short_data[i:i+short]))
                triple_index_values["medium_list"].append(
                    mean(medium_data[i:i+medium]))
                triple_index_values["long_list"].append(
                    mean(long_data[i:i+long_]))
            except Exception as ex:
                print(ex)
                pass

        return triple_index_values

    def triple_condition(self, conditions):
        if not 'triple' in conditions:
            return True

        triple_enabled = conditions['triple']['checked']
        if not triple_enabled:
            return True  # Buy

        triple_short = int(conditions['triple']['short'])
        triple_medium = int(conditions['triple']['medium'])
        triple_long = int(conditions['triple']['long'])
        triple_price_value = int(conditions['triple']['price'])
        triple_short_value = int(conditions['triple']['short_value'])
        triple_medium_value = int(conditions['triple']['medium_value'])
        triple_long_value = int(conditions['triple']['long_value'])
        triple_price_compare = conditions['triple']['price_compare']
        triple_short_compare = conditions['triple']['short_compare']
        triple_medium_compare = conditions['triple']['medium_compare']
        triple_long_compare = conditions['triple']['long_compare']

        values = self.calculate_triple_index(
            self.prices_until_today, 3, triple_short, triple_medium, triple_long)

        price = self.current_price
        short = values["short_list"][-1]
        medium = values["medium_list"][-1]
        long_ = values["long_list"][-1]

        triple_sorting_list = [0, 0, 0, 0]

        triple_sorting_list[triple_price_value - 1] = price
        triple_sorting_list[triple_short_value - 1] = short
        triple_sorting_list[triple_medium_value - 1] = medium
        triple_sorting_list[triple_long_value - 1] = long_

        if not (triple_sorting_list[3] > triple_sorting_list[2] and
                triple_sorting_list[2] > triple_sorting_list[1] and
                triple_sorting_list[1] > triple_sorting_list[0]):
            return False

        if triple_price_compare == ">":
            if not (price > self.prices_until_today[-2]):
                return False
        elif triple_price_compare == "<":
            if not (price < self.prices_until_today[-2]):
                return False

        if triple_short_compare == ">":
            if not (short > values["short_list"][-2]):
                return False
        elif triple_short_compare == "<":
            if not (short < values["short_list"][-2]):
                return False

        if triple_medium_compare == ">":
            if not (medium > values["medium_list"][-2]):
                return False
        elif triple_medium_compare == "<":
            if not (medium < values["medium_list"][-2]):
                return False

        if triple_long_compare == ">":
            if not (long_ > values["long_list"][-2]):
                return False
        elif triple_long_compare == "<":
            if not (long_ < values["long_list"][-2]):
                return False

        return True

    def rsi_condition(self, conditions):
        if not 'rsi' in conditions:
            return True

        rsi_enabled = conditions['rsi']['checked']
        if not rsi_enabled:
            return True  # Buy

        rsi_first = conditions['rsi']['first_compare']
        rsi_second = conditions['rsi']['second_compare']
        rsi_third = conditions['rsi']['third_compare']
        rsi_value_lower = conditions['rsi']['rsi_value_lower']
        rsi_value_upper = conditions['rsi']['rsi_value_upper']

        if rsi_first == ">":
            if not (self.rsi_values[-1] > self.rsi_values[-2]):
                return False
        elif rsi_first == "<":
            if not (self.rsi_values[-1] < self.rsi_values[-2]):
                return False
        if rsi_second == ">":
            if not (self.rsi_values[-2] > self.rsi_values[-3]):
                return False
        elif rsi_second == "<":
            if not (self.rsi_values[-2] < self.rsi_values[-3]):
                return False
        if rsi_third == ">":
            if not (self.rsi_values[-3] > self.rsi_values[-4]):
                return False
        elif rsi_third == "<":
            if not (self.rsi_values[-3] < self.rsi_values[-4]):
                return False

        if not (self.rsi_values[-1] >= rsi_value_lower and self.rsi_values[-1] <= rsi_value_upper):
            return False

        return True

    def sell_trace_condition(self):
        if not 'trace' in self.sell_conditions:
            return True

        trace_enabled = self.sell_conditions['trace']['checked']
        if not trace_enabled:
            return True  # Sell

        if self.current_price > self.sell_tracing_price:
            self.sell_tracing_price = self.current_price

        trace_value = self.sell_conditions['trace']['value']

        if not (self.current_price < self.sell_tracing_price * (100 - trace_value) / 100):
            return False

        self.sell_tracing_price = 0
        return True

    def aroon_condition(self):
        if not 'aroon' in self.buy_conditions:
            return True

        aroon_enabled = self.buy_conditions['aroon']['checked']
        if not aroon_enabled:
            return False

        up_lower = self.buy_conditions['aroon']['up_lower']
        up_upper = self.buy_conditions['aroon']['up_upper']
        down_lower = self.buy_conditions['aroon']['down_lower']
        down_upper = self.buy_conditions['aroon']['down_upper']
        aroon_compare = self.buy_conditions['aroon']['aroon_compare']
        uptrend = self.buy_conditions['aroon']['uptrend']
        downtrend = self.buy_conditions['aroon']['downtrend']

        aroon = calculate_aroon_index(self.prices_until_today, 3)

        up_condition = up_lower <= aroon['upper'][-1] and aroon['upper'][-1] <= up_upper
        down_condition = down_lower <= aroon['lower'][-1] and aroon['lower'][-1] <= down_upper

        if uptrend == "↑":
            uptrend_condition = aroon['upper'][-1] >= aroon['upper'][-2]
        elif uptrend == "↓":
            uptrend_condition = aroon['upper'][-1] <= aroon['upper'][-2]
        else:
            uptrend_condition = True

        if downtrend == "↑":
            downtrend_condition = aroon['lower'][-1] >= aroon['lower'][-2]
        elif downtrend == "↓":
            downtrend_condition = aroon['lower'][-1] <= aroon['lower'][-2]
        else:
            downtrend_condition = True

        if aroon_compare == "VE":
            if up_condition and down_condition and uptrend_condition and downtrend_condition:
                return True
            else:
                return False

        elif aroon_compare == "VEYA":
            if (up_condition and down_condition) or (uptrend_condition and downtrend_condition):
                return True
            else:
                return False

        return up_condition and down_condition

    def after_sell_condition(self):
        if not 'after_sell' in self.buy_conditions:
            return True

        after_sell_enabled = self.buy_conditions['after_sell']['checked']
        if not after_sell_enabled:
            return True

        if len(self.transaction_log) == 0:
            return True

        after_sell_percent = self.buy_conditions['after_sell']['percent']
        after_sell_period = self.buy_conditions['after_sell']['period']

        if self.current_price < self.prices_until_today[-2]:
            self.after_sell_values["min"] = self.current_price
            self.after_sell_values["days"] = 0

        self.after_sell_values["days"] += 1

        if self.after_sell_values["days"] >= after_sell_period and \
                self.current_price * (1 - (after_sell_percent / 100)) > self.after_sell_values["min"]:

            return True
        return False

    def buy_condition(self):
        after_sell_option = self.after_sell_condition()
        if not after_sell_option:
            return False

        aroon_option = self.aroon_condition()
        if aroon_option:
            return False

        price_option = self.price_condition(self.buy_conditions)
        if not price_option:
            return False

        triple_option = self.triple_condition(self.buy_conditions)
        if not triple_option:
            return False

        rsi_option = self.rsi_condition(self.buy_conditions)
        if not rsi_option:
            return False

        return True

    def sell_condition(self):
        price_option = self.price_condition(self.sell_conditions)
        if not price_option:
            return False

        triple_option = self.triple_condition(self.sell_conditions)
        if not triple_option:
            return False

        rsi_option = self.rsi_condition(self.sell_conditions)
        if not rsi_option:
            return False

        trace_option = self.sell_trace_condition()
        if not trace_option:
            return False

        return True

    def simulation(self, period):
        if period == "yearly":
            values = self.get_prices_yearly()
        elif period == "monthly":
            values = self.get_prices_monthly()

        calculation_prices = values["prices"]
        prices = values["prices"][30:]
        dates = values["dates"][30:]
        self.sell_tracing_price = 0
        self.buy_days = []
        self.sell_days = []
        self.after_sell_values = {"min": 0, "days": 0}

        for i in range(1, len(dates)):
            self.today = dates[i]
            self.current_price = round(prices[i], 2)
            self.prices_until_today = calculation_prices[i:(
                i + 31)]  # Last 30 days

            current_money = self.money + \
                (self.current_price * self.portfolio[self.stock_name])
            # Her gün sahip olduğum para miktarı
            self.moneys.append(current_money)
            self.rsi_values = calculate_rsi_index(self.prices_until_today, 5)

            if self.money > 0:
                if not self.buy_condition():
                    continue

                buy_amount = self.money / self.current_price
                info = ""
                self.buy(buy_amount, self.current_price, info)
                self.buy_days.append(i)

            elif self.money <= 0:
                if not self.sell_condition():
                    continue

                sell_amount = self.portfolio[self.stock_name]
                info = ""
                self.sell(sell_amount, self.current_price, info)
                self.sell_days.append(i)

                self.after_sell_values["min"] = self.current_price

        final_money = self.moneys[-1]
        print("Stock Name: %s" % self.stock_name)
        print("Final Money: %s" % final_money)
        print("Buy Days: %s" % self.buy_days)
        print("Sell Days: %s" % self.sell_days)

        return self.moneys, self.buy_days, self.sell_days


def run(buy_conditions, sell_conditions, stocks, period):
    all_ticker_values = []
    buyable_tickers = []
    for ticker in stocks:
        sim = Simulation(ticker, 10000, buy_conditions, sell_conditions)
        values, buy_days, sell_days = sim.simulation(period)
        all_ticker_values.append(values)

        if len(buy_days) >= 1:
            buyable_tickers.append(ticker)

    values = [sum(x) for x in zip(*all_ticker_values)]

    return values, buyable_tickers, buy_days, sell_days

# df = pd.DataFrame([sum(x) for x in zip(*all_ticker_values)])
# plt.plot(df)
# plt.show()
