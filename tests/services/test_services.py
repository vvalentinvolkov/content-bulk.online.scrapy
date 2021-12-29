import pytest
from mongoengine import StringField, ConnectionFailure, FieldDoesNotExist, ValidationError, NotUniqueError, Document

from src.services import db_services


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
