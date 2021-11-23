from mongoengine import connect, ValidationError, NotUniqueError
from pymongo.errors import ConnectionFailure, WriteError, DuplicateKeyError
from scrapy.exceptions import CloseSpider, DropItem
import logging

from . import db_services


class MongoPipeline:
    """Сохранение элементов в базу даных mongoDB"""

    def process_item(self, item: dict, spider):
        """Вызывается для каждого item"""
        db_services.db_save(item_class=spider.ITEM_CLASS, item=item)
        return item
