import argparse
from typing import Iterable, Union

from src.scrapy_app.crawl_script import CrawlScript

SPIDER_NAME = 'ZenSpider'
SETTINGS = {}


parser = argparse.ArgumentParser(description='run scrapy crawl command')
parser.add_argument('-spider', type=str, default=SPIDER_NAME,  help='name of spider in this project to crawl')
parser.add_argument('-s', type=str, action='append', metavar='', default=[],
                    help='update settings with kay-value pair')

args = parser.parse_args()


def get_build_in_type_from_str(value: str) -> Union[str, int, bool]:
    """Все значения, по[ожие на встроеные типы, возвращает как соответсвующий тип"""
    try:
        return int(value)
    except ValueError:
        return True if value == 'True' else False if value == 'False' else value


def _get_setting_from_args(settings: Iterable[str]) -> dict:
    res = {}
    for s in settings:
        k, v = s.split('=')
        res[k] = get_build_in_type_from_str(v)
    return res


if __name__ == '__main__':
    SPIDER_NAME = args.spider
    SETTINGS.update(_get_setting_from_args(args.s))
    crawler = CrawlScript()
    crawler.crawl(spider=SPIDER_NAME, settings=SETTINGS)

