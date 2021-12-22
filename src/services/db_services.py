import logging
import os
from typing import Union, Type, Optional, Iterable

import mongoengine
from mongoengine import Document, QuerySet, InvalidQueryError, Q
from mongoengine.queryset.transform import MATCH_OPERATORS

MAX_LIMIT = 1000


def db_connect(db: str, host: str, port: int):
    db = mongoengine.connect(db=db, host=host, port=port)
    db.admin.command('ping')


def mongo_mock_connect():
    db = mongoengine.connect('mongoenginetest', host='mongomock://localhost')
    db.admin.command('ping')


def get_all_scalar(doc: Type[Document], *fields) -> list:
    """Возвращает поля fields от всех объектов типа doc"""
    return list(doc.objects.scalar(*fields))


def db_save(item: Union[dict, Document], document_class: type = None):
    """Сохраняет документ и все вложенные документы в бд
    Если item экземпляр Document - сохраняет его
    Если item - dict, требуется document_class для содания экземпляра перед сохранением"""
    if issubclass(type(item), Document):
        item.save()
    elif document_class:
        document_class(**item).save()
    else:
        logging.error('db_save(...) need item: Document or document_class: type(Document)')


def get_query_set(
        document: Optional[Type[Document]] = None,
        fields: Optional[Iterable[str]] = (),
        limit: Optional[int] = 1,
        page: Optional[int] = 0,
        sort_field: Optional[str] = None,
        filters: Optional[str] = None) -> Optional[QuerySet]:
    """Возвращает queryset. По умолчанию возвращает первый документ

        :fields: возвращаемые поля
        :limit: колличество возвращаемых документов
        :page: колличество пропущеных документов по limit штук
        :sort_field: поле сортировки
        :filters: 3 параметра - поле__фильтр__значение

        Сортировка и фильтрация происходит по списку полей fields, а не по всем полям"""

    # Выбираем из данных только существующие у модели поля. Если fields пустой - берем все поля
    fields = set(fields) & set(document._fields.keys()) if fields else set(document._fields.keys())

    limit = 1 if not limit else min(limit, MAX_LIMIT)
    page = 0 if not page else page
    slice_ = slice(page * limit, page * limit + limit)

    if sort_field and '__' in sort_field:
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
        for field_filt_value in filters.split(' '):
            try:
                field, filt, value = field_filt_value.split('__')
            except ValueError:
                continue
            try:
                value = int(value)
            except ValueError:
                pass
            if field in fields:
                if not filt:
                    qc = qc & Q(**{f'{field}': value})
                elif filt in MATCH_OPERATORS:
                    qc = qc & Q(**{f'{field}__{filt}': value})

    try:
        print('document - ' + str(document))
        print('qc - ' + str(qc))
        print('fields - ' + str(fields))
        print('sort_field - ' + str(sort_field))
        print('slice_ - ' + str(slice_))
        return document.objects(qc).only(*fields).order_by(sort_field)[slice_]
    except (InvalidQueryError, LookupError):
        print('some error')
        return None
