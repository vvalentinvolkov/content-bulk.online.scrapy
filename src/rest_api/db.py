import logging

from mongoengine import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError

from src.db_services import db_services

logger = logging.getLogger(__name__)


def db_connect(db: str, host: str, port: int):
    """Подключение к MongoDb через mongoengine - при ConnectionFailure подымает CloseSpider"""
    try:
        db_services.mongo_connect(db=db, host=host, port=port)
        logger.info(f"Connect to {db} database")
    except (ConnectionFailure, ServerSelectionTimeoutError):
        logger.error(f'MongoDb is not available')
        raise ConnectionFailure
