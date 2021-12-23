import logging
import re
from typing import Optional


logger = logging.getLogger(__name__)


def get_visitors(text: str) -> Optional[int]:
    """Получение просмотров:
    - '223k story views'('223 тыс. просмотр публикации')
    - '223 story views'('223 просмотр публикации')
    """
    if text:
        parsed_value = re.search(r'^(?P<num>[\d.]+)(?P<unit>(:?k|\sтыс))*', text.lower())
        if not parsed_value:
            logger.warning(f'Unreadable value {text}')
            return None
        elif parsed_value['unit'] and ('k' in parsed_value['unit'] or 'тыс' in parsed_value['unit']):
            return int(float(parsed_value['num'])*1000)
        else:
            return int(parsed_value['num'])
    return None


def get_reads(text: str) -> Optional[int]:
    """Получение дочиток:
    - '144k full reads'('144 тыс. прочитали')
    - '144 full reads'('144 прочитали')
    """
    if text:
        parsed_value = re.search(r'^(?P<num>[\d.]+)(?P<unit>(:?k|\sтыс))*', text.lower())
        if not parsed_value:
            logger.warning(f'Unreadable value {text}')
            return None
        elif parsed_value['unit'] and ('k' in parsed_value['unit'] or 'тыс' in parsed_value['unit']):
            return int(float(parsed_value['num'])*1000)
        else:
            return int(parsed_value['num'])
    return None


def get_read_time(text: str) -> Optional[int]:
    """Получение дочиток:
    - '4,5 minutes — average reading time'('4,5 минуты — среднее время чтения')
    - '50 seconds — average reading time'('50 секунд — среднее время чтения')
    """
    if text:
        parsed_value = re.search(r'^(?P<num>[\d.]+)\s*(?P<unit>.*)', text.lower().replace(',', '.'))
        if not parsed_value:
            logger.warning(f'Unreadable value {text}')
            return None
        elif 'second' in parsed_value['unit'] or 'секунд' in parsed_value['unit']:
            return int(parsed_value['num'])
        if 'minut' in parsed_value['unit'] or 'минут' in parsed_value['unit']:
            return int(float(parsed_value['num'])*60)
    return None


def get_length(texts: list) -> Optional[int]:
    length = len(''.join(texts))
    if length == 0:
        return None
    return length


def get_num_images(tags: list) -> Optional[int]:
    if tags:
        return len(tags)
    return None

