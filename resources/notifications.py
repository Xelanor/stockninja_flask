from flask import Response, request
from database.models import Notification
from flask_restful import Resource
from datetime import datetime, timedelta
import json
from mongoengine.errors import DoesNotExist


class GetNotificationsApi(Resource):
    def post(self):
        body = request.get_json()

        Notifications = Notification.objects(
            receiver=body['receiver'], createdAt__gte=datetime.now() - timedelta(days=15)).order_by('-createdAt').to_json()

        return Response(Notifications, mimetype="application/json", status=200)


class AddNotificationItemApi(Resource):
    def post(self):
        body = request.get_json()

        notification = Notification(**body)
        notification.save()

        return {'token': str("Done")}, 200


class NotificationViewedApi(Resource):
    def post(self):
        body = request.get_json()

        Notification.objects.get(id=body['id']).update(set__viewed=True)

        return {'token': str("Done")}, 200


class DeleteNotificationApi(Resource):
    def post(self):
        body = request.get_json()

        Notification.objects.get(id=body['id']).delete()

        return {'token': str("Done")}, 200
