import asyncio
import logging
from collections import Iterable
from typing import Optional

import pymongo
from pymongo.collection import Collection

logger = logging.getLogger(__name__)


async def find_list(app: web.Application, collection_name: str, **kwargs):
    collection = app['db'][collection_name]
    return await _get_cursor(collection, **kwargs).to_list()


def _get_cursor(
        collection: Collection,
        fields: Optional[list[str]] = None,
        limit: Optional[str] = None,
        page: Optional[int] = 0,
        sort_field: Optional[str] = None,
        sort_ascending: Optional[bool] = False,
        filters: Optional[list[dict]] = None,
        filter_or: Optional[bool] = True) -> AsyncIOMotorCursor:
    """Возвращает курсор бд. Параметры для "Where" - cursor_expr передаются как словарь,
    остальные - cursor_params распоковываются

        :filter: словарь - ключи/поле"""

    cursor_expr = {}
    cursor_params = {}

    if limit:
        cursor_params['skip'] = page*limit
        cursor_params['limit'] = limit
    if fields:
        cursor_params['projection'] = fields
    if sort_field:
        if sort_ascending:
            cursor_params['sort'] = (sort_field, pymongo.ASCENDING)
        else:
            cursor_params['sort'] = (sort_field, pymongo.ASCENDING)
    for f in filters:
        if filter_or:
            cursor_expr[f.get('field')] = '{$in : {%s}}' % one_filed_filter
    if interests:
        cursor_expr['interests'] = '{$elemMatch: {feed_name: {$in : {%s}}}}' % interests

    try:
        return collection.find(cursor_expr, **cursor_params)
    # FIXME: как обработать исключение - отдать ответ с ошибкой
    except KeyError:
        logger.error(f'There is no collection {collection} in database!')