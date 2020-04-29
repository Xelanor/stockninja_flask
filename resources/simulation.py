from flask import Response, request
from database.models import Simulation
from flask_restful import Resource
from datetime import datetime, timedelta
import json
from mongoengine.errors import DoesNotExist

from .utils.ninja_simulator import run


class SimulationResultApi(Resource):
    def post(self):
        body = request.get_json()
        buy_conditions = body['buy']
        sell_conditions = body['sell']

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

        print(stocks)

        values = run(buy_conditions, sell_conditions, stocks)

        return {'values': values}, 200


class AddSimulationApi(Resource):
    def post(self):
        body = request.get_json()

        simulation = Simulation(**body)
        simulation.save()

        return {'token': str("Done")}, 200
