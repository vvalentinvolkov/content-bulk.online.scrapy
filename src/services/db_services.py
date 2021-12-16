import logging
from typing import Union, Type

import mongoengine

from src.default.models import MyDocument


def mongo_connect(db: str, host: str, port: int):
    client = mongoengine.connect(db=db, host=host, port=port)
    client.admin.command('ping')


def get_all_scalar(doc: Type[MyDocument], *fields) -> list:
    """Возвращает поля fields от всех объектов типа doc"""
    return list(doc.objects.scalar(*fields))


def db_save(item: Union[dict, MyDocument], document_class: type = None):
    """Сохраняет документ и все вложенные документы в бд
    Если item экземпляр Document - сохраняет его
    Если item - dict, требуется document_class для содания экземпляра перед сохранением"""
    if isinstance(item, MyDocument):
        item.mtm_cascade_save()
    elif document_class:
        document_class(**item).mtm_cascade_save()
    else:
        logging.error('db_save(...) need item: Document or document_class: type(Document)')
