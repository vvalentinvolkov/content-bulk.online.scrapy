import logging

import mongoengine
from mongoengine import ConnectionFailure
from scrapy import signals
from scrapy.exceptions import CloseSpider

logger = logging.getLogger(__name__)


def setup_db(crawler):
    crawler.signals.connect(db_connect, signal=signals.spider_opened)
    crawler.signals.connect(db_disconnect, signal=signals.spider_closed)


def db_connect(spider):
    """Подключение к MongoDb через mongoengine - при ConnectionFailure подымает CloseSpider"""
    host = spider.crawler.settings.get('DB_HOST')
    port = spider.crawler.settings.get('DB_PORT')
    db = spider.crawler.settings.get('DB_NAME')
    try:
        client = mongoengine.connect(db=db, host=host, port=port)
        client.admin.command('ping')
        logger.info(f"Connect to {db} database")
    except ConnectionFailure:
        try:
            client = mongoengine.get_connection()
            client.admin.command('ping')
            logger.info(f"Connect to {db} database (created before)")
        except ConnectionFailure:
            logger.error(f'MongoDb is not available')
            raise CloseSpider


def db_disconnect(spider, reason):
    logging.info(f'Mongoengine - disconnect(alias=default)')
    mongoengine.disconnect()


    