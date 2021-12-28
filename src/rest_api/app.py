import sys
sys.path.insert(0, '/home/bilkinegra/my_project/content-bulk.online.scrapy')

from flask import Flask
from flask_restful import Api

from . import db
from .resources import BulkResource, AggregationResource


def create_app(**kwargs) -> Flask:
    """Создает объект app Flask, получая конфиг из файла config.py
    и обновляя значения конфига из необязательных аргументов"""
    app_ = Flask(__name__)
    app_.config.from_pyfile('config.py')
    app_.config.update(kwargs)
    return app_


app = create_app()

with app.app_context():
    db.init_db()

api = Api(app)
api.add_resource(BulkResource, '/<string:document>')
api.add_resource(AggregationResource, '/aggr/<string:document>')

