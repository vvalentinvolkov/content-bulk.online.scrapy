import logging
from typing import Union, Type

import mongoengine
from mongoengine import Document


def mongo_connect(db: str, host: str, port: int):
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
