from mongoengine import Document, StringField, IntField, URLField, ListField, ReferenceField


class CommonArticleItem(Document):
    """Общие поля для всех статей из разных источников"""
    source = StringField(required=True)
    title = StringField(required=True)
    link = URLField(required=True, unique=True)
    interests = ListField(default=['No data'])
    audience = IntField(default=0)
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

    meta = {'abstract': True}


class ZenFeed(Document):
    feed = StringField(required=True, unique=True, defaut='main')
    feed_subscribers = IntField(required=True, defaut=0)

    meta = {'collection': 'zen_interests'}


class ZenArticle(CommonArticleItem):
    source = StringField(required=True, default='zen')
    zen_feed = ReferenceField(ZenFeed)

    meta = {'collection': 'zen_articles'}

    def __init__(self, *args, **kwargs):
        kwargs['zen_feed'] = ZenFeed(feed=kwargs.pop('feed', None),
                                     feed_subscribers=kwargs.pop('feed_subscribers', None))
        super().__init__(*args, **kwargs)

