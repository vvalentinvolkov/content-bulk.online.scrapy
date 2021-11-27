import pytest
import scrapy
import requests
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider

from src.default.items import ZenFeed
from src.default.spiders.zen_spider import ZenSpider

# process = CrawlerProcess()
#
# process.crawl(ZenSpider)
# process.start()     # the script will block here until the crawling is finished


def test_get_feeds_from_settings():
    """тест: получение видов из settings"""
    spider = ZenSpider()
    spider.settings = dict(ZEN_FEEDS_TO_PARSE='feed1 feed2 feed3')

    assert spider.get_feeds() == ['feed1', 'feed2', 'feed3']


def test_get_feeds_from_db(connect_to_mock_mongo):
    """тест: получение видов из db"""
    spider = ZenSpider()
    spider.settings = dict()
    ZenFeed(feed='feed1').save()
    ZenFeed(feed='feed2').save()
    ZenFeed(feed='feed3').save()

    assert spider.get_feeds() == ['feed1', 'feed2', 'feed3']


def test_get_empty_feeds(connect_to_mock_mongo):
    """тест: пустой список фидов"""
    spider = ZenSpider()
    spider.settings = dict()
    with pytest.raises(CloseSpider):
        spider.get_feeds()


def test_parse():
    """тест функции ZenSpider.parse на наличие в ответе соотвествующих значений в словаре cb_kwargs
        и ссылки для cb"""
    spider = ZenSpider()
    response = scrapy.http.TextResponse(
        url='https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&clid=300&interest_name=наука',
        body=requests.get('https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&clid=300&interest_name=наука').text,
        encoding='utf_8')
    for request in spider.parse(response):
        assert request.url
        assert request.cb_kwargs['feed_subscribers'] is not None
        assert request.cb_kwargs['title'] is not None
        assert request.cb_kwargs['link'] is not None
        assert request.cb_kwargs['public_date'] is not None
        assert request.cb_kwargs['time_public_to_parse'] is not None


def test_parse_channel():
    """тест функции ZenSpider.parse_channel на получение в ответе соотвествующих значений в словаре cb_kwargs
        и ссылки для cb"""
    spider = ZenSpider()
    response = scrapy.http.TextResponse(
        url='https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&lang=en'
            '&_csrf=298da2f6b3cd7f67dfae54e52942cce36205bf79-1637948673787-0-8725673611634847234%3A0'
            '&clid=300&channel_name=adstella',
        body=requests.get(
            'https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&lang=en'
            '&_csrf=298da2f6b3cd7f67dfae54e52942cce36205bf79-1637948673787-0-8725673611634847234%3A0'
            '&clid=300&channel_name=adstella').text,
        encoding='utf_8')

    request = spider.parse_channel(response, link='https://zen.yandex.ru/media/'
                                                 'adstella/7-planet-pohojih-na-zemliu-611262e8ccb50c2963f547a4')
    assert request.url == 'https://zen.yandex.ru/api/comments/top-comments?withUser=true&retryNum=0&' \
                          'manualRetry=false&commentId=0&withProfile=true&publisherId=607dbfe0a7a0b86de23291dc&' \
                          'documentId=native%3A611262e8ccb50c2963f547a4&commentCount=100'
    assert request.cb_kwargs['subscribers'] is not None
    assert request.cb_kwargs['audience'] is not None


def test_parse_top_comments():
    """тест функции ZenSpider.parse_top_comments на получение в ответе соотвествующих значений в словаре cb_kwargs
        и ссылки для cb"""
    spider = ZenSpider()
    response = scrapy.http.TextResponse(
        url='https://zen.yandex.ru/api/comments/top-comments?withUser=true&retryNum=0&'
            'manualRetry=false&commentId=0&withProfile=true&publisherId=607dbfe0a7a0b86de23291dc&'
            'documentId=native:611262e8ccb50c2963f547a4&commentCount=100',
        body=requests.get(
            'https://zen.yandex.ru/api/comments/top-comments?withUser=true&retryNum=0&'
            'manualRetry=false&commentId=0&withProfile=true&publisherId=607dbfe0a7a0b86de23291dc&'
            'documentId=native:611262e8ccb50c2963f547a4&commentCount=100').text,
        encoding='utf_8')
    request = spider.parse_top_comments(response, link='https://zen.yandex.ru/media/'
                                                       'adstella/7-planet-pohojih-na-zemliu-611262e8ccb50c2963f547a4')

    assert request.cb_kwargs['likes'] is not None
    assert request.cb_kwargs['comments'] is not None
    assert len(request.cb_kwargs['interests']) <= 10


def test_parse_article():
    spider = ZenSpider()
    response = scrapy.http.HtmlResponse(
        url='https://zen.yandex.ru/media/adstella/7-planet-pohojih-na-zemliu-611262e8ccb50c2963f547a4',
        body=requests.get('https://zen.yandex.ru/media/adstella/'
                          '7-planet-pohojih-na-zemliu-611262e8ccb50c2963f547a4').text,
        encoding='utf-8')
    res = spider.parse_article(response)
    assert res['visitors'] is not None
    assert res['reads'] is not None
    assert res['read_time'] is not None
    assert res['length'] is not None
    assert res['num_images'] is not None
