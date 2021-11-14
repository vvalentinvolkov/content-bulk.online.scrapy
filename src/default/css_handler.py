import re
from scrapy.exceptions import DropItem


def get_visitors(response) -> int:
    value = response.css('.article-stats-view__tip div:nth-child(1) span::text').get()
    parsed_value = re.search(r'^(?P<num>[\d.]*)(?P<unit>(:?k|\sтыс))*', value.lower())
    if not parsed_value:
        return 0
    elif parsed_value['unit'] and ('k' in parsed_value['unit'] or 'тыс' in parsed_value['unit']):
        return int(float(parsed_value['num'])*1000)
    else:
        return int(parsed_value['num'])


def get_reads(response) -> int:
    value = response.css('.article-stats-view__tip div:nth-child(2) span::text').get()
    parsed_value = re.search(r'^(?P<num>[\d.]*)(?P<unit>(:?k|\sтыс))*', value.lower())
    if not parsed_value:
        return 0
    elif parsed_value['unit'] and ('k' in parsed_value['unit'] or 'тыс' in parsed_value['unit']):
        return int(float(parsed_value['num'])*1000)
    else:
        return int(parsed_value['num'])


def get_read_time(response) -> int:
    value = response.css('.article-stats-view__tip div:nth-child(3) span::text').get()
    parsed_value = re.search(r'^(?P<num>[\d.]*)\s*(?P<unit>.*)', value.lower().replace(',', '.'))
    if not parsed_value:
        return 0
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


def get_num_video(response) -> int:
    value = response.css('.article-render[itemprop = "articleBody"] .zen-video-embed').getall()
    return len(value)


def get_with_form(response) -> bool:
    value = response.css('.article-render[itemprop = "articleBody"] .yandex-forms-embed').get()
    return bool(value)
