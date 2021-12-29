# MongoDB
import os

DB_HOST = os.environ.get('DB_HOST', default='localhost')
DB_PORT = int(os.environ.get('DB_PORT', default=27017))
DB_NAME = os.environ.get('DB_NAME', default='default_articles')

TESTING = os.environ.get('TESTING', default='False')    # Подключается к мок монго
BUNDLE_ERRORS = True
