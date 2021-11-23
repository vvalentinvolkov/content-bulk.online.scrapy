from datetime import datetime
import re
from urllib.parse import unquote

import logging
import mongoengine
from scrapy import http, Spider
from pymongo.errors import ConnectionFailure
from scrapy.exceptions import CloseSpider
from scrapy.http import TextResponse
from collections import Counter

from .. import css_handler, db_services
from ..items import ZenArticle


class ZenSpider(Spider):
    """Spider для статей из ЯндексДзена"""

    name = 'ZenSpider'
    ITEM_CLASS = ZenArticle  # Класс, унаследованый от Mongoengine.Document, для сохранения MongoPipeline
    allowed_domains = ['zen.yandex.ru']
    default_zen_feed = 'https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&clid=300'
    feed_interests = [
        'путешествия',
        'история',
        'здоровье',
        'недвижимость',
        'политика',
        'наука',
        'ссср',
        'юмор',
        'садидача',
        'рецепты',
        'кухня',
        'искусство',
        'политика',
        'наука',
        'здоровье',
        'экономика'
    ]

    # JOBDIR необходима для проверки на дипликаты уже паршеных ссылок (из бд)
    # custom_settings = {
    #     'JOBDIR': 'default/crawls/ZenSpider',    # Директория, для хранения состояние паука (FP спаршеных ссылок)
    # }

    @staticmethod
    def mongoengine_connect(db, host, port):
        """Подключение к MongoDb через mongoengine - при ConnectionFailure подымает CloseSpider"""
        try:
            client = mongoengine.connect(db=db, host=host, port=port)
            client.admin.command('ping')
            logging.info(f"Connect to {db} database")
        except ConnectionFailure:
            logging.error(f'MongoDb is not available')
            raise CloseSpider

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        host = crawler.settings.get('DB_HOST')
        port = crawler.settings.get('DB_PORT')
        db = crawler.settings.get('DEFAULT_DB_NAME')
        db_services.db_connect(db, host, port)
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def close(self, reason):
        # Разрыв соединение когда паук закрывается
        logging.info(f'Mongoengine - disconnect(alias=default)')
        db_services.db_disconnect()

    def start_requests(self):
        kwargs = {'feed': 'main'}
        yield http.Request(url=self.default_zen_feed, callback=self.parse, dont_filter=True, cb_kwargs=kwargs)
        yield http.Request(url=self.default_zen_feed, callback=self.parse, dont_filter=True, cb_kwargs=kwargs)
        yield http.Request(url=self.default_zen_feed, callback=self.parse, dont_filter=True, cb_kwargs=kwargs)
        for interest in self.feed_interests:
            url = self.default_zen_feed + '&interest_name=' + interest
            kwargs = {'feed': interest}
            yield http.Request(url=url, callback=self.parse, dont_filter=True, cb_kwargs=kwargs)

    def parse(self, response: TextResponse, **kwargs):
        """Получение фида - в случае ошибки или не получения какой либо информации
        все последующие запросы возвращают None.
        Проверяем если item это видео или источник верефицирован или публикация старше 6 месяцев -> следующий item
        Все собираемые данных добавляются в kwargs и передаются в cb"""
        feed_json = response.json()
        try:
            kwargs['feed_subscribers'] = feed_json['channel']['source']['subscribers']
        except KeyError as e:
            logging.warning(f'Cant get feed_subscribers from feed_json - {e}\nSet interest as "main"')
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
                    yield http.Request(url=item['channel_link'], callback=self.parse_channel, dont_filter=True,
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
        return http.Request(url=top_comments_link, callback=self.parse_top_comments,
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
                kwargs['interests'] = [interest for interest, _ in counted_interests.most_common(5)]
            else:
                return None
        except KeyError as e:
            logging.warning(f'Cant get from top_comments_json - {e}')
            return None
        return http.Request(url=kwargs['link'], callback=self.parse_article,
                            cb_kwargs=kwargs)

    def parse_article(self, response, **kwargs):
        """Получение данных самой статьи - селекторы содержат функции-обработчики в css_handler.
        Отдает в pipeline kwargs, которые содержит все данные полученые в пред запросах"""
        kwargs['visitors'] = css_handler.get_visitors(response)
        kwargs['reads'] = css_handler.get_reads(response)
        kwargs['read_time'] = css_handler.get_read_time(response)
        kwargs['length'] = css_handler.get_length(response)
        kwargs['num_images'] = css_handler.get_num_images(response)
        # print(kwargs)
        return kwargs
