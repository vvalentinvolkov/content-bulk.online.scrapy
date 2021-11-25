from datetime import datetime
import re

import logging
from scrapy import http, Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import TextResponse
from collections import Counter

from .. import re_handler, db_services
from ..items import ZenArticle, ZenFeed


class ZenSpider(Spider):
    """Spider для статей из ЯндексДзена"""

    name = 'ZenSpider'
    ITEM_CLASS = ZenArticle  # Класс, унаследованый от Mongoengine.Document, для сохранения MongoPipeline
    allowed_domains = ['zen.yandex.ru']
    default_feed = 'https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&clid=300'
    feeds = {}
    # headers = {
    #         # 'Accept': 'application/json;text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #         'Accept-Encoding': 'gzip, deflate, br',
    #         'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
    #         'Cache-Control': 'no-cache',
    #         'Connection': 'keep-alive',
    #         'DNT': '1',
    #         'Host': 'zen.yandex.ru',
    #         'Pragma': 'no-cache',
    #         'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    #         'sec-ch-ua-mobile': '?0',
    #         'Sec-Fetch-Dest': 'document',
    #         'Sec-Fetch-Mode': 'navigate',
    #         'Sec-Fetch-Site': 'none',
    #         'Sec-Fetch-User': '?1',
    #         'Upgrade-Insecure-Requests': '1',
    #         'User-Agent':' Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    #     }

    custom_settings = {
        'JOBDIR': 'default/crawls/ZenSpider',   # Директория, для хранения состояние паука (FP спаршеных ссылок)
        'DB_NAME': 'zen_articles',
        'PARSE_CYCLES': 1,  # Колличество проходов по списку фидов (каждый фид содержит около 30 ссылок)
    }

    @classmethod
    def connect_to_mongo(cls, crawler):
        host = crawler.settings.get('DB_HOST')
        port = crawler.settings.get('DB_PORT')
        db = crawler.settings.get('DB_NAME')
        db_services.db_connect(db, host, port)

    @classmethod
    def get_feeds(cls, crawler):
        """Получает список фидов для парсинга из settings['ZEN_FEEDS_TO_PARSE']
        или (если setting не задан) выгружает список из бд

        Не вызывает Spider.close() т.к. еще не создан паук - закрываем подключение к бд самостоятельно"""
        feed_list_path = crawler.settings.get('ZEN_FEEDS_TO_PARSE')
        if feed_list_path:
            cls.feeds = feed_list_path.split(' ')
        else:
            cls.feeds = list(ZenFeed.objects.scalar('feed'))
        if len(cls.feeds) == 0:
            logging.error('An empty feeds set. Add some ZenFeed objects in a database or'
                          ' set some feeds split by a space via setting["ZEN_FEEDS_TO_PARSE"]')
            db_services.db_disconnect()
            raise CloseSpider

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        cls.parse_cycles = crawler.settings.get('PARSE_CYCLES')
        cls.connect_to_mongo(crawler)
        cls.get_feeds(crawler)
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def close(self, reason):
        # Разрыв соединение когда паук закрывается
        db_services.db_disconnect()

    def start_requests(self):
        for _ in range(self.parse_cycles):
            for interest in self.feeds:
                url = self.default_feed + '&interest_name=' + interest
                kwargs = {'feed': interest}
                yield http.Request(url=url,
                                   callback=self.parse,
                                   dont_filter=True,
                                   cb_kwargs=kwargs)

    def parse(self, response: TextResponse, **kwargs):
        """Получение фида - в случае ошибки или не получения какой либо информации
        все последующие запросы возвращают None.
        Проверяем если item это видео или источник верефицирован или публикация старше 6 месяцев -> следующий item
        Все собираемые данных добавляются в kwargs и передаются в cb

        Spiders Contracts
        """
        feed_json = response.json()
        try:
            kwargs['feed_subscribers'] = feed_json['channel']['source']['subscribers']
        except KeyError:
            logging.warning(f'Cant get feed_subscribers from feed_json')
        if 'items' in feed_json:
            for item in feed_json['items']:
                try:
                    is_verified = item['source'].get('is_verified')
                    is_video = item.get('video') is not None
                    public_date = int(item['publication_date'])
                    time_public_to_parse = int(datetime.utcnow().timestamp()) - public_date
                    if not is_verified and not is_video and time_public_to_parse < 16070400:  # 16070400 сек ~ 6 мес.
                        kwargs['title'] = item['title']
                        kwargs['link'] = item['share_link']
                        kwargs['public_date'] = public_date
                        kwargs['time_public_to_parse'] = time_public_to_parse
                    else:
                        continue
                except KeyError as e:
                    logging.warning(f'Cant get from feed_json["items"] - {e}')
                else:
                    yield http.Request(url=item['channel_link'],
                                       callback=self.parse_channel,
                                       dont_filter=True,
                                       cb_kwargs=kwargs)
        else:
            return None

    def parse_channel(self, response: TextResponse, **kwargs):
        """Получение данных по каналу и формирование ссылки на динамические данные статьи (top_comments)"""
        try:
            document_id = re.match(r'.*-(\w*)$', kwargs['link'])[1]
        except TypeError:
            logging.info(f'Not zen article link - {kwargs["link"]}')
            return None
        channel_json = response.json()
        try:
            source = channel_json['channel']['source']
            kwargs['subscribers'] = source['subscribers']
            kwargs['audience'] = source.get('audience')
            publisher_id = source['publisher_id']
            # Ссылка на динамические данные статьи (top_comments)
            top_comments_link = 'https://zen.yandex.ru/api/comments/top-comments?' \
                                'withUser=true&retryNum=0&manualRetry=false&commentId=0&withProfile=true' \
                                f'&publisher_id={publisher_id}' \
                                f'&document_id=native%3A{document_id}' \
                                '&commentCount=100'
        except KeyError as e:
            logging.warning(f'Cant get from channel_json - {e}')
            return None
        return http.Request(url=top_comments_link,
                            callback=self.parse_top_comments,
                            cb_kwargs=kwargs)

    def parse_top_comments(self, response: TextResponse, **kwargs):
        """Получение динамических данных статьи и интересов из комментариев"""
        top_comments_json = response.json()
        try:
            meta = top_comments_json['meta']
            is_visible_comments = meta.get('visibleComments') == 'visible'
            if is_visible_comments:
                kwargs['likes'] = top_comments_json['publicationLikeCount']
                kwargs['comments'] = meta['commentsCount'] + meta['answersCount']
                counted_interests = Counter()
                counted_interests.update((interest['title'] for profile in top_comments_json['profiles']
                                          for interest in profile['interests']))
                kwargs['interests'] = [interest for interest, _ in counted_interests.most_common(10)]
            else:
                return None
        except KeyError as e:
            logging.warning(f'Cant get from top_comments_json - {e}')
            return None
        return http.Request(url=kwargs['link'],
                            callback=self.parse_article,
                            cb_kwargs=kwargs)

    def parse_article(self, response, **kwargs):
        """Получение данных самой статьи - селекторы содержат функции-обработчики в css_handler.
        Отдает в pipeline kwargs, которые содержит все данные полученые в пред запросах"""

        kwargs['visitors'] = re_handler.get_visitors(
            response.css('.article-stats-view__tip div:nth-child(1) span::text').get())
        kwargs['reads'] = re_handler.get_reads(
            response.css('.article-stats-view__tip div:nth-child(2) span::text').get())
        kwargs['read_time'] = re_handler.get_read_time(
            response.css('.article-stats-view__tip div:nth-child(3) span::text').get())
        kwargs['length'] = re_handler.get_length(
            response.css('.article-render[itemprop = "articleBody"] > p *::text').getall())
        kwargs['num_images'] = re_handler.get_num_images(
            response.css('.article-render[itemprop = "articleBody"] .article-image-item__image').getall())
        # print(kwargs)
        return self.load_item(kwargs)

    @staticmethod
    def load_item(item: dict) -> ZenArticle:
        """Возвращает вместо dict готовый ZenArticle объект для передачи в MongoPipeline"""
        # Создаем объект ZenFeed из значений полученых пауком и записываем в item['zen_feed']
        # и удаляем item['feed'], item['feed_subscribers']
        item['feed'] = ZenFeed(feed=item.pop('feed'),
                               feed_subscribers=item.pop('feed_subscribers', None))
        # Заменяем списко str - kwargs['interests'] на список объектов ZenFeed и сохраняем каждый
        item['interests'] = [ZenFeed(feed=interest) for interest in item['interests']]
        return ZenArticle(**item)
