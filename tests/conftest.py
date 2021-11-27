import pytest
from mongoengine import connect, disconnect

from src.default.spiders.zen_spider import ZenSpider


@pytest.fixture()
def zen_spider():
    return ZenSpider()

# TODO: как вернуть знчение в yield?
@pytest.fixture()
def connect_to_mock_mongo():
    connect('mongo_test', host='mongomock://localhost')
    yield
    disconnect()