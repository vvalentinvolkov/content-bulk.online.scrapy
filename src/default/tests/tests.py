import pytest
from scrapy.crawler import CrawlerProcess

from src.default import settings
from src.default.spiders.zen_spider import ZenSpider

db = settings.DEFAULT_MONGO_DB_NAME
host = settings.MONGO_HOST
port = settings.MONGO_PORT


@pytest.fixture()
def mongo_setup(request):
    yield


def test_spider_connection_to_mongo():
    """тест: подключение/закрытие монго в пауке"""
    pass


def test_selenium_request_is_full_rendered():
    """тест полуение ответа через селениум с зарендереным jsом"""
    pass


def test_mongo_validation():
    """тест: монго проверяет данные при соранении"""
    pass


def test_itemloader_return_valid_item():
    """тест: itemloader возвращает валидные данные"""
    pass

