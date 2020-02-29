from flask import Response, request
from database.models import Transaction
from flask_restful import Resource
from datetime import datetime, timedelta
import json
from mongoengine.errors import DoesNotExist

from .utils.investment_screen_calculator import investment_screen_data


class GetTransactionsApi(Resource):
    def post(self):
        body = request.get_json()

        Transactions = Transaction.objects(
            user=body['user']).order_by('-updatedAt')
        investment_data = investment_screen_data(Transactions)
        if len(investment_data["stock_values"]) == 0:
            return Response(json.dumps([]), mimetype="application/json", status=200)

        return Response(json.dumps(investment_data), mimetype="application/json", status=200)


class AddTransactionItemApi(Resource):
    def post(self):
        body = request.get_json()

        transaction = Transaction(**body, informCount=0)
        transaction.save()

        return {'token': str("Done")}, 200


class DeleteTransactionItemApi(Resource):
    def post(self):
        body = request.get_json()

        Transaction.objects.get(id=body['id']).delete()

        return {'token': str("Done")}, 200


class SetInformTransactionItemApi(Resource):
    def post(self):
        body = request.get_json()

        Transaction.objects.get(id=body['id']).update(
            set__informCount=body['informCount'])

        return {'token': str("Done")}, 200
