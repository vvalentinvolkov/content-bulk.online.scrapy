from mongoengine import connect, ValidationError, NotUniqueError
from pymongo.errors import ConnectionFailure, WriteError, DuplicateKeyError
from scrapy import Spider
from scrapy.exceptions import CloseSpider, DropItem
import logging

from . import db_services


class MongoPipeline:
    """Сохранение элементов в базу даных mongoDB"""

    logger = logging.getLogger('MongoPipeline')

    def process_item(self, item: dict, spider: Spider):
        """Вызывается для каждого item"""
        if spider.settings.get('ITEM_CLASS'):
            db_services.db_save(document_class=spider.settings.get('ITEM_CLASS'), item=item)
            return item
        self.logger.error('spider.settings["ITEM_CLASS"] is None')
        raise CloseSpider
