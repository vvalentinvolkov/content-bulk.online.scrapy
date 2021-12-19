import logging
from typing import Optional, Iterable, Type
from mongoengine import QuerySet, Q, Document, LookUpError

logger = logging.getLogger(__name__)

MAX_LIMIT = 20


def get_query_set(
        document: Type[Document],
        fields: Optional[Iterable[str]] = (),
        limit: Optional[int] = 1,
        page: Optional[int] = 0,
        sort_field: Optional[str] = None,
        filters: Optional[dict] = None) -> QuerySet:
    """Возвращает queryset. По умолчанию возвращает первый документ

        :fields: возвращаемые поля
        :limit: колличество возвращаемых документов
        :page: колличество пропущеных документов по limit штук
        :sort_field: поле сортировки
        :filters: пары значений - поле__фильтр: значение для фильтра"""

    limit = min(limit, MAX_LIMIT)
    start_pos = page * limit
    end_pos = page * limit + limit
    qc = Q()
    if filters:
        for field_filter, value in filters.items():
            qc = qc & Q(**{field_filter: value})
    return document.objects(qc).only(*fields).order_by(sort_field)[start_pos:end_pos]
