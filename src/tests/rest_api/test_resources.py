import json

from src.rest_api import resources


def test_zen_articles_resource_getting_json(client, set_test_document):
    """тест получения ответа в json фомате"""
    resources.MODEL_CLASSES['a'] = set_test_document(10)
    response = client.get('/bulk/a?filters=fa_int__lt__3')
    assert response.is_json
    json_response = response.get_json()
    python_response = json.loads(json_response)
    assert '_id' in python_response[0]
    assert python_response[0]['fa_int'] == 0
    assert python_response[0]['fa_const'] == 'const1'
    assert python_response[0]['fa_str'] == '0'
    assert python_response[0]['fa_list'] == [0, 'str0']
