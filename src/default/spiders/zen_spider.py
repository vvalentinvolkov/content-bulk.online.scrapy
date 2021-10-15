import scrapy
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class ZenSpider(scrapy.Spider):
    name = 'ZenSpider'
    ZEN_MAIN = 'https://zen.yandex.ru/'

    MIN_SCRAPED_ARTICLES = 10  # Минимальное колличество статей, которое должен спарсить паучек перед остановкой

    def __init__(self):
        self.scraped_articles = 0
        super().__init__()

    def start_requests(self):
        # Спарс(ш)еное колличество статей. Обнуляется, при каждом новом запуске
        # while self.scraped_articles < 10:
        #     print('Try self.ZEN_MAIN')
        yield scrapy.Request(url=self.ZEN_MAIN, callback=self.parse_main)

    def parse_main(self, response):
        """Ищет на главной странице ссылки на статьи (игнорируя видео)"""
        self.scraped_articles += 1
        articles_links_from_main = response.css('.feed__row._items-count_1'
                                                ' .card-image-one-column-view__content>a::attr(href)').getall()
        for link in articles_links_from_main:
            if link.startswith('https://zen.yandex.ru/'):
                yield SeleniumRequest(url=link, callback=self.parse_article)


    def parse_article(self, response):
        """Ищет инфу на странице статьи - лайки, дочитки и т.д."""
        with open(f'Article - {self.scraped_articles}.html', 'wb') as f:
            f.write(response.body)
        # print(response.css('article-stat-tip__value::text').get())
        # yield {
        #     'visitors': response.css('article-stat-tip__value::text')[0],
        #     'reads': response.css('article-stat-tip__value::text')[1],
        #     'reading_time': response.css('article-stat-tip__value::text')[2],
        # }
