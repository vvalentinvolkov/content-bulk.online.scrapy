import mongoengine
import pytest
from mongoengine import Document, StringField, IntField, ListField, ReferenceField, LookUpError

from src.rest_api.db_services import get_query_set


# class A(Document):
#     fa_str = StringField()
#     fa_int = IntField()
#     fa_list = ListField()


def test_get_query_set_fields(set_test_document):
    """тест получение заданных полей"""
    A = set_test_document
    res = get_query_set(A, fields=('fa_str', 'fa_int'))

    assert res[0].fa_str == '0'
    assert res[0].fa_int == 0
    assert res[0].fa_list is None

    res = get_query_set(A)
    assert res[0].fa_const == 'const1'
    assert res[0].fa_str == '0'
    assert res[0].fa_int == 0
    assert res[0].fa_list == [0, 0]

    with pytest.raises(LookUpError):
        get_query_set(A, fields=('fa_str', 'fa_int', 'fa_list', 'not_existed'))


def test_get_query_set_limit_and_page(set_test_document):
    """тест получение данных ограниченых page и limit"""
    A = set_test_document

    res = get_query_set(A, limit=3, page=2)
    assert len(res) == 3
    assert res[0].fa_int == 6

    res = get_query_set(A)
    assert len(res) == 1

    res = get_query_set(A, limit=20, page=2)
    assert len(res) == 0

    res = get_query_set(A, limit=20, page=0)
    assert len(res) == 10


def test_get_query_set_sort_field(set_test_document):
    """тест сортировки по одному полю"""
    A = set_test_document

    res = get_query_set(A, sort_field='+fa_int')
    assert res[0].fa_int == 0

    res = get_query_set(A, sort_field='-fa_int')
    assert res[0].fa_int == 9


def test_get_query_set_filters(set_test_document):
    """тест: фильтры по значениям полей"""
    A = set_test_document

    res = get_query_set(A,
                        limit=100,
                        filters={
                            'fa_const__exact': 'const1',
                            'fa_int__lt': 3,
                            'fa_int__gt': 0
                        }
                        )
    assert len(res) == 2
    assert res[0].fa_const == 'const1'
    assert res[0].fa_int == 1

    res = get_query_set(A,
                        limit=100,
                        filters={
                            'fa_const__exact': 'const3',
                            'fa_int__lt': 3,
                            'fa_int__gt': 0
                        }
                        )
    assert len(res) == 0
