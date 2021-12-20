from mongoengine import ValidationError, NotUniqueError, FieldDoesNotExist, Document
from pymongo.errors import ConnectionFailure
from scrapy.exceptions import CloseSpider, DropItem
import logging

from ..services import db_services


class MongoPipeline:
    """Сохранение элементов в базу даных mongoDB"""

    logger = logging.getLogger('MongoPipeline')

    def process_item(self, item: dict, spider):
        """Вызывается для каждого item"""
        document_class, values = next(iter(item.items()))
        if issubclass(document_class, Document):
            try:
                db_services.db_save(document_class=document_class, item=values)
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
        self.logger.error(f'load_item must return dict(<Document>: dict). Get {document_class}')
        raise CloseSpider
