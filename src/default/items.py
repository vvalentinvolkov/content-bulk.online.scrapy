from datetime import datetime

from mongoengine import Document, StringField, IntField, URLField, BooleanField, ListField

from .settings import DEFAULT_MONGO_COLLECTION_NAME


class CommonArticleItem(Document):
    """Общие поля для всех статей из разных источников"""
    source = StringField(required=True)
    title = StringField(required=True)
    link = URLField(required=True, unique=True)
    interests = ListField(default=['No data'])
    audience = IntField(required=True)
    likes = IntField(required=True)
    reads = IntField(required=True)
    visitors = IntField(required=True)
    read_time = IntField(required=True)
    subscribers = IntField(required=True)
    comments = IntField(required=True)
    time_public_to_parse = IntField(required=True)
    public_date = IntField(required=True)
    length = IntField(required=True)
    num_images = IntField(required=True)
    num_video = IntField(required=True)
    with_form = BooleanField(required=True)

    meta = {'abstract': True}


class ZenArticle(CommonArticleItem):
    source = StringField(required=True, default='zen')
    meta = {'collection': DEFAULT_MONGO_COLLECTION_NAME}
