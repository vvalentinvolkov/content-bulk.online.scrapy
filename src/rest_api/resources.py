from typing import Iterable, Optional

from flask import request
from flask_restful import Resource

from src.db_services.models import ZenArticle
from src.rest_api import db_services


class ZenArticlesResources(Resource):

    MODEL_CLASS = ZenArticle

    def get(self):
        get_args = request.args.to_dict()
        query_set = db_services.get_query_set(
            document=self.MODEL_CLASS,
            fields=self._get_fields(get_args.pop('fields', None)),
            limit=self._get_limit(get_args.pop('limit', None)),
            page=self._get_page(get_args.pop('page', None)),
            sort_field=self._get_sort_field(get_args.pop('sort_field', None)),
            filters=self._get_filters(get_args)  # Собирает оставшиеся поля - лучше присваивать в коцне
        )

        return query_set.to_json()

    @staticmethod
    def _get_fields(arg: Optional[str]) -> Optional[Iterable[str]]:
        if arg:
            return arg.split(' ')

    @staticmethod
    def _get_limit(arg: Optional[str]) -> Optional[int]:
        if arg:
            try:
                return int(arg)
            except ValueError:
                return None

    @staticmethod
    def _get_page(arg: Optional[str]) -> Optional[int]:
        if arg:
            try:
                return int(arg)
            except ValueError:
                return None

    @staticmethod
    def _get_sort_field(arg: Optional[str]) -> Optional[str]:
        if arg:
            return arg

    @staticmethod
    def _get_filters(filters: dict):
        return filters
