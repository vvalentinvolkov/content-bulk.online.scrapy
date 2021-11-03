from collections import OrderedDict
from pyclbr import Class

import pymongo

from .items import CommonArticleItem
from .settings import MONGO_URL, DEFAULT_MONGO_DB_NAME, DEFAULT_MONGO_COLLECTION_NAME


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MongoDb(metaclass=MetaSingleton):
    """Класс для работы с бд - содержит инст конекта"""
    _client = None

    @property
    def client(self):
        """Возвращает клиента монги. При неудачном конекте (через 5 сек) подымает ConnectionFailure"""
        if not self._client:
            self._client = pymongo.MongoClient(f"mongodb://{MONGO_URL}/", serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
        return self._client

    def close(self):
        self.client.close()

    @property
    def db(self):
        return self.get_db()

    def get_db(self, db_name: str = DEFAULT_MONGO_DB_NAME):
        return self.client[db_name]

    def get_collection_for_item(self, item_class: type):
        """Принимает класс, унаследованый от CommonArticleClass и возвращает коллекцию, указаную в классе.
        Если колекции нет - создает новую и устанавливает valid_scheme из класса."""
        assert issubclass(item_class, CommonArticleItem), f'{item_class} не наследует CommonArticleItem'
        if item_class.COLLECTION_NAME not in self.db.list_collection_names():
            self.db.create_collection(item_class.COLLECTION_NAME)
            cmd = OrderedDict([('collMod', item_class.COLLECTION_NAME),
                               ('validator', item_class.VALID_SCHEME)])
            self.db.command(cmd)
        return self.db[item_class.COLLECTION_NAME]
