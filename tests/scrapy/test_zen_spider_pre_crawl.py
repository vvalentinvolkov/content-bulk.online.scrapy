import pytest
from scrapy.exceptions import CloseSpider

from src.services.models import ZenFeed


def test_get_feeds_from_settings(zen_spider):
    """тест: получение видов из settings"""
    zen_spider.settings = dict(ZEN_FEEDS_TO_PARSE='feed1 feed2 feed3')

    assert zen_spider.get_feeds_names() == ['feed1', 'feed2', 'feed3']


def test_get_feeds_from_db(connect_to_mock_mongo, zen_spider):
    """тест: получение видов из db"""
    zen_spider.settings = dict()
    ZenFeed(feed_name='feed1').save()
    ZenFeed(feed_name='feed2').save()
    ZenFeed(feed_name='feed3').save()

    assert zen_spider.get_feeds_names() == ['feed1', 'feed2', 'feed3']


def test_get_empty_feeds(connect_to_mock_mongo, zen_spider):
    """тест: пустой список фидов"""
    zen_spider.settings = dict()
    with pytest.raises(CloseSpider):
        zen_spider.get_feeds_names()


def test_start_request(zen_spider):
    """тест функции ZenSpider.parse на наличие в ответе соотвествующих значений в словаре cb_kwargs
        и ссылки для cb"""
    zen_spider.feeds_names = ['feed1', 'feed2', 'feed3']
    zen_spider.parse_cycles = 2
    requests = list(zen_spider.start_requests())
    assert requests[0].cb_kwargs['feed_name'] == 'feed1'
    assert requests[1].cb_kwargs['feed_name'] == 'feed2'
    assert requests[2].cb_kwargs['feed_name'] == 'feed3'
    assert requests[0].url == requests[3].url
    assert requests[1].url == requests[4].url
    assert requests[2].url == requests[5].url

