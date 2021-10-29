import pymongo
import pytest

from pymongo.errors import ConnectionFailure, InvalidName


# TODO: PyTest туда переезжаем
class TestMongo:
    """Тесты подключения к бд"""
    MONGO_URI = 'mongodb://localhost:27017/'
    MONGO_DB = 'scrapy_mongo'

    def test_connection(self):
        """тест подключения к монго"""
        client = pymongo.MongoClient(self.MONGO_URI, serverSelectionTimeoutMS=5000)
        try:
            client.admin.command('ping')
            print('ping')
            db = client['somedb']
            collection = db['test-collection']
            db.create_collection()
            collection.insert_one({'x': 1})
        except ConnectionFailure:
            print("Server not available")
        except InvalidName:
            print('InvalidName')
        finally:
            client.close()
