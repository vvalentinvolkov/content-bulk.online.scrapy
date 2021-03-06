import logging
from typing import Union, Type, Optional

import mongoengine
from mongoengine import Document, InvalidQueryError, Q
from mongoengine.queryset.transform import MATCH_OPERATORS

from src.services.query_set_converter import ConvertibleQuerySet


def db_connect(db: str, host: str, port: int):
    db = mongoengine.connect(db=db, host=host, port=port)
    db.admin.command('ping')


def mongo_mock_connect():
    db = mongoengine.connect('mongoenginetest', host='mongomock://localhost')
    db.admin.command('ping')


# TODO: Зачем это?
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
        fields: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = 0,
        sort: Optional[str] = None,
        filters: Optional[str] = None) -> Optional[ConvertibleQuerySet]:
    """Возвращает ConvertibleQuerySet с lazy загрузкой.

        :fields: возвращаемые поля
        :limit: колличество возвращаемых документов
        :page: колличество пропущеных документов по limit штук
        :sort: поле сортировки
        :filters: 3 параметра - поле__фильтр__значение

        Сортировка и фильтрация происходит по списку полей fields, а не по всем полям"""

    # Выбираем из данных только существующие у модели поля. Если fields пустой - берем все поля
    # QuerySet будет держать fields в QuerySet._loaded_fields.fields
    if fields:
        fields = set(fields.split(';')) & set(document._fields.keys())
    else:
        fields = set(document._fields.keys())
        fields.remove('id')

    if not limit:
        slice_ = slice(None, None)
    elif not page:
        slice_ = slice(0, limit)
    else:
        slice_ = slice(page * limit, page * limit + limit)

    if sort and '__' in sort:
        field_, direct_ = sort.split('__')
        if field_ in fields:
            if direct_ == 'a':
                sort = '+' + field_
            elif direct_ == 'd':
                sort = '-' + field_
            else:
                sort = None
        else:
            sort = None

    # Убираем пары с неуказаными полеми или с операторами не из MATCH_OPERATORS
    qc = Q()
    if filters:
        for field_filt_value in filters.split(';'):
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
        return document.objects(qc).fields(id=0).only(*fields).order_by(sort)[slice_]
    except (InvalidQueryError, LookupError) as e:
        logging.error(f'Db service: {e}')
        return None


def get_aggr_res(
        document: Optional[Type[Document]] = None,
        fields: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = 0,
        sort: Optional[str] = None,
        filters: Optional[str] = None,
        qs: Optional[ConvertibleQuerySet] = None,
        aggr_funcs: Optional[str] = None,
        aggr_field: Optional[str] = None) -> Optional[dict]:
    """Получает ConvertibleQuerySet и возвращает результат функций агрегации funcs"""

    if not qs:
        qs = get_query_set(document=document,
                           fields=fields,
                           limit=limit,
                           page=page,
                           sort=sort,
                           filters=filters)
    if aggr_funcs:
        aggr_funcs_ = aggr_funcs.split(';')
    else:
        aggr_funcs_ = ['count', 'sum', 'avg']
    res = {}
    if 'count' in aggr_funcs_:
        res['count'] = _get_count(qs=qs)
    if 'sum' in aggr_funcs_:
        res['sum'] = _get_sum(qs=qs, aggr_field=aggr_field)
    if 'avg' in aggr_funcs_:
        res['avg'] = _get_avg(qs=qs, aggr_field=aggr_field)
    return res


def _get_count(qs: ConvertibleQuerySet, with_slice: bool = False):
    """Возвращает число элементов QuerySet"""
    return qs.count(with_limit_and_skip=with_slice)


def _get_sum(qs: ConvertibleQuerySet, aggr_field: Optional[str]):
    """Возвращает сумму значений в поле aggr_field в QuerySet"""
    if aggr_field:
        try:
            return qs.sum(field=aggr_field)
        except mongoengine.errors.LookUpError:
            return 0
    return 0


def _get_avg(qs: ConvertibleQuerySet, aggr_field: Optional[str]):
    """Возвращает среднее из значений в поле aggr_field в QuerySet"""
    if aggr_field:
        try:
            res = qs.average(field=aggr_field)
        except mongoengine.errors.LookUpError:
            return 0
        if res:
            return res
    return 0
