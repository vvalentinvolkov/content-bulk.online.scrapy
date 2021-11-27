import logging
from typing import Union

import mongoengine
from mongoengine import ValidationError, NotUniqueError, FieldDoesNotExist, ConnectionFailure, Document
from scrapy.exceptions import CloseSpider, DropItem

from .items import MyDocument


def db_connect(db, host, port):
    """Подключение к MongoDb через mongoengine - при ConnectionFailure подымает CloseSpider"""
    try:
        client = mongoengine.connect(db=db, host=host, port=port)
        client.admin.command('ping')
        logging.info(f"Connect to {db} database")
    except ConnectionFailure:
        logging.error(f'MongoDb is not available')
        raise CloseSpider


def db_disconnect():
    logging.info(f'Mongoengine - disconnect(alias=default)')
    mongoengine.disconnect()


def db_save(item: Union[dict, MyDocument], document_class: type = None):
    """Сохраняет документ и все вложенные документы в бд
    Если item экземпляр Document - сохраняет его
    Если item - dict, требуется document_class для содания экземпляра перед сохранением"""
    try:
        if isinstance(item, MyDocument):
            item.mtm_cascade_save()
        elif document_class:
            document_class(**item).mtm_cascade_save()
        else:
            logging.error('db_save(...) need item: Document or document_class: type(Document)')
    except ConnectionFailure:
        logging.error('MongoDb is not available - closing the spider')
        raise CloseSpider
    except ValidationError:
        logging.warning('Not valid item')
        raise DropItem
    except NotUniqueError:
        logging.warning('NotUniqueError')
        raise DropItem
    except FieldDoesNotExist:
        logging.error('Item with extra values')
        raise DropItem

