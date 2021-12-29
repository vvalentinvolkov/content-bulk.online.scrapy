from src.flask_app import resources


def test_get_count(client, set_test_document):
    num = 10
    resources.MODEL_CLASSES['a'] = set_test_document(num)
    response = client.get('aggr/a?aggr_funcs=count').get_json()
    assert response['count'] == num


def test_get_sum(client, set_test_document):
    num = 10
    resources.MODEL_CLASSES['a'] = set_test_document(num)
    response = client.get('aggr/a?aggr_funcs=sum').get_json()
    assert response['sum'] == 0
    response = client.get('aggr/a?aggr_funcs=sum&aggr_field=fa_int').get_json()
    assert response['sum'] == 45
    response = client.get('aggr/a?aggr_funcs=sum&aggr_field=fa_incorrect').get_json()
    assert response['sum'] == 0
    response = client.get('aggr/a?aggr_funcs=sum&aggr_field=fa_str').get_json()
    assert response['sum'] == 0


def test_get_avg(client, set_test_document):
    num = 10
    resources.MODEL_CLASSES['a'] = set_test_document(num)
    response = client.get('aggr/a?aggr_funcs=avg').get_json()
    assert response['avg'] == 0
    response = client.get('aggr/a?aggr_funcs=avg&aggr_field=fa_int').get_json()
    assert response['avg'] == 4.5
    response = client.get('aggr/a?aggr_funcs=avg&aggr_field=fa_incorrect').get_json()
    assert response['avg'] == 0
    response = client.get('aggr/a?aggr_funcs=avg&aggr_field=fa_str').get_json()
    assert response['avg'] == 0


def test_get_all(client, set_test_document):
    num = 10
    resources.MODEL_CLASSES['a'] = set_test_document(num)
    response = client.get('aggr/a?').get_json()
    assert 'count' in response
    assert 'sum' in response
    assert 'avg' in response
