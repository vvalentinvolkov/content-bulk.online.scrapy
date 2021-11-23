import re
from scrapy.exceptions import DropItem


def get_visitors(response) -> int:
    """Получение просмотров:
    - '223k story views'('223 тыс. просмотр публикации')
    - '223 story views'('223 просмотр публикации')
    """
    value = response.css('.article-stats-view__tip div:nth-child(1) span::text').get()
    parsed_value = re.search(r'^(?P<num>[\d.]*)(?P<unit>(:?k|\sтыс))*', value.lower())
    if not parsed_value:
        raise DropItem
    elif parsed_value['unit'] and ('k' in parsed_value['unit'] or 'тыс' in parsed_value['unit']):
        return int(float(parsed_value['num'])*1000)
    else:
        return int(parsed_value['num'])


def get_reads(response) -> int:
    """Получение дочиток:
    - '144k full reads'('144 тыс. прочитали')
    - '144 full reads'('144 прочитали')
    """
    value = response.css('.article-stats-view__tip div:nth-child(2) span::text').get()
    parsed_value = re.search(r'^(?P<num>[\d.]*)(?P<unit>(:?k|\sтыс))*', value.lower())
    if not parsed_value:
        raise DropItem
    elif parsed_value['unit'] and ('k' in parsed_value['unit'] or 'тыс' in parsed_value['unit']):
        return int(float(parsed_value['num'])*1000)
    else:
        return int(parsed_value['num'])


def get_read_time(response) -> int:
    """Получение дочиток:
    - '4,5 minutes — average reading time'('4,5 минуты — среднее время чтения')
    - '50 seconds — average reading time'('50 секунд — среднее время чтения')
    """
    value = response.css('.article-stats-view__tip div:nth-child(3) span::text').get()
    parsed_value = re.search(r'^(?P<num>[\d.]*)\s*(?P<unit>.*)', value.lower().replace(',', '.'))
    if not parsed_value:
        raise DropItem
    elif 'second' in parsed_value['unit'] or 'секунд' in parsed_value['unit']:
        return int(parsed_value['num'])
    if 'minut' in parsed_value['unit'] or 'минут' in parsed_value['unit']:
        return int(float(parsed_value['num'])*60)
    raise DropItem


def get_length(response) -> int:
    value = response.css('.article-render[itemprop = "articleBody"] > p *::text').getall()
    return len(''.join(value))


def get_num_images(response) -> int:
    value = response.css('.article-render[itemprop = "articleBody"] .article-image-item__image').getall()
    return len(value)

