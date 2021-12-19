import json

from src.rest_api.resources import ZenArticlesResources


def test_zen_articles_resource_args_handlers():
    """тест функций, обрабатывающих get параметры для передачи в db_services"""
    assert ZenArticlesResources._get_fields(arg='field1 field2 field3') == ['field1', 'field2', 'field3']
    assert ZenArticlesResources._get_fields(arg='') is None
    assert ZenArticlesResources._get_fields(arg=None) is None

    assert ZenArticlesResources._get_limit(arg='1') == 1
    assert ZenArticlesResources._get_limit(arg='not int') is None
    assert ZenArticlesResources._get_limit(arg='') is None
    assert ZenArticlesResources._get_limit(arg=None) is None

    assert ZenArticlesResources._get_page(arg='1') == 1
    assert ZenArticlesResources._get_page(arg='not int') is None
    assert ZenArticlesResources._get_page(arg='') is None
    assert ZenArticlesResources._get_page(arg=None) is None

    assert ZenArticlesResources._get_sort_field(arg='field__a') == 'field__a'
    assert ZenArticlesResources._get_sort_field(arg='') is None
    assert ZenArticlesResources._get_sort_field(arg=None) is None

    assert ZenArticlesResources._get_filters({'field1__op': 1, 'field2__op': 1}) == {'field1__op': 1, 'field2__op': 1}
    assert ZenArticlesResources._get_filters({}) == {}


def test_zen_articles_resource_getting_json(client, set_test_document):
    """тест получения ответа в json фомате"""
    ZenArticlesResources.MODEL_CLASS = set_test_document(10)
    response = client.get('/bulk/zen_articles')
    assert response.is_json
    json_response = response.get_json()
    python_response = json.loads(json_response)
    assert '_id' in python_response[0]
    assert python_response[0]['fa_int'] == 0
    assert python_response[0]['fa_const'] == 'const1'
    assert python_response[0]['fa_str'] == '0'
    assert python_response[0]['fa_list'] == [0, 1]
