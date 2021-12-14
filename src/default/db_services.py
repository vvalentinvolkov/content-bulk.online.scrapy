import logging
from typing import Union, Type

import mongoengine
from mongoengine import ValidationError, NotUniqueError, FieldDoesNotExist, ConnectionFailure
from scrapy.exceptions import CloseSpider, DropItem

from .models import MyDocument


def get_all_scalar(doc: Type[MyDocument], *fields) -> list:
    """Возвращает поля fields от всех объектов типа doc"""
    return list(doc.objects.scalar(*fields))


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



