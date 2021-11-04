from mongoengine import connect
from pymongo.errors import ConnectionFailure, WriteError
from scrapy.exceptions import CloseSpider, DropItem

from .items import ZenArticle


class MongoPipeline:
    """Сохранение элементов в базу даных mongoDB"""

    def process_item(self, item, spider):
        try:
            ZenArticle(**item).save()
        except ConnectionFailure:
            print('MongoDb is not available - closing the spider')
            raise CloseSpider
        except WriteError as e:
            print('Not valid item: ', e)
            raise DropItem
        return item
