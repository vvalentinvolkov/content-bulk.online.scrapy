from src.scrapy_app.spiders.re_handler import *


def test_get_visitors():
    """тест ре для получения visitors"""
    io_values_true = [
        ('223k story views', 223000),
        ('223 story views', 223),
        ('0 story views', 0),
        ('223 тыс. просмотр публикации', 223000),
        ('223 просмотр публикации', 223),
        ('0 просмотр публикации', 0)
    ]
    for i, o in io_values_true:
        assert get_visitors(i) == o

    io_values_false = [
        ('', 0)
    ]
    for i, o in io_values_false:
        assert get_visitors(i) is None


def test_get_reads():
    """тест ре для получения reads"""
    io_values_true = [
        ('144k full reads', 144000),
        ('144 full reads', 144),
        ('0 full reads', 0),
        ('144 тыс. прочитали', 144000),
        ('144 прочитали', 144),
        ('0 прочитали', 0)
    ]
    for i, o in io_values_true:
        assert get_reads(i) == o

    io_values_false = [
        ('', 0)
    ]
    for i, o in io_values_false:
        assert get_reads(i) is None


def test_get_read_time():
    """тест ре для получения read_time"""
    io_values_true = [
        ('4,5 minutes — average reading time', 270),
        ('10 minutes — average reading time', 600),
        ('1 minute — average reading time', 60),
        ('50 seconds — average reading time', 50),
        ('4,5 минуты — среднее время чтения', 270),
        ('10 минут — среднее время чтения', 600),
        ('1 минута — среднее время чтения', 60),
        ('50 секунд — среднее время чтения', 50)
    ]
    for i, o in io_values_true:
        assert get_read_time(i) == o

    io_values_false = [
        ('', 0)
    ]
    for i, o in io_values_false:
        assert get_read_time(i) is None


def test_get_length():
    """тест получения общей длины всех отрывков статьи"""
    final_length = 100
    s = 'a'*final_length
    list_str = [s[i*10:i*10 + 10] for i in range(10)]
    assert get_length(list_str) == final_length
    assert get_length(['']) is None
    assert get_length([]) is None
    assert get_length(None) is None


def test_get_num_images():
    assert get_num_images([1, 2, 3]) == 3
    assert get_num_images([]) is None
    assert get_num_images(None) is None

