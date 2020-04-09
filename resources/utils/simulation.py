import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
from pprint import pprint
import matplotlib.pyplot as plt
import json
from statistics import mean

from constants.tickers import valuable_tickers
from utils import epoch_to_date, calculate_williams_index, calculate_triple_index, calculate_aroon_index, calculate_ninja_index, calculate_rsi_index


class Simulation:
    def __init__(self, stock_name, money):
        self.today = ""
        self.sim_end = ""
        self.stock_name = stock_name
        self.money = money
        self.portfolio = {stock_name: 0}
        self.transaction_log = []
        self.sim_period = 1
        self.values = []

    def epoch_to_date(self, date, hour=3):
        """
        Convert timestamp to datetime
        """
        return (datetime.utcfromtimestamp(date) + timedelta(hours=hour)).strftime("%d-%m-%Y %H:%M")

    def get_prices_old(self):
        values = {"prices": [], "dates": []}
        QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/chart/{}?range=261d&interval={}d&indicators=quote&includeTimestamps=true"

        res = requests.get(QUERY_URL.format(self.stock_name, 1)).json()
        prices = res['chart']["result"][0]['indicators']["quote"][0]["close"]
        timestamps = res['chart']['result'][0]['timestamp']

        values['prices'] = prices

        for timestamp in timestamps:
            date = self.epoch_to_date(timestamp)
            values['dates'].append(date)

        self.today = values['dates'][0]
        self.sim_end = values['dates'][-1]

        return values

    def get_prices(self):
        values = {"prices": [], "dates": []}
        df = pd.read_csv("prices.csv", index_col="Date",
                         parse_dates=True)[self.stock_name]

        values['prices'] = df.tolist()
        timestamps = df.index.values.tolist()

        for timestamp in timestamps:
            date = self.epoch_to_date(int(str(timestamp)[:-9]))
            values['dates'].append(date)

        self.today = values['dates'][0]
        self.sim_end = values['dates'][-1]

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

    def sell(self, amount, price, info):
        self.money += amount * price
        self.portfolio[self.stock_name] -= amount
        self.transaction(amount, price, "sell", info)

    def calculate_average(self, historic_data, data_scope):
        first_data = historic_data[-1 * (data_scope + 21):]

        average_list = []

        for i in range(0, data_scope):
            try:
                average_list.append(round(mean(first_data[i:i+21]), 2))
            except Exception as ex:
                print(ex)
                pass

        return average_list

    def calculate_average_alternative(self, historic_data, data_scope):
        data = historic_data[-1 * (data_scope + 5):]
        result = []

        for i in range(0, data_scope):
            closes = data[i:i+6]
            first = closes[0]
            second = closes[1]
            yesterday = closes[-2]
            today = closes[-1]

            avg_first = ((yesterday - first) / first * 100)
            avg_second = ((today - second) / second * 100)

            result.append(avg_first + avg_second)

        return result
    
    def forecast_next(self, prices, averages, data_scope):
        xy = [x * y for x, y in zip(prices, averages)]
        x2 = [x * x for x in averages]

        a1 = sum(prices) / len(prices)
        a2 = sum(averages) / len(averages)
        a3 = sum(xy) * len(prices)
        a4 = sum(x2) * len(prices)
        a5 = sum(prices) * sum(averages)
        a6 = sum(prices) ** 2
        a7 = a3 - a5
        a8 = a4 - a6
        a9 = a7 / a8
        a10 = a2 - (a9 * a1)
        a11 = a10 + (a9 * (len(prices) + 1))

        return a11

    def simulation(self):

        # CONDITIONS
        rsi_max = 30
        rsi_min = 70
        ninja_max = -0.03
        ninja_min = 0.02
        buy_tracing_rate = 0.97
        sell_tracing_rate = 10
        buy_tracing_price = 0
        sell_tracing_price = 1000000
        arith_avg_period = 4
        avg_alternative_rate = -4
        # arith_avg_buy_rate = 0.01
        buy_days = []
        sell_days = []
        _prices = []
        _forecasts = []
        _arith = []
        values = self.get_prices()
        for i in range(len(values["prices"][30:])):
            self.today = values["dates"][i + 30]
            price = round(values["prices"][i + 30], 2)
            prev_price = round(values["prices"][i + 29], 2)
            prices_until_today = values["prices"][:(i + 31)]
            prices_until_tomorrow = values["prices"][:(i + 32)]

            current_money = self.money + \
                (price * self.portfolio[self.stock_name])
            self.values.append(current_money)

            ninja = calculate_ninja_index(prices_until_today, 14)
            rsi = calculate_rsi_index(prices_until_tomorrow, 3)
            williams = calculate_williams_index(prices_until_tomorrow, 3)
            triple = calculate_triple_index(
                prices_until_tomorrow, 3)["third_list"]
            aroon = calculate_aroon_index(prices_until_tomorrow, 3)
            arith_avg = self.calculate_average(prices_until_today, 11)
            avg_alternative = self.calculate_average_alternative(
                prices_until_today, 1)
            forecast = self.forecast_next(prices_until_today, arith_avg, 10)
            _forecasts.append(forecast)
            _prices.append(price)
            _arith.append(arith_avg[-1])
            
            if self.money <= 0 and price > buy_tracing_price:
                buy_tracing_price = price

            if self.money > 0 and price < sell_tracing_price:
                sell_tracing_price = price

            if self.money > 0:  # BUY
                # if ninja > ninja_max:
                #     continue

                # if price >= sell_tracing_price * sell_tracing_rate:
                #     continue

                # if aroon['upper'][-1] < 70:
                #     continue

                # if aroon['lower'][-1] > 30:
                #     continue

                # if avg_rate < 0:
                #     continue

                # if price < arith_avg[-1] * 0.98:
                #     continue

                # if arith_avg[-1] < arith_avg[-2]:
                #     continue

                # if price > arith_avg[-1] * 1.02:
                #     continue

                # if price <= sell_tracing_price:
                #     continue

                # if avg_alternative[-1] < avg_alternative_rate:
                #     continue

                # if forecast < arith_avg[-1]:
                #     continue

                # if ninja[-2] < -0.04:
                #     continue
                
                if price < prev_price:
                    continue

                if ninja[-1] < ninja[-2]:
                    continue

                if ninja[-2] > 0.01:
                    continue

                if -1 * (arith_avg[-1] - price) / arith_avg[-1] < -0.04:
                    continue

                if arith_avg[-1] < arith_avg[-5]:
                    continue

                today = arith_avg[-1]
                x_th_day = arith_avg[-1 * arith_avg_period]
                avg_rate = round((today - x_th_day) / x_th_day * 100, 2)
                buy_ninja = round(
                    (price - values["prices"][i + 29]) / values["prices"][i + 29] * 100, 2)

                buy_amount = self.money / price
                info = "ALIM NINJA: %s \nFIYAT: %s \nRSI: %s \nNINJA: %s \nWilliams: %s \n7-avg: %s \nAroon: %s \nAverage: %s" % (
                    str(buy_ninja), str(values["prices"][i + 29:i + 32]),  str(rsi), str([ninja[-2], ninja[-1]]), str(williams), str(triple), str(aroon), str([arith_avg[-2], arith_avg[-1]]))
                self.buy(buy_amount, price, info)

                buy_tracing_price = price

                buy_days.append(i+30)

            elif self.money <= 0:  # SELL

                if price > buy_tracing_price * buy_tracing_rate:
                    continue

                today = arith_avg[-1]
                x_th_day = arith_avg[-1 * arith_avg_period]
                avg_rate = round((today - x_th_day) / x_th_day * 100, 2)

                sell_amount = self.portfolio[self.stock_name]
                info = "Tracing: %s \nFIYAT: %s \nRSI: %s \nNINJA: %s \nWilliams: %s \n7-avg: %s \nAroon: %s \nAverage: %s" % (
                    str(buy_tracing_price),  str(values["prices"][i + 29:i + 32]),  str(rsi), str(ninja), str(williams), str(triple), str(aroon), str(arith_avg[-1]))
                self.sell(sell_amount, price, info)

                sell_tracing_price = 1000000

                sell_days.append(i+30)

        final_money = (self.money +
                       (price * self.portfolio[self.stock_name]))

        f.write("%s \n" % self.stock_name)
        f.write("%s \n" % str(self.money +
                              (price * self.portfolio[self.stock_name])))
        json_obj = json.dumps(self.transaction_log, indent=4)
        f.write(json_obj)
        f.write("\nToplam hareket sayisi: %s" % str(len(buy_days)))

        print("Stock Name: %s" % self.stock_name)
        print("Final Money: %s" % final_money)
        # pprint(self.transaction_log)
        print("Buy Days: %s" % buy_days)
        print("Sell DAys: %s " % sell_days)
        # df1 = pd.DataFrame(_prices)
        # df2 = pd.DataFrame(_forecasts)
        # df3 = pd.DataFrame(_arith)
        # plt.plot(df1, color='olive')
        # plt.plot(df2, color='blue')
        # plt.plot(df3, color='red')
        # plt.show()
        return self.values


f = open("stock.txt", "w")
all_values = []
for ticker in ["TUPRS.IS"]:
    sim = Simulation(ticker, 10000)
    values = sim.simulation()
    all_values.append(values)

f.close()
df = pd.DataFrame([sum(x) for x in zip(*all_values)])
plt.plot(df)
plt.savefig('figure.png')
plt.show()

# sim = Simulation("TUPRS.IS", 10000)
# values = sim.get_prices()
# prices = values["prices"]


# df = pd.DataFrame(avg)
# plt.plot(df)
# plt.savefig('average.png')
# plt.show()

# def get_prices_old(name):
#     values = {'prices': [], "dates": []}
#     QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/chart/{}?range=1y&interval=1d&indicators=quote&includeTimestamps=true"

#     res = requests.get(QUERY_URL.format(name)).json()
#     prices = res['chart']["result"][0]['indicators']["quote"][0]["close"]
#     timestamps = res['chart']['result'][0]['timestamp']

#     values['prices'] = prices

#     # for timestamp in timestamps:
#     #     date = epoch_to_date(timestamp)
#     #     values['dates'].append(date)

#     return values


# def calculate_average_alternative(historic_data, data_scope):
#     data = historic_data[-1 * (data_scope + 5):]
#     result = []

#     for i in range(0, data_scope):
#         closes = data[i:i+6]
#         first = closes[0]
#         second = closes[1]
#         yesterday = closes[-2]
#         today = closes[-1]

#         avg_first = ((yesterday - first) / first * 100)
#         avg_second = ((today - second) / second * 100)

#         result.append(avg_first + avg_second)

#     return result


# def dollar_stock():
#     stock_prices = get_prices_old("TUPRS.IS")
#     averages = calculate_average_alternative(
#         stock_prices['prices'], len(stock_prices['prices']) - 5)

#     pprint(stock_prices)
#     pprint(averages)

#     prices = stock_prices['prices'][5:]

#     df1 = pd.DataFrame(prices)
#     df2 = pd.DataFrame(averages)

#     fig, ax1 = plt.subplots()
#     ax2 = ax1.twinx()
#     ax1.plot(df1, 'g-')
#     ax2.plot(df2, 'b-')

#     plt.title("TUPRS.IS")
#     ax1.set_ylabel('FIYATLAR', color='g')
#     ax2.set_ylabel('ORTALAMALAR', color='b')

#     plt.show()


# dollar_stock()
