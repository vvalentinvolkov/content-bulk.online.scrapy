import re
from datetime import datetime

from itemloaders import ItemLoader
from itemloaders.processors import Compose, TakeFirst
from scrapy.exceptions import DropItem

MONTH_NUMBERS = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12,
    'январ': 1,
    'феврал': 2,
    'март': 3,
    'апрел': 4,
    'ма': 5,
    'июн': 6,
    'июл': 7,
    'август': 8,
    'сентябр': 9,
    'октябр': 10,
    'ноябр': 11,
    'декабр': 12,
}


def _get_public_date(value: str) -> datetime:
    """Получаем по РЕ день месяц и год публикации и возвращаем datetime
    или подымаем DropItem если дата не получена"""

    # parsed_date_str['month'] собирает все что между числом и годом
    parsed_date_match = re.search(r'^(?P<day>\d{1,2})(?P<month>.*)(?P<year>\d{4})*$', value.lower())
    try:
        day = int(parsed_date_match['day'])
        year = int(parsed_date_match['year'] if parsed_date_match['year'] else datetime.now().year)
    except (ValueError, TypeError):
        print("Can't get day or year of public date")
        raise DropItem
    for month_name in MONTH_NUMBERS:
        if month_name in parsed_date_match['month']:
            month = MONTH_NUMBERS[month_name]
            break
    else:
        print("Can't get month of public date ")
        raise DropItem

    return datetime(year=year, month=month, day=day)


def _get_likes(value: str) -> int:
    parsed_value = re.search(r'^(?P<num>[\d.]*)\s(?P<unit>(:?k|тыс))*', value.lower())
    if parsed_value['unit'] and ('k' in parsed_value['unit'] or 'тыс' in parsed_value['unit']):
        return int(float(parsed_value['num'])*1000)
    else:
        return int(parsed_value['num'])


def _get_comments(value: str) -> int:
    parsed_value = re.search(r'^(?P<num>[\d.]*)\s*(?P<unit>(:?k|тыс))*', value.lower())
    if parsed_value['unit'] and ('k' in parsed_value['unit'] or 'тыс' in parsed_value['unit']):
        return int(float(parsed_value['num'])*1000)
    else:
        return int(parsed_value['num'])


def _get_subscribers(value: str) -> int:
    parsed_value = re.search(r'^(?P<num>\d+(:?\s\d*)*(?=\s))', value.lower())
    return int(parsed_value['num'].replace(' ', ''))


def _get_visitors(value: str) -> int:
    parsed_value = re.search(r'^(?P<num>[\d.]*)(?P<unit>(:?k|\sтыс))*', value.lower())
    if parsed_value['unit'] and ('k' in parsed_value['unit'] or 'тыс' in parsed_value['unit']):
        return int(float(parsed_value['num'])*1000)
    else:
        return int(parsed_value['num'])


def _get_reads(value: str) -> int:
    parsed_value = re.search(r'^(?P<num>[\d.]*)(?P<unit>(:?k|\sтыс))*', value.lower())
    if parsed_value['unit'] and ('k' in parsed_value['unit'] or 'тыс' in parsed_value['unit']):
        return int(float(parsed_value['num'])*1000)
    else:
        return int(parsed_value['num'])


def _get_read_time(value: str) -> int:
    parsed_value = re.search(r'^(?P<num>[\d.]*)\s*(?P<unit>.*)', value.lower().replace(',', '.'))
    if 'second' in parsed_value['unit'] or 'секунд' in parsed_value['unit']:
        return int(parsed_value['num'])
    if 'minut' in parsed_value['unit'] or 'минут' in parsed_value['unit']:
        return int(float(parsed_value['num'])*60)
    raise DropItem


class ZenLoader(ItemLoader):
    """Loader для статей из Zen -
    обрабатывает полчаемые <Selector> в каждом поле для загрузки в бд"""

    default_output_processor = TakeFirst()  # по умолчанию вощвращает в неизменном виде

    public_date_out = Compose(TakeFirst(), _get_public_date)
    likes_out = Compose(TakeFirst(), _get_likes)
    comments_out = Compose(TakeFirst(), _get_comments)
    subscribers_out = Compose(TakeFirst(), _get_subscribers)
    visitors_out = Compose(TakeFirst(), _get_visitors)
    reads_out = Compose(TakeFirst(), _get_reads)
    read_time_out = Compose(TakeFirst(), _get_read_time)