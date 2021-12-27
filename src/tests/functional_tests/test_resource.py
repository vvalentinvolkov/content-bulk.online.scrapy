import json

from src.rest_api import resources


def test_bulk_resource_getting_json(client, set_test_document):
    """тест получения ответа в json фомате"""
    resources.MODEL_CLASSES['a'] = set_test_document(10)
    response = client.get('/bulk/a')
    assert response.is_json


def test_bulk_fields_query(client, set_test_document):
    """тест получения ответа с заданными полями fields"""
    resources.MODEL_CLASSES['a'] = set_test_document(10)
    response_ = client.get('/bulk/a?fields=fa_int+fa_str').get_json()
    response = json.loads(response_)

    for item in response:
        assert '_id' not in item
        assert 'fa_int' in item
        assert 'fa_str' in item
        assert 'fa_const' not in item
        assert 'fa_list' not in item


def test_bulk_limit_page_query(client, set_test_document):
    """тест получения ответа с заданными полями fields"""
    resources.MODEL_CLASSES['a'] = set_test_document(10)
    limit = 2
    page = 2
    response_ = client.get(f'/bulk/a?limit={limit}&page={page}').get_json()
    response = json.loads(response_)
    assert len(response) == limit

    for i, item in enumerate(response):
        assert item['fa_int'] == limit * page + i


def test_bulk_sort_query(client, set_test_document):
    """тест получение ответа, отсортированного по полю sort"""
    resources.MODEL_CLASSES['a'] = set_test_document(10)
    sort = 'fa_int__d'
    response_ = client.get(f'/bulk/a?limit=10&sort={sort}').get_json()
    response = json.loads(response_)
    for i, item in enumerate(response):
        assert item['fa_int'] == len(response) - 1 - i

    sort = 'fa_int'
    response_ = client.get(f'/bulk/a?sort={sort}').get_json()
    response = json.loads(response_)
    for i, item in enumerate(response):
        assert item['fa_int'] == i


def test_bulk_filter_query(client, set_test_document):
    """тест получение ответа, c филтрами"""
    resources.MODEL_CLASSES['a'] = set_test_document(10)
    filter_1 = 'fa_int__gt__3'
    filter_2 = 'fa_const__exact__const1'
    filter_3 = 'fa_list____4'
    response_ = client.get(f'/bulk/a?limit=10&filters={filter_1}+{filter_2}+{filter_3}').get_json()
    response = json.loads(response_)
    assert len(response) == 1
    assert response[0]['fa_int'] > 3
    assert response[0]['fa_const'] == 'const1'
    assert 4 in response[0]['fa_list']



