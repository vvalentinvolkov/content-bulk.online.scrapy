import pytest
from mongoengine import connect, disconnect

from src.default.spiders.zen_spider import ZenSpider


@pytest.fixture()
def zen_spider():
    return ZenSpider()


@pytest.fixture()
def connect_to_mock_mongo():
    yield connect('mongo_test', host='mongomock://localhost')
    disconnect()