import logging

from flask import current_app
from mongoengine import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError

from src.services import db_services

logger = logging.getLogger(__name__)


def init_db():
    """Вызывает db_connection c app.config.DB_NAME DB_HOST DB_PORT
    Если TESTING = True - подключаеться к мок бд"""
    db = current_app.config['DB_NAME']
    host = current_app.config['DB_HOST']
    port = current_app.config['DB_PORT']
    if current_app.config['TESTING']:
        db_services.mongo_mock_connect()
    else:
        db_connect(db=db, host=host, port=port)


def db_connect(db: str, host: str, port: int):
    """Подключение к MongoDb через mongoengine"""
    try:
        db_services.mongo_connect(db=db, host=host, port=port)
        logger.info(f"Connect to {db} database")
    except (ConnectionFailure, ServerSelectionTimeoutError):
        logger.error(f'MongoDb is not available')
        raise ConnectionFailure
