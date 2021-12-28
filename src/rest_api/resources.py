import logging

import flask
from flask_restful import Resource, reqparse,  abort

from src.services import db_services
from src.services.models import ZenArticle, ZenFeed
from src.services.query_set_converter import ConvertibleQuerySet

logger = logging.getLogger(__name__)

MODEL_CLASSES = {
    'zen_articles': ZenArticle,
    'zen_feeds': ZenFeed,
}


class BulkResource(Resource):

    # TODO: Убрать _id поле из выдачи бд
    MAX_LIMIT = 20

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('fields', location='args')
        self.parser.add_argument('limit', location='args', type=int)
        self.parser.add_argument('page', location='args', type=int)
        self.parser.add_argument('sort', location='args')
        self.parser.add_argument('filters', location='args')

    def get(self, document):
        model_class = MODEL_CLASSES.get(document)
        if not model_class:
            return abort(404, msg=f'There is no {document}')
        else:
            args_ = self.parser.parse_args()
            query_set = db_services.get_query_set(document=model_class, **args_)
            res = flask.Response(response=query_set.to_json(), status=200)
            res.content_type = 'application/json; charset=utf-8'
            return res
