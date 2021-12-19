from typing import Iterable, Optional

from flask import request
from flask_restful import Resource, reqparse

from src.services import db_services
from src.services.models import ZenArticle, ZenFeed

MODEL_CLASSES = {
    'zen_articles': ZenArticle,
    'zen_feeds': ZenFeed,
}


class BulkResources(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('fields', location='args', default=None)
        self.parser.add_argument('limit', location='args', type=int, default=None)
        self.parser.add_argument('page', location='args', type=int, default=None)
        self.parser.add_argument('sort_field', location='args', default=None)
        self.parser.add_argument('filters', location='args', default=None)

    def get(self, document):
        model_class = MODEL_CLASSES.get(document)
        if not model_class:
            pass
            # FIXME: ошибка 404
        else:
            args_ = self.parser.parse_args()
            query_set = db_services.get_query_set(document=model_class, **args_)
            return query_set.to_json()
