import mongoengine
import scrapy
from pymongo.errors import ConnectionFailure
from scrapy.exceptions import CloseSpider
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ..items import ZenArticle
from ..loaders import ZenLoader


class ZenSpider(scrapy.Spider):
    """Spider для статей из ЯндексДзена"""

    name = 'ZenSpider'
    ITEM_CLASS = ZenArticle    # Класс, унаследованый от Mongoengine.Document, для сохранения MongoPipeline
    allowed_domains = ['zen.yandex.ru']
    start_urls = ['https://zen.yandex.ru/']

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
        cls.mongoengine_connect(db, host, port)
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def close(self, reason):
        # Разрываем соединение когда паук закрывается
        print(f'Mongoengine - disconnect(alias=default)')
        mongoengine.disconnect()

    def parse(self, response, **kwargs):
        """Ищет на главной странице ссылки на статьи,
        игнорируя видео и ссылки на стороние сайты (см. self.allowed_domains) """
        link_articles_from_main = (a.attrib['href'] for a in
                                   response.css('.feed__row._items-count_1 .card-image-one-column-view__content > a'))

        # for link in link_articles_from_main:
        for link in ['https://zen.yandex.ru/media/automaniac/razobral-dvigatel-lady-vesty-18-l-vaz-21179-pokazyvaiu-iz-chego-sdelan-etot-motor-i-est-li-v-nem-rossiiskie-komplektuiuscie-61519246bd215b71fd3c6b26',
                     'https://zen.yandex.ru/media/zenwhatsnew/klast-ili-lojit-proidite-korotkii-test-na-gramotnost-i-uznaite-chto-u-vas-po-russkomu-iazyku-na-samom-dele-61370e227ce5df2042c41fe1',
                     'https://zen.yandex.ru/media/automaniac/razobral-dvigatel-lady-vesty-18-l-vaz-21179-pokazyvaiu-iz-chego-sdelan-etot-motor-i-est-li-v-nem-rossiiskie-komplektuiuscie-61519246bd215b71fd3c6b26']:
            yield SeleniumRequest(url=link,
                                  callback=self.parse_article,
                                  wait_time=4,
                                  wait_until=EC.element_to_be_clickable(
                                      (By.CSS_SELECTOR, '.left-column-button__text_short')),
                                  meta={"proxy": "localhost:58200"}
                                  )
        # yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse_article(self, response, **kwargs):
        """Ищет инфу на странице статьи и передает значение из параметра "selector" в виде <Selector> -
        может передавать и список <Selector>"""
        zen_loader = ZenLoader(selector=response.css('body'))

        zen_loader.add_css('title', 'h1::text')
        zen_loader.add_value('url', response.url)
        zen_loader.add_css('public_date', '.article-stats-view__item[itemprop="datePublished"]::text')
        zen_loader.add_css('likes', '.left-block-redesign-view button:nth-child(1) .left-column-button__text_short::text')
        zen_loader.add_css('comments', '.left-block-redesign-view button:nth-child(3) .left-column-button__text_short::text')
        zen_loader.add_css('visitors', '.article-stats-view__tip div:nth-child(1) span::text')
        zen_loader.add_css('reads', '.article-stats-view__tip div:nth-child(2) span::text')
        zen_loader.add_css('read_time', '.article-stats-view__tip div:nth-child(3) span::text')
        zen_loader.add_css('subscribers', '.publisher-controls__subtitle::text')
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
