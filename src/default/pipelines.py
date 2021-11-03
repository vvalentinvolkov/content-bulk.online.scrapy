from collections import OrderedDict

import pymongo
from itemadapter import ItemAdapter
from pymongo.errors import ConnectionFailure, WriteError
from scrapy.exceptions import CloseSpider
from mongo_services import MongoDb


class MongoPipeline:
    """Сохранение элементов в базу даных mongoDB"""

    def process_item(self, item, spider):
        try:
            MongoDb().get_collection_for_item(item_class=type(item)).insert_one(ItemAdapter(item).asdict())
        except ConnectionFailure:
            print('MongoDb is not available - closing the spider')
            raise CloseSpider
        except WriteError as e:
            print('Not valid item: ', e)
        return item
