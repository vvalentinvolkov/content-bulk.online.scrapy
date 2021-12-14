import logging

import mongoengine
from mongoengine import ConnectionFailure
from scrapy import signals
from scrapy.exceptions import CloseSpider

logger = logging.getLogger(__name__)


def setup_db(crawler):
    host = crawler.settings.get('DB_HOST')
    port = crawler.settings.get('DB_PORT')
    db = crawler.settings.get('DB_NAME')

    def db_connect():
        """Подключение к MongoDb через mongoengine - при ConnectionFailure подымает CloseSpider"""
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

    def db_disconnect():
        logging.info(f'Mongoengine - disconnect(alias=default)')
        mongoengine.disconnect()

    crawler.connect(db_connect, signal=signals.spider_opened)
    crawler.connect(db_disconnect, signal=signals.spider_closed)
    