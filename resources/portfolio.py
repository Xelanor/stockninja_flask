from flask import Response, request
from database.models import Portfolio
from flask_restful import Resource
from datetime import datetime, timedelta
import json
from mongoengine.errors import DoesNotExist

from .utils.my_ticker_details import my_ticker_details


class GetPortfoliosApi(Resource):
    def post(self):
        body = request.get_json()
        Portfolios = Portfolio.objects(user=body['user'])
        if len(Portfolios) == 0:
            return Response(json.dumps([]), mimetype="application/json", status=200)
        portfolio = my_ticker_details(Portfolios)
        return Response(json.dumps(portfolio), mimetype="application/json", status=200)


class GetSinglePortfolioApi(Resource):
    def post(self):
        body = request.get_json()

        name = body['name']
        user = body['user']

        try:
            SingleItem = Portfolio.objects.get(user=user, name=name).to_json()
        except DoesNotExist:
            SingleItem = json.dumps(None)

        return Response(SingleItem, mimetype="application/json", status=200)


class AddPortfolioItemApi(Resource):
    def post(self):
        body = request.get_json()

        name = body['name']
        user = body['user']

        portfolio = Portfolio.objects(
            name=name, user=user).modify(set__name=name, set__user=user, set__buyTarget=0, set__sellTarget=0, upsert=True, new=True)

        return {'token': str("Done")}, 200


class SetPortfolioBuyTarget(Resource):
    def post(self):
        body = request.get_json()

        name = body['name']
        user = body['user']
        target = body['target']

        portfolio = Portfolio.objects(
            name=name, user=user).modify(set__name=name, set__user=user, set__buyTarget=target, upsert=True, new=True)

        return {'token': str("Done")}, 200


class SetPortfolioSellTarget(Resource):
    def post(self):
        body = request.get_json()

        name = body['name']
        user = body['user']
        target = body['target']

        portfolio = Portfolio.objects(
            name=name, user=user).modify(set__name=name, set__user=user, set__sellTarget=target, upsert=True, new=True)

        return {'token': str("Done")}, 200


class PortfolioDeleteApi(Resource):
    def post(self):
        body = request.get_json()

        name = body['name']
        user = body['user']

        portfolio = Portfolio.objects.get(name=name, user=user).delete()
        return {'token': str("Done")}, 200
