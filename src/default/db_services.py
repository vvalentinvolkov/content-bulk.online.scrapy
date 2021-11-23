import logging

import mongoengine
from mongoengine import ValidationError, NotUniqueError
from pymongo.errors import ConnectionFailure, WriteError, DuplicateKeyError
from scrapy.exceptions import CloseSpider, DropItem


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
    mongoengine.disconnect()


def db_save(document_class: type, item: dict):
    try:
        document_class(**item).save()
    except ConnectionFailure:
        logging.error('MongoDb is not available - closing the spider')
        raise CloseSpider
    except (WriteError, ValidationError) as e:
        logging.warning(f'Not valid item: {e}\n{item.get("url")[:50]}')
        raise DropItem
    except (NotUniqueError, DuplicateKeyError):
        logging.warning('Not unique url')
        raise DropItem
