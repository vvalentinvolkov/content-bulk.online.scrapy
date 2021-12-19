import logging
from typing import Optional, Iterable, Type
from mongoengine import QuerySet, Q, Document, InvalidQueryError
from mongoengine.queryset.transform import MATCH_OPERATORS

logger = logging.getLogger(__name__)

MAX_LIMIT = 20


def get_query_set(
        document: Optional[Type[Document]] = None,
        fields: Optional[Iterable[str]] = (),
        limit: Optional[int] = 1,
        page: Optional[int] = 0,
        sort_field: Optional[str] = None,
        filters: Optional[dict] = None) -> Optional[QuerySet]:
    """Возвращает queryset. По умолчанию возвращает первый документ

        :fields: возвращаемые поля
        :limit: колличество возвращаемых документов
        :page: колличество пропущеных документов по limit штук
        :sort_field: поле сортировки
        :filters: пары значений - поле__фильтр: значение для фильтра

        Сортировка и фильтрация происходит по списку полей fields, а не по всем полям"""

    # Выбираем из данных только существующие у модели поля. Если fields пустой - берем все поля
    fields = set(fields) & set(document._fields.keys()) if fields else set(document._fields.keys())

    limit = 1 if not limit else min(limit, MAX_LIMIT)
    page = 0 if not page else page
    slice_ = slice(page * limit, page * limit + limit)

    if sort_field:
        field_, direct_ = sort_field.split('__')
        if field_ in fields:
            if direct_ == 'a':
                sort_field = '+' + field_
            elif direct_ == 'd':
                sort_field = '-' + field_
            else:
                sort_field = None
        else:
            sort_field = None

    # Убираем пары с неуказаными полеми или с операторами не из MATCH_OPERATORS
    qc = Q()
    if filters:
        for field_filter, value in filters.items():
            if '__' in field_filter:
                field_, filter_ = field_filter.split('__')
                if field_ in fields and filter_ in MATCH_OPERATORS:
                    qc = qc & Q(**{field_filter: value})

    try:
        return document.objects(qc).only(*fields).order_by(sort_field)[slice_]
    except (InvalidQueryError, LookupError):
        return None
