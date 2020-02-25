from flask import Flask
from database.db import initialize_db
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.routes import initialize_routes
from resources.errors import errors

app = Flask(__name__)
app.config.from_envvar('ENV_FILE_LOCATION')
api = Api(app)
api = Api(app, errors=errors)
jwt = JWTManager(app)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb+srv://Xelanor:Xelanor01@stockninja-nd7xb.mongodb.net/stockninja'
}

initialize_db(app)
initialize_routes(api)

app.run(debug=True)
