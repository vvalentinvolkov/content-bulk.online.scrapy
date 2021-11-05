from mongoengine import connect, ValidationError
from pymongo.errors import ConnectionFailure, WriteError
from scrapy.exceptions import CloseSpider, DropItem


class MongoPipeline:
    """Сохранение элементов в базу даных mongoDB"""

    def process_item(self, item, spider):
        try:
            spider.ITEM_CLASS(**item).save()
        except ConnectionFailure:
            print('MongoDb is not available - closing the spider')
            raise CloseSpider
        except (WriteError, ValidationError) as e:
            print('Not valid item: ', e)
            raise DropItem
        return item
