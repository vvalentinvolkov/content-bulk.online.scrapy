from collections import OrderedDict

import pymongo
from itemadapter import ItemAdapter
from pymongo.errors import ConnectionFailure, WriteError


class MongoPipeline:
    collection_name = 'scrapy_articles'

    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=f"mongodb://{crawler.settings.get('MONGO_URL')}/",
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url, serverSelectionTimeoutMS=5000)
        try:
            self.client.admin.command('ping')
        except ConnectionFailure:
            print("Server not available")
            print("Closing the spider")
            spider.close()
        else:
            self.db = self.client['scrapy_mongo']
            print("<----- Get db ----->")

    def close_spider(self, spider):
        self.client.close()

    scheme = {
        "$jsonSchema": {
            "required": [
                "source",
                "title",
            ],
            "properties": {
                "source": {
                    "bsonType": "string",
                    "enum": ["zen"],
                    "description": "must be a string and is required"
                },
                "title": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                }
            }
        }
    }

    def process_item(self, item, spider):
        print(item)
        if self.collection_name not in self.db.list_collection_names():
            self.db.create_collection(self.collection_name)
            cmd = OrderedDict([('collMod', self.collection_name),
                               ('validator', self.scheme)])
            self.db.command(cmd)
        try:
            self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        except WriteError as e:
            print('not valid', e)
        print("<----- Get collection ----->")
        return item
