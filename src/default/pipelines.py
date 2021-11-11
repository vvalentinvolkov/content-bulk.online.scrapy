from mongoengine import connect, ValidationError, NotUniqueError
from pymongo.errors import ConnectionFailure, WriteError, DuplicateKeyError
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
            print('Not valid item: ', e, item.get['url'][:50])
            raise DropItem
        except (NotUniqueError, DuplicateKeyError):
            print('Not unique url')
            raise CloseSpider
        return item
