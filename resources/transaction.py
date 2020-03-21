from flask import Response, request
from database.models import Transaction
from flask_restful import Resource
from datetime import datetime, timedelta
import json
from mongoengine.errors import DoesNotExist

from .utils.investment_screen_calculator import investment_screen_data


class GetAllTransactionsApi(Resource):
    def get(self):
        Transactions = Transaction.objects(informCount__lte=3).to_json()

        if len(Transactions) == 0:
            return Response(json.dumps([]), mimetype="application/json", status=200)

        return Response(Transactions, mimetype="application/json", status=200)


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


class SellTransactionItemApi(Resource):
    def post(self):
        body = request.get_json()

        transaction = Transaction(user=body['user'], name=body["name"], price=body["price"],
                                  amount=body["amount"], kind=body["kind"], profit=body["profit"], informCount=0)
        transaction.save()

        transaction = Transaction.objects.get(id=body['id'])
        transaction_amount = transaction.amount

        transaction.update(set__amount=transaction_amount - body['amount'])

        return {'token': str("Done")}, 200


class GetTracingTransactionsApi(Resource):
    def get(self):
        Transactions = Transaction.objects(traced__ne=True).to_json()

        if len(Transactions) == 0:
            return Response(json.dumps([]), mimetype="application/json", status=200)

        return Response(Transactions, mimetype="application/json", status=200)


class SetCurrentPriceTransactionItemApi(Resource):
    def post(self):
        body = request.get_json()

        Transaction.objects.get(id=body['id']).update(
            set__currentPrice=body['current_price'])

        return {'token': str("Done")}, 200


class SetTracedTransactionItemApi(Resource):
    def post(self):
        body = request.get_json()

        Transaction.objects.get(id=body['id']).update(set__traced=True)

        return {'token': str("Done")}, 200
