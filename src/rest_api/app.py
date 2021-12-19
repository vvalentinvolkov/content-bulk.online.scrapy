from flask import Flask
from flask_restful import Api

from src.rest_api import db
from src.rest_api.resources import ZenArticlesResources


def create_app() -> Flask:
    """Создает объект app Flask, получая конфиг из файла config.py
    и обновляя значения конфига из необязательных аргументов"""
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    return app


def create_api() -> Api:
    app = create_app()

    with app.app_context():
        db.init_db()

    api = Api(app)
    api.add_resource(ZenArticlesResources, '/bulk/zen_articles')

    return api

# if __name__ == '__main__':
#     app.run(debug=True)
