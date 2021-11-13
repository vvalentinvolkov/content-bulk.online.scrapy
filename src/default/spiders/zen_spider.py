import re

import mongoengine
import scrapy
from pymongo.errors import ConnectionFailure
from scrapy.exceptions import CloseSpider
from scrapy.http import TextResponse
from scrapy_splash import SplashRequest
import simplejson as json

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ..items import ZenArticle
from ..loaders import ZenLoader


class ZenSpider(scrapy.Spider):
    """Spider для статей из ЯндексДзена"""

    name = 'ZenSpider'
    ITEM_CLASS = ZenArticle  # Класс, унаследованый от Mongoengine.Document, для сохранения MongoPipeline
    allowed_domains = ['zen.yandex.ru']
    start_urls = ['https://zen.yandex.ru/api/v3/launcher/export?country_code=ru&clid=300']

    LIMIT_CRAWLED_ARTICLES = 10
    crawled_articles = 0

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
            print(f"Connect to {db}")
        except ConnectionFailure:
            print(f'MongoDb is not available')
            raise CloseSpider

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        host = crawler.settings.get('MONGO_HOST')
        port = crawler.settings.get('MONGO_PORT')
        db = crawler.settings.get('DEFAULT_MONGO_DB_NAME')
        # cls.mongoengine_connect(db, host, port)
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def close(self, reason):
        # Разрываем соединение когда паук закрывается
        print(f'Mongoengine - disconnect(alias=default)')
        mongoengine.disconnect()

    def parse(self, response: TextResponse, **kwargs):
        """TODO:"""
        feed_json = json.load(response.text)

        for item in feed_json['items']:
            try:
                is_verified = item['source'].get('is_verified')
                is_video = 'video' in item
                if not is_verified and not is_video:
                    cb_kwargs = {'title': item['title'],
                                 'article_link': item['link'],
                                 'publication_date': item['publication_date']
                                 }
                else:
                    print('Is video or verified')
                    continue
            except KeyError as e:
                print('Cant get something from feed_json', e)
            else:
                yield scrapy.Request(url=item['channel_link'], callback=self.parse_channel, dont_filter=True,
                                     cb_kwargs=cb_kwargs)

        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)
    # TODO: Что надо вернуть мб ошибку в  error_cb
    def parse_channel(self, response: TextResponse, **kwargs):
        channel_json = json.load(response.text)
        try:
            source = channel_json['channel']['source']

            kwargs['subscribers'] = source['subscribers']
            kwargs['audience'] = source['audience']

            publisher_id = source['publisher_id']
            document_id = re.match(r'.*-(\w*)', kwargs['article_link'])[1]
            top_comments_link = 'https://zen.yandex.ru/api/comments/top-comments?' \
                                'withUser=true&retryNum=0&manualRetry=false&commentId=0&withProfile=true' \
                                f'&{publisher_id}=601c6ae930694e141a19391d' \
                                f'&{document_id}=native%3A612c02ed4b943d646eed8032&commentCount=100'
        except KeyError as e:
            print('Cant get something from channel_json', e)
            return None
        else:
            scrapy.Request(url=top_comments_link, callback=self.parse_top_comments,
                           cb_kwargs=kwargs)

    def parse_top_comments(self, response: TextResponse, **kwargs):
        top_comments_json = json.load(response.text)
        try:
            meta = top_comments_json['meta']
            is_visible_comments = meta.get('visibleComments') == 'visible'
            if is_visible_comments:
                kwargs['likes'] = meta['publicationLikeCount']
                kwargs['comments'] = meta['commentsCount'] + meta['answersCount']
            else:
                return None
        except KeyError as e:
            print('Cant get something from top_comments_json', e)
            return None
        else:
            yield scrapy.Request(url=kwargs['article_link'], callback=self.parse_article,
                                 cb_kwargs=kwargs)

    def parse_article(self, response, **kwargs):
        """Ищет инфу на странице статьи и передает значение из параметра "selector" в виде <Selector> -
        может передавать и список <Selector>"""
        har = response.data['har']
        zen_loader = ZenLoader(selector=response.data['html'].css('body'))

        # zen_loader.add_css('title', 'h1::text')
        zen_loader.add_value('url', response.url)
        # zen_loader.add_css('public_date', '.article-stats-view__item[itemprop="datePublished"]::text')
        # zen_loader.add_css('likes', '.left-block-redesign-view button:nth-child(1) .left-column-button__text_short::text')
        # zen_loader.add_css('comments', '.left-block-redesign-view button:nth-child(3) .left-column-button__text_short::text')
        zen_loader.add_css('visitors', '.article-stats-view__tip div:nth-child(1) span::text')
        zen_loader.add_css('reads', '.article-stats-view__tip div:nth-child(2) span::text')
        zen_loader.add_css('read_time', '.article-stats-view__tip div:nth-child(3) span::text')
        # zen_loader.add_css('subscribers', '.publisher-controls__subtitle::text')
        zen_loader.add_css('length', '.article-render[itemprop = "articleBody"] > p *::text')
        zen_loader.add_css('num_images', '.article-render[itemprop = "articleBody"] .article-image-item__image')
        zen_loader.add_css('num_video', '.article-render[itemprop = "articleBody"] .zen-video-embed')
        zen_loader.add_css('with_form', '.article-render[itemprop = "articleBody"] .yandex-forms-embed')

        item = zen_loader.load_item()
        if self.LIMIT_CRAWLED_ARTICLES and self.crawled_articles >= self.LIMIT_CRAWLED_ARTICLES:
            print(f'{self.name} LIMIT_PARSED_ARTICLES_NUM <= parsed_articles: {self.crawled_articles}')
            raise CloseSpider
        else:
            self.crawled_articles += 1
        print(item)
        # return item
