import time

import scrapy
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# TODO: почему не получаем ответ при while
class ZenSpider(scrapy.Spider):
    name = 'ZenSpider'
    allowed_domains = ['zen.yandex.ru']
    ZEN_MAIN = 'https://zen.yandex.ru/'
    MIN_SCRAPED_ARTICLES = 10  # Минимальное колличество статей, которое должен спарсить паучек перед остановкой

    def __init__(self):
        self.i = 0
        super().__init__()

    def start_requests(self):
        # Спарс(ш)еное колличество статей. Обнуляется, при каждом новом запуске
        while self.i < 15:
            self.i += 1
            yield scrapy.Request(url=self.ZEN_MAIN, callback=self.parse_main, dont_filter=True)

    def parse_main(self, response):
        """Ищет на главной странице ссылки на статьи (игнорируя видео)"""
        print(f'Try self.ZEN_MAIN - {self.i}')
        articles_links_from_main = response.css('.feed__row._items-count_1'
                                                ' .card-image-one-column-view__content>a::attr(href)').getall()
        for link in articles_links_from_main:
            # link = 'https://zen.yandex.ru/media/number_one_knitting/prodat-sharfik-sviazanyi-kriuchkom-za-34-000-rub-ne-realno-pokaju-vam-genialnuiu-viazalscicu-u-kotoroi-takie-ceny-612332e865102f6d71140407'
            yield SeleniumRequest(url=link, callback=self.parse_article, wait_time=1)


    # TODO: Перехват ajax запроса с данными
    def parse_article(self, response):
        """Ищет инфу на странице статьи - лайки, дочитки и т.д."""
        # with open(f'Article - 0.html', 'wb') as f:
        #     f.write(response.body)
        stats = response.css('.article-stat-tip__value::text').getall()
        article_title = response.css('h1::text').get()
        yield {
            'article': article_title,
            'visitors': stats[0],
            'reads': stats[1],
            'reading_time': stats[2],
        }
