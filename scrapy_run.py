import argparse
from typing import Iterable, Union

from src.scrapy_app.crawl_script import CrawlScript

SPIDER_NAME = 'ZenSpider'
SETTINGS = {}


parser = argparse.ArgumentParser(description='''run scrapy crawl command
                                             available settings:
                                             LOG_FILE=scr/scrapy_app/logs/*.log
                                             LOG_LEVEL=INFO
                                             DOWNLOAD_DELAY=2
                                             CLOSESPIDER_TIMEOUT=300
                                             CLOSESPIDER_ITEMCOUNT=10
                                             CLOSESPIDER_PAGECOUN=50
                                             CLOSESPIDER_ERRORCOUNT=5''')
parser.add_argument('-spider', type=str, default=SPIDER_NAME,  help='name of spider in this project to crawl')
parser.add_argument('-s', type=str, action='append', metavar='', default=[],
                    help='update settings with kay-value pair')

args = parser.parse_args()


def _get_build_in_type_from_str(value: str) -> Union[str, int, bool, None]:
    """Все значения, похожие на встроеные типы, возвращает как соответсвующий тип"""
    try:
        return int(value)
    except ValueError:
        if value == 'True':
            return True
        if value == 'False':
            return False
        if value == 'None':
            return None
        return value


def _get_setting_from_args(settings: Iterable[str]) -> dict:
    res = {}
    for s in settings:
        k, v = s.split('=')
        res[k] = _get_build_in_type_from_str(v)
    return res


def run(spider: str, settings: dict):
    crawler_script = CrawlScript()
    crawler_script.crawl(spider=spider, settings=settings)


if __name__ == '__main__':
    SPIDER_NAME = args.spider
    SETTINGS.update(_get_setting_from_args(args.s))
    run(SPIDER_NAME, SETTINGS)
