import pytest
from mongoengine import connect, disconnect, Document, StringField, IntField, ListField, ReferenceField, \
    CachedReferenceField

from src.default.spiders.zen_spider import ZenSpider

@pytest.fixture()
def zen_spider():
    spider = ZenSpider()
    spider.custom_settings.pop('JOBDIR', None)
    return spider


@pytest.fixture()
def connect_to_mock_mongo():
    yield connect('mongo_test', host='mongomock://localhost')
    disconnect()


@pytest.fixture()
def set_test_document():
    connect('mongoenginetest', host='mongomock://localhost')

    class A(Document):
        fa_str = StringField()
        fa_const = StringField()
        fa_int = IntField()
        fa_list = ListField(null=True)

    for i in range(10):
        if i > 4:
            A(fa_const='const2', fa_str=f'{i}', fa_int=i, fa_list=[i, i]).save()
        else:
            A(fa_const='const1', fa_str=f'{i}', fa_int=i, fa_list=[i, i]).save()
    yield A
    disconnect()

