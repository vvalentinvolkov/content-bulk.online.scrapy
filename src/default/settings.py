#MongoDB
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DEFAULT_MONGO_DB_NAME = 'scrapy'
DEFAULT_MONGO_COLLECTION_NAME = 'articles'

# Selenium
from shutil import which
import logging
from selenium.webdriver.remote.remote_connection import LOGGER

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('chromedriver')
SELENIUM_DRIVER_ARGUMENTS = ['-headless']
LOGGER.setLevel(logging.WARNING)

BOT_NAME = 'default'

SPIDER_MODULES = ['default.spiders']
NEWSPIDER_MODULE = 'default.spiders'

#USER_AGENT = 'default (+http://www.yourdomain.com)'

ROBOTSTXT_OBEY = True

#CONCURRENT_REQUESTS = 32

DOWNLOAD_DELAY = 3
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

#COOKIES_ENABLED = False
#TELNETCONSOLE_ENABLED = False

#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

SPIDER_MIDDLEWARES = {
   'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
   'scrapy_selenium.SeleniumMiddleware': 800,
}

#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

ITEM_PIPELINES = {
   'default.pipelines.MongoPipeline': 100,
}

#AUTOTHROTTLE_ENABLED = True
#AUTOTHROTTLE_START_DELAY = 5
#AUTOTHROTTLE_MAX_DELAY = 60
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
#AUTOTHROTTLE_DEBUG = False

#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
