# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CommonArticleItem(scrapy.Item):
    """Общие поля для всех статей из разных источников"""
    source = scrapy.Field()

    title = scrapy.Field()
    link = scrapy.Field()
    likes = scrapy.Field()
    reads = scrapy.Field()
    visitors = scrapy.Field()
    read_time = scrapy.Field()
    subscribers = scrapy.Field()
    comments = scrapy.Field()

    parsing_date = scrapy.Field()
    public_date = scrapy.Field()

    length = scrapy.Field()
    num_images = scrapy.Field()


