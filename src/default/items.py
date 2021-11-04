from mongoengine import Document, StringField, IntField, DateField

from .settings import DEFAULT_MONGO_COLLECTION_NAME, DEFAULT_MONGO_DB_NAME
import scrapy


class CommonArticleItem(Document):
    """Общие поля для всех статей из разных источников"""
    source = StringField()
    title = StringField()
    url = StringField()
    likes = IntField()
    reads = IntField()
    visitors = IntField()
    read_time = IntField()
    subscribers = IntField()
    comments = IntField()
    parsing_date = DateField()
    public_date = DateField()
    length = IntField()
    num_images = IntField()

    meta = {'allow_inheritance': True}


class ZenArticle(CommonArticleItem):
    meta = {'collection': DEFAULT_MONGO_COLLECTION_NAME}
    pass
