import logging

import mongoengine
from mongoengine import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError
from scrapy import signals
from scrapy.exceptions import CloseSpider

from src.services import db_services

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
        db_services.mongo_connect(db=db, host=host, port=port)
        logger.info(f"Connect to {db} database")
    except (ConnectionFailure, ServerSelectionTimeoutError):
        logger.error(f'MongoDb is not available')
        raise CloseSpider


def db_disconnect(spider, reason):
    logging.info(f'Mongoengine - disconnect(alias=default)')
    mongoengine.disconnect()


    