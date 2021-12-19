import pytest
from mongoengine import StringField, ListField, ReferenceField, ConnectionFailure, FieldDoesNotExist, ValidationError, \
    NotUniqueError, Document

from src.services import db_services
from src.services.models import ZenArticle, ZenFeed
from src.default.pipelines import MongoPipeline
from src.default.spiders.zen_spider import ZenSpider


class SomeItem(Document):
    first_field = StringField(required=True, unique=True)
    second_field = StringField()


class TestDbServices:
    """"""
    def test_db_save_dict(self, connect_to_mock_mongo):
        """тест корректного сохранения словаря"""
        item = {'first_field': 'first_value',
                'second_field': 'second_value'}
        db_services.db_save(document_class=SomeItem, item=item)
        assert SomeItem.objects().first().first_field == 'first_value'

    def test_db_save_document(self, connect_to_mock_mongo):
        """тест корректного сохранения словаря"""
        _item = {'first_field': 'first_value',
                 'second_field': 'second_value'}
        item = SomeItem(**_item)
        db_services.db_save(item=item)
        assert SomeItem.objects().first().first_field == 'first_value'

    def test_db_save_with_db_not_available(self):
        """тест: сохранение при недоступной бд поднимает ConnectionFailure"""
        item = {'first_field': 'first_value', 'second_field': 'second_value'}
        with pytest.raises(ConnectionFailure):
            db_services.db_save(document_class=SomeItem, item=item)

    def test_db_save_with_extra_value_in_item(self, connect_to_mock_mongo):
        """тест: сохранение словаря с лишними или недостающими значениями поднимает DropItem"""
        item = {'first_field': 'first_value',
                 'second_field': 'second_value',
                 'extra_field': 'some_extra_value'}

        with pytest.raises(FieldDoesNotExist):
            db_services.db_save(document_class=SomeItem, item=item)

    def test_db_save_with_not_valid_item(self, connect_to_mock_mongo):
        """тест: сохранение словаря с не валидными значениями поднимает DropItem"""
        item1 = {'first_field': 0,
                 'second_field': None}
        item2 = {'first_field': None,
                 'second_field': None}
        item3 = {'second_field': 'second_value'}

        with pytest.raises(ValidationError):
            db_services.db_save(document_class=SomeItem, item=item1)
            db_services.db_save(document_class=SomeItem, item=item2)
            db_services.db_save(document_class=SomeItem, item=item3)

    def test_db_save_with_duplicate(self, connect_to_mock_mongo):
        """тест: сохранение дупликата подымает DropItem"""
        item1 = {'first_field': 'first_value',
                 'second_field': 'second_value'}
        item2 = {'first_field': 'first_value',
                 'second_field': 'other_value'}

        db_services.db_save(document_class=SomeItem, item=item1)
        with pytest.raises(NotUniqueError):
            db_services.db_save(document_class=SomeItem, item=item2)


class TestItems:
    """"""
    parsed_item1 = dict(feed_name='feed1', feed_subscribers=100, title='title1', link='https://zen.yandex.ru/',
                        public_date=200, time_public_to_parse=300, subscribers=400, audience=500, likes=600,
                        comments=700, interests=['feed1', 'feed2', 'feed3'], visitors=800, reads=900, read_time=1000,
                        length=1100, num_images=1200)
    parsed_item2 = dict(feed_name='feed2', feed_subscribers=100, title='title1', link='https://zen.yandex.ru/2',
                        public_date=200, time_public_to_parse=300, subscribers=400, audience=500, likes=600,
                        comments=700, interests=['feed1', 'feed2', 'feed3'], visitors=800, reads=900, read_time=1000,
                        length=1100, num_images=1200)

    def test_save_zen_article_with_creating_zen_feed(self, connect_to_mock_mongo):
        """тест: при сохранении ZenArticle создаются и сохраняются обхекты feed
        из атрибутов feed и interests, без перезаписи уже существующий ZenFeed"""
        spider_res_gen1 = ZenSpider.load_item(self.parsed_item1)
        spider_res_gen2 = ZenSpider.load_item(self.parsed_item2)
        MongoPipeline().process_item(item=next(spider_res_gen1))
        MongoPipeline().process_item(item=next(spider_res_gen1))
        MongoPipeline().process_item(item=next(spider_res_gen2))
        MongoPipeline().process_item(item=next(spider_res_gen2))

        articles = ZenArticle.objects.all()
        feeds = ZenFeed.objects.all()

        assert len(articles) == 2
        assert articles[0].title == 'title1'
        assert len(feeds) == 2
        assert next(f for f in feeds if f.feed_name == 'feed1').feed_subscribers == 100
        assert next(f for f in feeds if f.feed_name == 'feed2').feed_subscribers == 100
