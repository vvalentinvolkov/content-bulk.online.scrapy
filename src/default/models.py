from dataclasses import dataclass

from mongoengine import Document, StringField, IntField, URLField, ListField, ReferenceField, NotUniqueError


class MyDocument(Document):
    """Базовый класс для всех документов - нужен для корректной работы db_services
    и содержит вспомогательные методы"""
    meta = {'abstract': True}

    def mtm_cascade_save(self):
        """Сохраняет документ. Потом, ищет поля ListField с вложенными ReferenceField (many-to-many)
        и сохраняет все экземпляры в найденных списках (один уровень вложености)"""
        self.save()
        if self._meta.get('cascade'):
            document_cls = type(self)
            all_field_names = document_cls._fields_ordered  # получаем имена всех полей в документе
            for field_name in all_field_names:
                field = getattr(document_cls, field_name)   # получаем объект класса Field
                if isinstance(field, ListField):
                    in_list_field = field.field     # получаем объект класса, который лежит в ListField
                    if isinstance(in_list_field, ReferenceField):
                        ref_documents = getattr(self, field_name)   # список в экземпляре документа ([<ReferenceField>])
                        for ref_document in ref_documents:
                            try:
                                ref_document.save(force_insert=ref_document._meta['force_insert'])
                            except NotUniqueError:
                                pass


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
    feed_name = StringField(primary_key=True)
    feed_subscribers = IntField()

    meta = {'collection': 'zen_feeds',
            'force_insert': True,
            'cascade': True}


class ZenArticle(CommonArticleItem):
    source = StringField(required=True, default='zen')
    feed = ReferenceField(ZenFeed, default=ZenFeed(feed_name='default'))
    interests = ListField(ReferenceField(ZenFeed), required=True)
    audience = IntField()
    visitors = IntField(required=True)
    read_time = IntField(required=True)
    subscribers = IntField(required=True)

    meta = {'collection': 'zen_articles',
            'cascade': True}




