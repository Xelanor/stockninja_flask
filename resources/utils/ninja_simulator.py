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

    def get_prices(self):
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
        price_enabled = conditions['price']['checked']
        if not price_enabled:
            return True  # Buy

        price_day = conditions['price']['priceDay']
        price_percentage = conditions['price']['pricePercentage']
        price_condition = conditions['price']['priceCondition']

        if price_condition == "Yüksek":
            if self.current_price < self.prices_until_today[-1 * (price_day + 1)] * (price_percentage + 100) / 100:
                return False  # Dont buy
        elif price_condition == "Sıralı Düşük":
            # If state positive increasing else decreasing
            days, state = self.calculate_consecutive_days(
                self.prices_until_today[-10:])
            if state:
                return False
            if days < price_day:
                return False
            if self.current_price < self.prices_until_today[-1 * (price_day + 1)] * (price_percentage + 100) / 100:
                return False
        elif price_condition == "Sıralı Yüksek":
            # If state positive increasing else decreasing
            days, state = self.calculate_consecutive_days(
                self.prices_until_today[-10:])
            if not state:
                return False
            if days < price_day:
                return False
            if self.current_price > self.prices_until_today[-1 * (price_day + 1)] * (price_percentage + 100) / 100:
                return False  # Dont buy
        elif price_condition == "Düşük":
            if self.current_price > self.prices_until_today[-1 * (price_day + 1)] * (price_percentage + 100) / 100:
                return False  # Dont buy

        return True

    def calculate_triple_index(self, historic_data, data_scope, short, long_):
        short = int(short)
        long_ = int(long_)
        short_data = historic_data[-1 * (data_scope + short):]
        long_data = historic_data[-1 * (data_scope + long_):]

        triple_index_values = {"short_list": [], "long_list": []}

        for i in range(0, data_scope):
            try:
                triple_index_values["short_list"].append(
                    mean(short_data[i:i+short]))
                triple_index_values["long_list"].append(
                    mean(long_data[i:i+long_]))
            except Exception as ex:
                print(ex)
                pass

        return triple_index_values

    def triple_condition(self):
        triple_enabled = self.buy_conditions['triple']['checked']
        if not triple_enabled:
            return True  # Buy

        triple_short = self.buy_conditions['triple']['short']
        triple_long = self.buy_conditions['triple']['long']
        triple_first = self.buy_conditions['triple']['first']
        triple_second = self.buy_conditions['triple']['second']
        triple_third = self.buy_conditions['triple']['third']
        triple_first_compare = self.buy_conditions['triple']['first_compare']
        triple_first_perc = self.buy_conditions['triple']['first_percentage']
        triple_second_compare = self.buy_conditions['triple']['second_compare']
        triple_second_perc = self.buy_conditions['triple']['second_percentage']

        values = self.calculate_triple_index(
            self.prices_until_today, 2, triple_short, triple_long)

        price = self.current_price
        short = values["short_list"][-1]
        long_ = values["long_list"][-1]

        if triple_first == "F":
            a_value = price
        elif triple_first == "K":
            a_value = short
        elif triple_first == "U":
            a_value = long_

        if triple_second == "F":
            b_value = price
        elif triple_second == "K":
            b_value = short
        elif triple_second == "U":
            b_value = long_

        if triple_third == "F":
            c_value = price
        elif triple_third == "K":
            c_value = short
        elif triple_third == "U":
            c_value = long_

        rate_A = (a_value - b_value) / b_value * 100
        rate_B = (b_value - c_value) / c_value * 100

        if triple_first_compare == ">":
            if not (rate_A > 0 and rate_A < triple_first_perc):
                return False
        elif triple_first_compare == "<":
            if not (rate_A * -1 > 0 and rate_A * -1 < triple_first_perc):
                return False

        if triple_second_compare == ">":
            if not (rate_B > 0 and rate_B < triple_second_perc):
                return False
        elif triple_second_compare == "<":
            if not (rate_B * -1 > 0 and rate_B * -1 < triple_second_perc):
                return False

        return True

    def rsi_condition(self, conditions):
        rsi_enabled = conditions['rsi']['checked']
        if not rsi_enabled:
            return True  # Buy

        rsi_first = conditions['rsi']['first_compare']
        rsi_second = conditions['rsi']['second_compare']
        rsi_third = conditions['rsi']['third_compare']
        rsi_value = conditions['rsi']['rsi_value']
        rsi_compare = conditions['rsi']['rsi_compare']

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

        if rsi_compare == ">":
            if not (self.rsi_values[-1] > rsi_value):
                return False
        elif rsi_compare == "<":
            if not (self.rsi_values[-1] < rsi_value):
                return False

        return True

    def sell_trace_condition(self):
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
        aroon_enabled = self.buy_conditions['aroon']['checked']
        if not aroon_enabled:
            return True  # Buy

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

    def buy_condition(self):
        aroon_option = self.aroon_condition()
        if aroon_option:
            return False

        price_option = self.price_condition(self.buy_conditions)
        if not price_option:
            return False

        triple_option = self.triple_condition()
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

        rsi_option = self.rsi_condition(self.sell_conditions)
        if not rsi_option:
            return False

        trace_option = self.sell_trace_condition()
        if not trace_option:
            return False

        return True

    def simulation(self):
        values = self.get_prices()
        calculation_prices = values["prices"]
        prices = values["prices"][30:]
        dates = values["dates"][30:]
        self.sell_tracing_price = 0
        self.buy_days = []
        self.sell_days = []

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

        final_money = self.moneys[-1]
        print("Stock Name: %s" % self.stock_name)
        print("Final Money: %s" % final_money)
        print("Buy Days: %s" % self.buy_days)
        print("Sell Days: %s" % self.sell_days)

        return self.moneys


def run(buy_conditions, sell_conditions, stocks):
    all_ticker_values = []
    for ticker in stocks:
        sim = Simulation(ticker, 10000, buy_conditions, sell_conditions)
        values = sim.simulation()
        all_ticker_values.append(values)

    return [sum(x) for x in zip(*all_ticker_values)]

# df = pd.DataFrame([sum(x) for x in zip(*all_ticker_values)])
# plt.plot(df)
# plt.show()
