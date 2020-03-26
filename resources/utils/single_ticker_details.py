import requests
from datetime import datetime, timedelta
import json
from statistics import mean
from xml.etree import ElementTree
from .utils import *


class StockDetails:
    def __init__(self, userId, stockName, data_scope):
        self.userId = userId
        self.stockName = stockName
        self.data_scope = data_scope
        self.non_stocks = ["XU100.IS", "GC=F"]

    def combine_data_target(self):
        daily_data = self.daily_data
        stock_target = self.stock_target
        special_data = self.special_data

        stock_details = {
            "name": self.stockName,
            "date": epoch_to_date(daily_data["regularMarketTime"]),
            "price": daily_data["regularMarketPrice"],
            "shortName": daily_data["shortName"],
            "open": daily_data["regularMarketOpen"],
            "dayLow": daily_data["regularMarketDayLow"],
            "volume": daily_data["regularMarketVolume"],
            "dayHigh": daily_data["regularMarketDayHigh"],
            "50avg": daily_data["fiftyDayAverage"],
            "50avgChange": daily_data["fiftyDayAverageChange"],
            "50avgChangePerc": daily_data["fiftyDayAverageChangePercent"],
            "200avg": daily_data["twoHundredDayAverage"],
            "200avgChange": daily_data["twoHundredDayAverageChange"],
            "200avgChangePerc": daily_data["twoHundredDayAverageChangePercent"],
            "dayRange": daily_data["regularMarketDayRange"],
            "prevClose": daily_data["regularMarketPreviousClose"],
            "52wLow": daily_data["fiftyTwoWeekLow"],
            "52wHigh": daily_data["fiftyTwoWeekHigh"],
            "sellTarget": stock_target['sellTarget'] if 'sellTarget' in stock_target else 0,
            "buyTarget": stock_target['buyTarget'] if 'buyTarget' in stock_target else 0,
            "prevSellTarget": stock_target['prevSellTarget'] if 'prevSellTarget' in stock_target else 0,
            "prevBuyTarget": stock_target['prevBuyTarget'] if 'prevBuyTarget' in stock_target else 0,
            "stateBuy": stock_target['stateBuy'] if 'stateBuy' in stock_target else False,
            "stateSell": stock_target['stateSell'] if 'stateSell' in stock_target else False,
            "intraday": self.intraday_values,
            "rsi": self.rsi_values,
            "env": self.env_values,
            "ninja_index": self.ninja_values,
            "ninja_index_s": self.ninja_values_s,
            "triple_index": self.triple_index_values,
            "closes": self.historic_data,
            "williams": self.williams_values,
            "aroon": self.aroon_values,
            # "news": self.all_news,
            "fk": special_data['fk'] if 'fk' in special_data else 0,
            "pd_dd": special_data['pd_dd'] if 'pd_dd' in special_data else 0,
        }

        return stock_details

    def start(self):
        """
        Main entry point to get stock details
        Fetch the targets, get daily data, combine these two
        Get historic data for stock or non-stock
        """
        userId = self.userId
        stockName = self.stockName
        data_scope = self.data_scope

        self.stock_target = get_single_stock_target(userId, stockName)
        self.daily_data = get_current_tickers_data(stockName)[0]
        self.special_data = get_single_stock_special_data(stockName)
        self.intraday_values = get_stock_intraday_data(stockName)

        if self.stockName in self.non_stocks:
            self.historic_data = get_non_stock_historic_data(
                stockName, data_scope)
            self.rsi_values = []
        else:
            self.historic_data = get_stock_historic_data(
                stockName, data_scope)
            self.rsi_values = calculate_rsi_index(
                self.historic_data, data_scope)

        # self.all_news = get_stock_news(stockName)
        self.env_values = calculate_env_index(
            self.historic_data, data_scope)
        self.ninja_values = calculate_ninja_index(
            self.historic_data, data_scope)
        self.ninja_values_s = calculate_ninja_index_s(
            self.historic_data, data_scope)
        self.triple_index_values = calculate_triple_index(
            self.historic_data, data_scope)
        self.williams_values = calculate_williams_index(
            self.historic_data, data_scope)
        self.aroon_values = calculate_williams_index(
            self.historic_data, data_scope)
        self.stock_details = self.combine_data_target()

        return self.stock_details


def single_ticker_details(user, name):
    details = StockDetails(user, name, 90)

    stock_details = details.start()

    return stock_details
