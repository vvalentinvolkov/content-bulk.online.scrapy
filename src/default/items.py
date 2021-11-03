# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from .settings import DEFAULT_MONGO_COLLECTION_NAME
import scrapy


class CommonArticleItem(scrapy.Item):
    """Общие поля для всех статей из разных источников"""
    COLLECTION_NAME = DEFAULT_MONGO_COLLECTION_NAME

    source = scrapy.Field()

    title = scrapy.Field()
    url = scrapy.Field()
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
    # SHOULDBE: Конструктор валид схемы из полей класса
    VALID_SCHEME = {
       "validator": {
          "$jsonSchema": {
             "required": [
                "source",
                "title",
                "link"
                # "likes",
                # "reads",
                # "visitors",
                # "read_time",
                # "subscribers",
                # "comments",
                # "parsing_date",
                # "public_date",
                # "length",
                # "num_images"
             ],
             "properties": {
                "source": {
                   "bsonType": "string",
                   "enum": ["zen"],
                   "description": "must be a string and is required"
                },
                "title": {
                   "bsonType": "string",
                   "description": "must be a string and is required"
                },
                "link": {
                   "bsonType": "string",
                   "description": "must be a string and is required"
                },
                "likes": {
                   "bsonType": "int",
                   "description": "must be a string and is required"
                },
                "reads": {
                   "bsonType": "int",
                   "description": "must be a string and is required"
                },
                "visitors": {
                   "bsonType": "int",
                   "description": "must be a string and is required"
                },
                "read_time": {
                   "bsonType": "int",
                   "description": "must be a string and is required"
                },
                "subscribers": {
                   "bsonType": "int",
                   "description": "must be a string and is required"
                },
                "comments": {
                   "bsonType": "int",
                   "description": "must be a string and is required"
                },
                "parsing_date": {
                   "bsonType": "",
                   "description": "must be a string and is required"
                },
                "public_date": {
                   "bsonType": "",
                   "description": "must be a string and is required"
                },
                "length": {
                   "bsonType": "int",
                   "description": "must be a string and is required"
                },
                "num_images": {
                   "bsonType": "int",
                   "description": "must be a string and is required"
               }
             }
          }
       }
    }


class ZenArticle(CommonArticleItem):
    pass
