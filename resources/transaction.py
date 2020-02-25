from flask import Response, request
from database.models import Transaction
from flask_restful import Resource
from datetime import datetime, timedelta
import json
from mongoengine.errors import DoesNotExist


class GetTransactionsApi(Resource):
    def post(self):
        body = request.get_json()

        Transactions = Transaction.objects(
            user=body['user']).order_by('-updatedAt').to_json()

        return Response(Transactions, mimetype="application/json", status=200)


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
