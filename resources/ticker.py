from flask import Response, request
from database.models import Ticker
from flask_restful import Resource
from datetime import datetime, timedelta
import json
from mongoengine.errors import DoesNotExist


class GetTickersApi(Resource):
    def get(self):
        body = request.get_json()
        Tickers = Ticker.objects().to_json()

        return Response(Tickers, mimetype="application/json", status=200)


class GetSingleTickerApi(Resource):
    def post(self):
        body = request.get_json()

        name = body['name']

        SingleItem = Ticker.objects.get(user=user).to_json()

        return Response(SingleItem, mimetype="application/json", status=200)


class AddTickerItemApi(Resource):
    def post(self):
        body = request.get_json()

        name = body['name']
        rsi = body['rsi']
        ninja = body['ninja']

        Ticker.objects(name=name).modify(set__name=name, set__rsi=rsi,
                                         set__ninja=ninja, set__updatedAt=datetime.now, upsert=True, new=True)

        return {'token': str("Done")}, 200


class AddTickerScrapDataApi(Resource):
    def post(self):
        body = request.get_json()

        name = body['name']
        fk = body['fk']
        pd_dd = body['pd_dd']

        Ticker.objects(name=name).modify(set__name=name, set__fk=fk,
                                         set__pd_dd=pd_dd, set__updatedAt=datetime.now, upsert=True, new=True)

        return {'token': str("Done")}, 200


class TickerSearchApi(Resource):
    def post(self):
        body = request.get_json()

        rsi = body['rsi']
        ninja = body['ninja']
        pd_dd = body['pd_dd']

        Tickers = Ticker.objects(
            rsi__lte=rsi, ninja__lte=ninja, pd_dd__lte=pd_dd).to_json()

        return Response(Tickers, mimetype="application/json", status=200)
