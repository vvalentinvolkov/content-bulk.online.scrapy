from datetime import datetime

from mongoengine import Document, StringField, IntField, DateField, URLField, DateTimeField, BooleanField

from .settings import DEFAULT_MONGO_COLLECTION_NAME, DEFAULT_MONGO_DB_NAME
import scrapy


class CommonArticleItem(Document):
    """Общие поля для всех статей из разных источников"""
    source = StringField(required=True)
    title = StringField(required=True)
    url = URLField(required=True, unique=True)
    likes = IntField(required=True)
    reads = IntField(required=True)
    visitors = IntField(required=True)
    read_time = IntField(required=True)
    subscribers = IntField(required=True)
    comments = IntField(required=True, default=0)
    parsing_date = DateField(required=True, default=datetime.utcnow())
    public_date = DateField(required=True)
    length = IntField(required=True)
    num_images = IntField(required=True, default=0)
    num_video = IntField(required=True, default=0)
    with_form = BooleanField(required=True, default=False)

    meta = {'abstract': True}


class ZenArticle(CommonArticleItem):
    source = StringField(required=True, default='zen')
    meta = {'collection': DEFAULT_MONGO_COLLECTION_NAME}
