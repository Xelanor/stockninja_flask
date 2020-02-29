from .utils.utils import telegram_bot_sendtext
from flask import Response, request
from database.models import User
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
import random
import json

from resources.errors import SchemaValidationError, MovieAlreadyExistsError, InternalServerError, UpdatingMovieError, DeletingMovieError, MovieNotExistsError
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError


class SignupApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            user = None
            try:
                user = User.objects.get(email=body.get('email'))
            except:
                pass

            if user is None:
                user = User(**body)
                user.save()

            notifId = body['notifId']

            passCode = random.randint(1000, 9999)
            user.update(notifId=notifId,
                        loginPassCode=passCode,
                        loginPassCodeExpires=datetime.utcnow() + timedelta(minutes=15))

            telegram_bot_sendtext(str(passCode))

            return {'result': str(passCode)}, 200

        except NotUniqueError:
            raise MovieAlreadyExistsError
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except Exception as e:
            raise InternalServerError


class InitialLoginApi(Resource):
    def post(self):
        body = request.get_json()
        user = User.objects.get(email=body.get('email'))
        if not user:
            return {'error': 'Email is invalid'}, 401

        passCode = random.randint(1000, 9999)
        user.update(loginPassCode=passCode,
                    loginPassCodeExpires=datetime.utcnow() + timedelta(minutes=15))

        telegram_bot_sendtext(str(passCode))

        return {'token': "success"}, 200


class PassLoginApi(Resource):
    def post(self, code):
        body = request.get_json()
        user = User.objects.get(email=body.get('email'))
        user_pass_code = user.loginPassCode
        user_pass_code_expires = user.loginPassCodeExpires

        if user_pass_code_expires < datetime.utcnow() or int(code) != user_pass_code:
            return {'error': 'Pass code is invalid or expired'}, 401

        expires = timedelta(days=999999)
        payload = json.dumps(
            {"id": str(user.id), "email": user.email, "role": user.role})
        access_token = create_access_token(
            identity=payload, expires_delta=expires)

        return {'token': access_token}, 200
