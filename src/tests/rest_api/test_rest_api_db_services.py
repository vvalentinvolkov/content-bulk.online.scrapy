from src.services.db_services import get_query_set


def test_get_query_set_fields(connect_to_mock_mongo, set_test_document):
    """тест получение заданных полей"""
    A = set_test_document(10)
    res = get_query_set(A, fields=('fa_str', 'fa_int'))
    assert res[0].fa_str == '0'
    assert res[0].fa_int == 0
    assert res[0].fa_list is None

    res = get_query_set(A)
    assert res[0].fa_const == 'const1'
    assert res[0].fa_str == '0'
    assert res[0].fa_int == 0
    assert res[0].fa_list == [0, 1]

    res = get_query_set(A, fields=('fa_str', 'fa_int', 'not_existed'))
    assert res[0].fa_str == '0'
    assert res[0].fa_int == 0
    assert res[0].fa_list is None


def test_get_query_set_limit_and_page(connect_to_mock_mongo, set_test_document):
    """тест получение данных ограниченых page и limit"""
    num = 10
    A = set_test_document(num)

    for page in range(num):
        for limit in range(1, num):
            res = get_query_set(A, limit=limit, page=page)
            if limit >= num and page < num/limit:
                assert len(res) == num
                assert res[0].fa_int == page * limit
                assert res[num-1].fa_int == page*limit + num
            if (limit < num and page >= num/limit) or (limit >= num and page >= num/limit):
                assert len(res) == 0
            if limit < num < num and page < num/limit:
                assert len(res) == limit
                assert res[0].fa_int == page*limit
                assert res[limit].fa_int == page*limit + limit


def test_get_query_set_sort_field(connect_to_mock_mongo, set_test_document):
    """тест сортировки по одному полю"""
    A = set_test_document(10)

    res = get_query_set(A, sort_field='fa_int__a')
    assert res[0].fa_int == 0

    res = get_query_set(A, sort_field='fa_int__d')
    assert res[0].fa_int == 9

    res = get_query_set(A, sort_field='notfield__d')
    assert res[0].fa_int == 0

    res = get_query_set(A, sort_field='fa_int__notcorrect')
    assert res[0].fa_int == 0


def test_get_query_set_filters(connect_to_mock_mongo, set_test_document):
    """тест: фильтры по значениям полей"""
    A = set_test_document(10)

    res = get_query_set(A, limit=100,filters='fa_const__exact__const1 fa_int__lt__3 fa_int__gt__0')
    assert len(res) == 2
    assert res[0].fa_const == 'const1'
    assert res[0].fa_int == 1

    res = get_query_set(A, limit=100, filters='fa_const__exact__const3 fa_int__lt__3')
    assert len(res) == 0

    res = get_query_set(A, limit=100, filters='fa_int__notcorrect__3')
    assert len(res) == 10

    res = get_query_set(A, limit=100, filters='notfield__lt__3')
    assert len(res) == 10
