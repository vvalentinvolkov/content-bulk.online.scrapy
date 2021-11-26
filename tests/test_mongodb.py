import pytest
from mongoengine import Document, StringField, connect, disconnect, ListField, ReferenceField, IntField, URLField, \
    NotUniqueError
from scrapy.exceptions import CloseSpider, DropItem

from src.default import db_services
from src.default.items import ZenArticle, ZenFeed, MyDocument
from src.default.spiders.zen_spider import ZenSpider


class SomeItem(MyDocument):
    first_field = StringField(required=True, unique=True)
    second_field = StringField()


@pytest.fixture()
def connect_to_mongo():
    connect('mongo_test', host='mongomock://localhost')
    yield
    disconnect()


class TestDbServices:
    """"""
    def test_db_save_dict(self, connect_to_mongo):
        """тест корректного сохранения словаря"""
        item = {'first_field': 'first_value',
                'second_field': 'second_value'}
        db_services.db_save(document_class=SomeItem, item=item)
        assert SomeItem.objects().first().first_field == 'first_value'

    def test_db_save_document(self, connect_to_mongo):
        """тест корректного сохранения словаря"""
        _item = {'first_field': 'first_value',
                 'second_field': 'second_value'}
        item = SomeItem(**_item)
        db_services.db_save(item=item)
        assert SomeItem.objects().first().first_field == 'first_value'

    def test_db_save_with_db_not_available(self):
        """тест: сохранение при недоступной бд поднимает CloseSpider"""
        item = {'first_field': 'first_value', 'second_field': 'second_value'}
        with pytest.raises(CloseSpider):
            db_services.db_save(document_class=SomeItem, item=item)

    def test_db_save_with_extra_missing_value_in_item(self, connect_to_mongo):
        """тест: сохранение словаря с лишними или недостающими значениями поднимает DropItem"""
        item = {'first_field': 'first_value',
                 'second_field': 'second_value',
                 'extra_field': 'some_extra_value'}

        with pytest.raises(DropItem):
            db_services.db_save(document_class=SomeItem, item=item)

    def test_db_save_with_not_valid_item(self, connect_to_mongo):
        """тест: сохранение словаря с не валидными значениями поднимает DropItem"""
        item1 = {'first_field': 0,
                 'second_field': None}
        item2 = {'first_field': None,
                 'second_field': None}
        item3 = {'second_field': 'second_value'}

        with pytest.raises(DropItem):
            db_services.db_save(document_class=SomeItem, item=item1)
            db_services.db_save(document_class=SomeItem, item=item2)
            db_services.db_save(document_class=SomeItem, item=item3)

    def test_db_save_with_duplicate(self, connect_to_mongo):
        """тест: сохранение дупликата подымает DropItem"""
        item1 = {'first_field': 'first_value',
                 'second_field': 'second_value'}
        item2 = {'first_field': 'first_value',
                 'second_field': 'other_value'}

        db_services.db_save(document_class=SomeItem, item=item1)
        with pytest.raises(DropItem):
            db_services.db_save(document_class=SomeItem, item=item2)

    def test_cascade_save_for_many_to_many(self, connect_to_mongo):
        """тест: при сохранении документа с many-to-many полем: ListField(ReferenceField(<Document>))
        сохраняет связанные документы"""
        class RefItem(MyDocument):
            field = StringField(primary_key=True)

            meta = {'cascade': True,
                    'force_insert': True}

        class BaseItem(MyDocument):
            ref_field = ReferenceField(RefItem, default=RefItem(field='default'))
            field = ListField(ReferenceField(RefItem), required=True)
            meta = {'cascade': True}

        ref_item1 = RefItem(field='ref_item1')
        ref_item2 = RefItem(field='ref_item2')

        base_item = BaseItem(ref_field=ref_item1, field=[ref_item1, ref_item2])

        db_services.db_save(base_item)
        base_items = BaseItem.objects.all()
        ref_items = RefItem.objects.all()

        assert len(base_items) == 1
        assert len(ref_items) == 2


class TestItems:
    """"""
    parsed_item = dict(feed='feed1', feed_subscribers=100, title='title1', link='https://zen.yandex.ru/',
                       public_date=200, time_public_to_parse=300, subscribers=400, audience=500, likes=600,
                       comments=700, interests=['feed1', 'feed2', 'feed3'], visitors=800, reads=900, read_time=1000,
                       length=1100, num_images=1200)
    parsed_item2 = dict(feed='feed2', feed_subscribers=100, title='title1', link='https://zen.yandex.ru/2',
                        public_date=200, time_public_to_parse=300, subscribers=400, audience=500, likes=600,
                        comments=700, interests=['feed1', 'feed2', 'feed3'], visitors=800, reads=900, read_time=1000,
                        length=1100, num_images=1200)

    def test_save_zen_article_with_creating_zen_feed(self, connect_to_mongo):
        """тест: при сохранении ZenArticle создаются и сохраняются обхекты feed
        из атрибутов feed и interests, без перезаписи уже существующий ZenFeed"""
        db_services.db_save(document_class=ZenArticle, item=self.parsed_item)
        db_services.db_save(document_class=ZenArticle, item=self.parsed_item2)
        articles = ZenArticle.objects.all()
        feeds = ZenFeed.objects.all()

        assert len(articles) == 2
        assert articles[0].title == 'title1'
        assert len(feeds) == 3
        assert next(f for f in feeds if f.feed == 'feed1').feed_subscribers == 100
        assert next(f for f in feeds if f.feed == 'feed2').feed_subscribers == 100
        assert next(f for f in feeds if f.feed == 'feed3').feed_subscribers is None
