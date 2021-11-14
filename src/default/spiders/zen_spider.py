import re

import mongoengine
from scrapy import http, Spider
from pymongo.errors import ConnectionFailure
from scrapy.exceptions import CloseSpider
from scrapy.http import TextResponse
from collections import Counter

from .. import css_handler
from ..items import ZenArticle


class ZenSpider(Spider):
    """Spider для статей из ЯндексДзена"""

    name = 'ZenSpider'
    ITEM_CLASS = ZenArticle  # Класс, унаследованый от Mongoengine.Document, для сохранения MongoPipeline
    allowed_domains = ['zen.yandex.ru']
    start_urls = ['https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&clid=300']

    # LIMIT_CRAWLED_ARTICLES = 20
    # crawled_articles = 0

    # JOBDIR необходима для проверки на дипликаты уже паршеных ссылок (из бд)
    custom_settings = {
        'JOBDIR': 'default/crawls/ZenSpider',    # Директория, для хранения состояние паука (FP спаршеных ссылок)
    }

    @staticmethod
    def mongoengine_connect(db, host, port):
        """Подключение к MongoDb через mongoengine - при ConnectionFailure подымает CloseSpider"""
        try:
            client = mongoengine.connect(db=db, host=host, port=port)
            client.admin.command('ping')
            print(f"Connect to {db}")
        except ConnectionFailure:
            print(f'MongoDb is not available')
            raise CloseSpider

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        host = crawler.settings.get('MONGO_HOST')
        port = crawler.settings.get('MONGO_PORT')
        db = crawler.settings.get('DEFAULT_MONGO_DB_NAME')
        cls.mongoengine_connect(db, host, port)
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def close(self, reason):
        # Разрываем соединение когда паук закрывается
        print(f'Mongoengine - disconnect(alias=default)')
        mongoengine.disconnect()

    def parse(self, response: TextResponse, **kwargs):
        """TODO:"""
        feed_json = response.json()
        for item in feed_json['items']:
            try:
                is_verified = item['source'].get('is_verified')
                is_video = 'video' in item
                if not is_verified and not is_video:
                    kwargs = {'title': item['title'],
                              'link': item['link'],
                              'public_date': item['publication_date']
                             }
                else:
                    continue
            except KeyError as e:
                print('Cant get from feed_json item - ', e)
            else:
                yield http.Request(url=item['channel_link'], callback=self.parse_channel, dont_filter=True,
                                   cb_kwargs=kwargs)

        yield http.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse_channel(self, response: TextResponse, **kwargs):
        try:
            document_id = re.match(r'.*-(\w*)', kwargs['link'])[1]
        except TypeError:
            print('Not zen article link - ', kwargs['link'])
            return None
        channel_json = response.json()
        try:
            source = channel_json['channel']['source']
            kwargs['subscribers'] = source['subscribers']
            kwargs['audience'] = source['audience']
            publisher_id = source['publisher_id']
            top_comments_link = 'https://zen.yandex.ru/api/comments/top-comments?' \
                                'withUser=true&retryNum=0&manualRetry=false&commentId=0&withProfile=true' \
                                f'&publisher_id={publisher_id}' \
                                f'&document_id=native%3A{document_id}' \
                                '&commentCount=100'
        except KeyError as e:
            print('Cant get from channel_json - ', e)
            return None
        return http.Request(url=top_comments_link, callback=self.parse_top_comments,
                            cb_kwargs=kwargs)

    def parse_top_comments(self, response: TextResponse, **kwargs):
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
            print('Cant get from top_comments_json - ', e)
            return None
        return http.Request(url=kwargs['link'], callback=self.parse_article,
                            cb_kwargs=kwargs)

    def parse_article(self, response, **kwargs):
        """Ищет инфу на странице статьи и передает значение из параметра "selector" в виде <Selector> -
        может передавать и список <Selector>"""

        kwargs['visitors'] = css_handler.get_visitors(response)
        kwargs['reads'] = css_handler.get_reads(response)
        kwargs['read_time'] = css_handler.get_read_time(response)
        kwargs['length'] = css_handler.get_length(response)
        kwargs['num_images'] = css_handler.get_num_images(response)
        kwargs['num_video'] = css_handler.get_num_video(response)
        kwargs['with_form'] = css_handler.get_with_form(response)

        # if self.LIMIT_CRAWLED_ARTICLES and self.crawled_articles >= self.LIMIT_CRAWLED_ARTICLES:
        #     print(f'{self.name} LIMIT_PARSED_ARTICLES_NUM <= parsed_articles: {self.crawled_articles}')
        #     raise CloseSpider
        # else:
        #     self.crawled_articles += 1
        #
        # print('<--------------------------------->')
        # print(self.crawled_articles)
        # print('<--------------------------------->')

        return kwargs
