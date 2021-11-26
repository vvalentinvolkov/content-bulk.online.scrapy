from dataclasses import dataclass

from mongoengine import Document, StringField, IntField, URLField, ListField, ReferenceField, NotUniqueError


class MyDocument(Document):
    """Базовый класс для всех документов - нужен для корректной работы db_services
    и содержит вспомогательные методы"""
    meta = {'abstract': True}

    # TODO: переписать чрез пре методы с прверкой на каскад
    def mtm_cascade_save(self):
        """Сохраняет документ. Потом, ищет поля ListField с вложенными ReferenceField (many-to-many)
        и сохраняет все экземпляры в найденных списках"""
        self.save()
        if self._meta.get('cascade'):
            document_cls = type(self)
            # TODO: рефракторинг имен
            for field_name in document_cls._fields_ordered:
                list_field = getattr(document_cls, field_name)
                if isinstance(list_field, ListField):
                    ref_field = list_field.field
                    if isinstance(ref_field, ReferenceField):
                        for ref in getattr(self, field_name):
                            try:
                                ref.save(force_insert=ref._meta['force_insert'])
                            except NotUniqueError:
                                pass

    def __init__(self, item: dict = {}, *args, **kwargs):
        # Принимает именнованый параметр item и распоковывает его вместе с kwargs -
        # необходим для документов, не перезаписывающих __init__, т.к. db_services.save()
        # прокидывает item: dict для каждого класса
        super().__init__(*args, **kwargs, **item)


class CommonArticleItem(MyDocument):
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


class ZenFeed(MyDocument):
    feed = StringField(primary_key=True)
    feed_subscribers = IntField()

    meta = {'collection': 'zen_feeds',
            'force_insert': True,
            'cascade': True}


class ZenArticle(CommonArticleItem):
    source = StringField(required=True, default='zen')
    feed = ReferenceField(ZenFeed, default=ZenFeed(feed='default'))
    interests = ListField(ReferenceField(ZenFeed), required=True)
    audience = IntField()
    visitors = IntField(required=True)
    read_time = IntField(required=True)
    subscribers = IntField(required=True)

    meta = {'collection': 'zen_articles',
            'cascade': True}

    def __init__(self, item: dict = {}, *args, **kwargs):
        # Меняет спаршеный словарь для корректного создания ReferenceField
        if item:
            # Создаем объект ZenFeed из значений полученых пауком и записываем в item['zen_feed']
            # и удаляем item['feed'], item['feed_subscribers']
            item['feed'] = ZenFeed(feed=item.pop('feed'),
                                   feed_subscribers=item.pop('feed_subscribers', None))
            # Заменяем списко str - kwargs['interests'] на список объектов ZenFeed
            item['interests'] = [ZenFeed(feed=interest) for interest in item['interests']]
        super().__init__(*args, **kwargs, **item)




