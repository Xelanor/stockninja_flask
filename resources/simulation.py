from flask import Response, request
from database.models import Simulation, User
from flask_restful import Resource
from datetime import datetime, timedelta
import json
from mongoengine.errors import DoesNotExist
from pprint import pprint

from .utils.ninja_simulator import run


class SimulationResultApi(Resource):
    def post(self):
        body = request.get_json()
        buy_conditions = body['buy']
        sell_conditions = body['sell']
        period = body["period"]

        stocks = []
        if buy_conditions['stock_type'] == "Yükselenler":
            stocks = ["TUPRS.IS", "CCOLA.IS",
                      "MGROS.IS", "ANACM.IS", "TRKCM.IS"]
        elif buy_conditions['stock_type'] == "Düşenler":
            stocks = ["KARSN.IS", "KCHOL.IS", "SISE.IS",
                      "TKFEN.IS", "TRGYO.IS", "TRKCM.IS", "TSKB.IS"]
        elif buy_conditions['stock_type'] == "Özel":
            for key, value in buy_conditions['stocks'].items():
                if value == True:
                    stocks.append(key)

        # print(buy_conditions)
        # print(sell_conditions)

        values, buyable_tickers = run(
            buy_conditions, sell_conditions, stocks, period)

        return {'values': values, 'buyable': buyable_tickers}, 200


class SimulationSaveApi(Resource):
    def post(self):
        body = request.get_json()
        buy_conditions = body['buy']
        sell_conditions = body['sell']
        user_id = body['user']

        User.objects.get(id=user_id).update(set__simulation={"buy": buy_conditions, "sell": sell_conditions})

        return {'token': str("Done")}, 200


class AddSimulationApi(Resource):
    def post(self):
        body = request.get_json()

        simulation = Simulation(**body)
        simulation.save()

        return {'token': str("Done")}, 200
