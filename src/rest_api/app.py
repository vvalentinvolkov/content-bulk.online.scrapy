import os

from flask import Flask
from flask_restful import Api

from src.rest_api.resources.bulk import Bulk

#Database
DB_HOST = os.environ.get('DB_HOST', default='localhost')
DB_PORT = int(os.environ.get('DB_PORT', default=27017))
DB_NAME = os.environ.get('DB_NAME', default='default_articles')


app = Flask(__name__)
api = Api(app)

api.add_resource(Bulk, '/bulk')

if __name__ == '__main__':
    app.run(debug=True)