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
        print(buy_conditions)

        values = run(buy_conditions)

        return {'values': values}, 200


class AddSimulationApi(Resource):
    def post(self):
        body = request.get_json()

        simulation = Simulation(**body)
        simulation.save()

        return {'token': str("Done")}, 200
