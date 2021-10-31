from collections import OrderedDict

import pymongo
from itemadapter import ItemAdapter
from pymongo.errors import ConnectionFailure, WriteError
from scrapy.exceptions import CloseSpider


class MongoPipeline:
    """Сохранение элементов в базу даных mongoDB"""

    def process_item(self, item, spider):
        try:
            spider.collection.insert_one(ItemAdapter(item).asdict())
        except WriteError as e:
            print('Not valid item: ', e)
        return item
