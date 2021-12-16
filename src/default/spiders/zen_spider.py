from datetime import datetime
import re

from scrapy import http, Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import TextResponse
from collections import Counter


from .. import re_handler, db
from ...services import db_services
from ..models import ZenArticle, ZenFeed


class ZenSpider(Spider):
    """Spider для статей из ЯндексДзена"""

    name = 'ZenSpider'
    allowed_domains = ['zen.yandex.ru']
    default_feed = 'https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&clid=300'
    feeds_names = []

    custom_settings = {
        'JOBDIR': 'default/crawls/ZenSpider',   # Директория, для хранения состояние паука (FP спаршеных ссылок)
        'DB_NAME': 'zen_articles',
        'PARSE_CYCLES': 1,  # Колличество проходов по списку фидов (каждый фид содержит около 30 ссылок)
        'ITEM_CLASS': ZenArticle  # Класс, унаследованый от Mongoengine.Document, для сохранения MongoPipeline
    }

    def get_feeds_names(self):
        """Получает список фидов для парсинга из бд"""
        if self.settings.get('ZEN_FEEDS_TO_PARSE'):
            _feeds = self.settings.get('ZEN_FEEDS_TO_PARSE').split(' ')
        else:
            _feeds = db_services.get_all_scalar(ZenFeed, 'feed_name')
        if len(_feeds) == 0:
            self.logger.error('An empty feeds set. Add some ZenFeed objects in a database or'
                          ' set some feeds split by a space via setting["ZEN_FEEDS_TO_PARSE"]')
            raise CloseSpider
        return _feeds

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        cls.parse_cycles = crawler.settings.get('PARSE_CYCLES')
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        db.setup_db(crawler)
        return spider

    def start_requests(self):
        for _ in range(self.parse_cycles):
            if len(self.feeds_names) == 0:
                self.feeds_names = self.get_feeds_names()
            for feed_name in self.feeds_names:
                url = self.default_feed + '&interest_name=' + feed_name
                kwargs = {'feed_name': feed_name}
                yield http.Request(url=url,
                                   callback=self.parse,
                                   dont_filter=True,
                                   cb_kwargs=kwargs)

    def parse(self, response: TextResponse, **kwargs):
        """Получение фида - в случае ошибки или не получения какой либо информации
        все последующие запросы возвращают None.
        Проверяем если item это видео или источник верефицирован или публикация старше 6 месяцев -> следующий item
        Все собираемые данных добавляются в kwargs и передаются в cb"""

        feed_json = response.json()
        try:
            kwargs['feed_subscribers'] = feed_json['channel']['source']['subscribers']
        except KeyError:
            self.logger.warning(f'Cant get feed_subscribers from feed_json')
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

                        channel_link = item['channel_link']
                    else:
                        continue
                except KeyError as e:
                    self.logger.warning(f'Cant get from feed_json["items"] - {e}')
                else:
                    yield http.Request(url=channel_link,
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
            self.logger.info(f'Not zen article link - {kwargs["link"]}')
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
                                f'&publisherId={publisher_id}' \
                                f'&documentId=native%3A{document_id}' \
                                '&commentCount=100'
        except KeyError as e:
            self.logger.warning(f'Cant get from channel_json - {e}')
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
            self.logger.warning(f'Cant get from top_comments_json - {e}')
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
        return self.load_item(kwargs)

    @staticmethod
    def load_item(item: dict) -> dict:
        """Возвращает валидный словарь для pipelines"""
        # Создаем объект ZenFeed, из значений полученых пауком, и записываем в item['zen_feed']
        # и удаляем item['feed_subscribers']
        item['feed'] = ZenFeed(feed_name=item.pop('feed_name', None),
                               feed_subscribers=item.pop('feed_subscribers', None))
        # Заменяем списко str - kwargs['interests'] на список объектов ZenFeed
        item['interests'] = [ZenFeed(feed_name=interest) for interest in item['interests']]
        return item
