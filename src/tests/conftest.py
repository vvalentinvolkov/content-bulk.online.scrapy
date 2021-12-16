import asyncio

import pytest
from mongoengine import connect, disconnect
from motor.motor_asyncio import AsyncIOMotorClient

from src.default.spiders.zen_spider import ZenSpider

@pytest.fixture()
def zen_spider():
    spider = ZenSpider()
    spider.custom_settings.pop('JOBDIR', None)
    return spider


@pytest.fixture()
def connect_to_mock_mongo():
    yield connect('mongo_test', host='mongomock://localhost')
    disconnect()
