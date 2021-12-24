import scrapy
import requests

from src.services.models import ZenFeed, ZenArticle


def test_parse(zen_spider):
    """тест функции ZenSpider.parse на наличие в ответе соотвествующих значений в словаре cb_kwargs
        и ссылки для cb"""
    response = scrapy.http.TextResponse(
        url='https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&clid=300&interest_name=наука',
        body=requests.get('https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&clid=300&interest_name=наука').text,
        encoding='utf_8')
    for request in zen_spider.parse(response):
        assert request.url
        assert request.cb_kwargs['feed_subscribers'] is not None
        assert request.cb_kwargs['title'] is not None
        assert request.cb_kwargs['link'] is not None
        assert request.cb_kwargs['public_date'] is not None
        assert request.cb_kwargs['time_public_to_parse'] is not None


def test_parse_channel(zen_spider):
    """тест функции ZenSpider.parse_channel на получение в ответе соотвествующих значений в словаре cb_kwargs
        и ссылки для cb"""
    response = scrapy.http.TextResponse(
        url='https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&lang=en'
            '&_csrf=298da2f6b3cd7f67dfae54e52942cce36205bf79-1637948673787-0-8725673611634847234%3A0'
            '&clid=300&channel_name=adstella',
        body=requests.get(
            'https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&lang=en'
            '&_csrf=298da2f6b3cd7f67dfae54e52942cce36205bf79-1637948673787-0-8725673611634847234%3A0'
            '&clid=300&channel_name=adstella').text,
        encoding='utf_8')

    request = next(zen_spider.parse_channel(response, link='https://zen.yandex.ru/media/'
                                                 'adstella/7-planet-pohojih-na-zemliu-611262e8ccb50c2963f547a4'))
    assert request.url == 'https://zen.yandex.ru/api/comments/top-comments?withUser=true&retryNum=0&' \
                          'manualRetry=false&commentId=0&withProfile=true&publisherId=607dbfe0a7a0b86de23291dc&' \
                          'documentId=native%3A611262e8ccb50c2963f547a4&commentCount=100'
    assert request.cb_kwargs['subscribers'] is not None
    assert request.cb_kwargs['audience'] is not None


def test_parse_top_comments(zen_spider):
    """тест функции ZenSpider.parse_top_comments на получение в ответе соотвествующих значений в словаре cb_kwargs
        и ссылки для cb"""
    response = scrapy.http.TextResponse(
        url='https://zen.yandex.ru/api/comments/top-comments?withUser=true&retryNum=0&'
            'manualRetry=false&commentId=0&withProfile=true&publisherId=607dbfe0a7a0b86de23291dc&'
            'documentId=native:611262e8ccb50c2963f547a4&commentCount=100',
        body=requests.get(
            'https://zen.yandex.ru/api/comments/top-comments?withUser=true&retryNum=0&'
            'manualRetry=false&commentId=0&withProfile=true&publisherId=607dbfe0a7a0b86de23291dc&'
            'documentId=native:611262e8ccb50c2963f547a4&commentCount=100').text,
        encoding='utf_8')
    request = next(zen_spider.parse_top_comments(
        response,
        link='https://zen.yandex.ru/media/adstella/7-planet-pohojih-na-zemliu-611262e8ccb50c2963f547a4'))

    assert request.cb_kwargs['likes'] is not None
    assert request.cb_kwargs['comments'] is not None
    assert len(request.cb_kwargs['interests']) <= 10


def test_parse_article_and_load_item(zen_spider):
    response = scrapy.http.HtmlResponse(
        url='https://zen.yandex.ru/media/adstella/7-planet-pohojih-na-zemliu-611262e8ccb50c2963f547a4',
        body=requests.get('https://zen.yandex.ru/media/adstella/'
                          '7-planet-pohojih-na-zemliu-611262e8ccb50c2963f547a4').text,
        encoding='utf-8')
    gen = zen_spider.parse_article(response, feed_name='feed_name1', feed_subscribers=10, interests=['feed1', 'feed2'])
    items = [item for item in gen]
    feed = items[0][ZenFeed]
    assert feed['feed_name'] == 'feed_name1'
    assert feed['feed_subscribers'] == 10
    article = items[len(items)-1][ZenArticle]
    assert article['visitors'] is not None
    assert article['reads'] is not None
    assert article['read_time'] is not None
    assert article['length'] is not None
    assert article['num_images'] is not None
    assert article['interests'][0] == 'feed1'
    assert article['interests'][1] == 'feed2'
    for i in range(1, len(items)-1):
        feed_from_interests = items[i][ZenFeed]
        assert feed_from_interests['feed_name'] == article['interests'][i-1]
