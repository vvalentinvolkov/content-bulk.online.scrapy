from mongoengine import ValidationError, NotUniqueError, FieldDoesNotExist
from pymongo.errors import ConnectionFailure
from scrapy import Spider
from scrapy.exceptions import CloseSpider, DropItem
import logging

from ..db_services import db_services


class MongoPipeline:
    """Сохранение элементов в базу даных mongoDB"""

    logger = logging.getLogger('MongoPipeline')

    def process_item(self, item: dict, spider: Spider):
        """Вызывается для каждого item"""
        if spider.settings.get('ITEM_CLASS'):
            try:
                db_services.db_save(document_class=spider.settings.get('ITEM_CLASS'), item=item)
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
            return item
        self.logger.error('spider.settings["ITEM_CLASS"] is None')
        raise CloseSpider
