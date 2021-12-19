from typing import Type

import pytest
from mongoengine import connect, disconnect, Document, StringField, IntField, ListField

from src.default.spiders.zen_spider import ZenSpider
from src.rest_api import app, db
from src.rest_api.resources import ZenArticlesResources


@pytest.fixture
def zen_spider():
    spider = ZenSpider()
    spider.custom_settings.pop('JOBDIR', None)
    return spider


@pytest.fixture
def set_test_document():
    class A(Document):
        fa_str = StringField()
        fa_const = StringField()
        fa_int = IntField()
        fa_list = ListField(null=True)

    def save_test_documents(num):
        for i in range(num):
            if i > num/2:
                A(fa_const='const2', fa_str=f'{i}', fa_int=i, fa_list=[i, i + 1]).save()
            else:
                A(fa_const='const1', fa_str=f'{i}', fa_int=i, fa_list=[i, i + 1]).save()
        return A

    return save_test_documents


@pytest.fixture
def connect_to_mock_mongo():
    yield connect('mongoenginetest', host='mongomock://localhost')
    disconnect()


@pytest.fixture
def client():
    api = app.create_api()
    with api.app.test_client() as client:
        with api.app.app_context():
            db.init_db()

        yield client
    disconnect()



