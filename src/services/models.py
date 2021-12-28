from mongoengine import Document, StringField, IntField, URLField, ListField, NotUniqueError
from .query_set_converter import ConvertibleQuerySet


class CommonArticleItem(Document):
    """Общие поля для всех статей из разных источников"""
    source = StringField(required=True)
    title = StringField(required=True)
    link = URLField(required=True, unique=True)
    likes = IntField(required=True)
    reads = IntField(required=True)
    comments = IntField(required=True)
    time_public_to_parse = IntField(required=True)
    public_date = IntField(required=True)
    length = IntField(required=True)
    num_images = IntField(required=True)

    meta = {'abstract': True}


class ZenFeed(Document):
    feed_name = StringField(required=True, unique=True)
    feed_subscribers = IntField(default=None)

    meta = {'collection': 'zen_feeds',
            'queryset_class': ConvertibleQuerySet}

    def save(self, *args, **kwargs):
        # Если feed_subscribers=None
        # не переписываеться старое значение (force_insert=True)
        if self.feed_subscribers:
            kwargs['force_insert'] = False
            return super().save(*args, **kwargs)
        else:
            kwargs['force_insert'] = True
            try:
                return super().save(*args, **kwargs)
            except NotUniqueError:
                pass


class ZenArticle(CommonArticleItem):
    source = StringField(required=True, default='zen')
    interests = ListField(field=StringField(), required=True, null=True, default=None)
    audience = IntField()
    visitors = IntField(required=True)
    read_time = IntField(required=True)
    subscribers = IntField(required=True)

    meta = {'collection': 'zen_articles',
            'queryset_class': ConvertibleQuerySet}



