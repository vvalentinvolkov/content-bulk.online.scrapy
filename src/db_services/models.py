from mongoengine import Document, StringField, IntField, URLField, ListField, ReferenceField, NotUniqueError, NULLIFY


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
    feed_name = StringField(primary_key=True)
    feed_subscribers = IntField(default=None)

    meta = {'collection': 'zen_feeds'}

    def save(self, *args, **kwargs):
        # Если фид сохраняется из интересов, то feed_subscribers=None
        # и не переписываеться старое значение (force_insert=True)
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
    feed = ReferenceField(ZenFeed, default=ZenFeed(feed_name='default'))
    interests = ListField(ReferenceField(ZenFeed, reverse_delete_rule=NULLIFY), required=True)
    audience = IntField()
    visitors = IntField(required=True)
    read_time = IntField(required=True)
    subscribers = IntField(required=True)

    meta = {'collection': 'zen_articles',
            'cascade': True}

    def save(self, *args, **kwargs):
        for ref in self.interests:
            ref.save()
        return super().save(*args, **kwargs)


