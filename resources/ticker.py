from flask import Response, request
from database.models import Ticker
from flask_restful import Resource
from datetime import datetime, timedelta
import json
from mongoengine.errors import DoesNotExist

from .utils.all_ticker_details import fetch_all_stocks
from .utils.all_currency_details import fetch_all_currencies
from .utils.single_ticker_details import single_ticker_details


class GetTickersApi(Resource):
    def get(self):
        Tickers = Ticker.objects().to_json()

        return Response(Tickers, mimetype="application/json", status=200)


class GetAllTickerDetailsApi(Resource):
    def get(self):
        allTickers = fetch_all_stocks()

        return Response(json.dumps(allTickers), mimetype="application/json", status=200)


class GetAllCurrencyDetailsApi(Resource):
    def get(self):
        allCurrencies = fetch_all_currencies()

        return Response(json.dumps(allCurrencies), mimetype="application/json", status=200)


class GetSingleTickerApi(Resource):
    def post(self):
        body = request.get_json()

        name = body['name']

        try:
            SingleItem = Ticker.objects.get(name=name).to_json()
        except DoesNotExist:
            SingleItem = json.dumps(None)

        return Response(SingleItem, mimetype="application/json", status=200)


class GetSingleTickerDetailsApi(Resource):
    def post(self):
        body = request.get_json()

        user = body['user']
        name = body['name']

        SingleItem = single_ticker_details(user, name)

        return Response(json.dumps(SingleItem), mimetype="application/json", status=200)


class AddTickerItemApi(Resource):
    def post(self):
        body = request.get_json()

        name = body['name']
        rsi = body['rsi']
        ninja = body['ninja']
        ninja_s = body['ninja_s']

        Ticker.objects(name=name).modify(set__name=name, set__rsi=rsi, set__ninja=ninja,
                                         set__ninja_s=ninja_s, set__updatedAt=datetime.now, upsert=True, new=True)

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

        rsi_upper = body['rsi']['upper']
        rsi_lower = body['rsi']['lower']
        ninja_upper = body['ninja']['upper'] / 100
        ninja_lower = body['ninja']['lower'] / 100
        ninja_s_upper = body['ninja_s']['upper'] / 100
        ninja_s_lower = body['ninja_s']['lower'] / 100
        pd_dd_upper = body['pd_dd']['upper']
        pd_dd_lower = body['pd_dd']['lower']
        fk_upper = body['fk']['upper']
        fk_lower = body['fk']['lower']

        Tickers = Ticker.objects(rsi__lte=rsi_upper, rsi__gte=rsi_lower, ninja__lte=ninja_upper, ninja__gte=ninja_lower, ninja_s__lte=ninja_s_upper, ninja_s__gte=ninja_s_lower,
                                 pd_dd__lte=pd_dd_upper, pd_dd__gte=pd_dd_lower, fk__lte=fk_upper, fk__gte=fk_lower).to_json()

        return Response(Tickers, mimetype="application/json", status=200)
