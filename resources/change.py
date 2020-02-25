from flask import Response, request
from database.models import Change
from flask_restful import Resource
from datetime import datetime, timedelta
import json
from mongoengine.errors import DoesNotExist


class GetChangesApi(Resource):
    def get(self):
        body = request.get_json()
        Changes = Change.objects().order_by('-updatedAt')[:66].to_json()

        return Response(Changes, mimetype="application/json", status=200)


class AddChangeItemApi(Resource):
    def post(self):
        body = request.get_json()

        date = body['date']
        increasing = body['increasing']
        decreasing = body['decreasing']
        same = body['same']
        bist = body['bist']

        Change.objects(date=date).modify(set__date=date, set__increasing=increasing, set__decreasing=decreasing,
                                         set__same=same, set__bist=bist, set__updatedAt=datetime.now, upsert=True, new=True)

        return {'token': str("Done")}, 200
