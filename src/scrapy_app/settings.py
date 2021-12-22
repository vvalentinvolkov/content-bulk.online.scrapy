import os

#Database
DB_HOST = os.environ.get('DB_HOST', default='localhost')
DB_PORT = int(os.environ.get('DB_PORT', default=27017))
DB_NAME = os.environ.get('DB_NAME', default='default_articles')

LOG_FILE = 'src/scrapy_app/logs/ZenSpider.txt'
LOG_LEVEL = 'INFO'

SPIDER_MODULES = ['scrapy_app.spiders']
NEWSPIDER_MODULE = 'scrapy_app.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36.'

COOKIES_ENABLED = False
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 2

CLOSESPIDER_TIMEOUT = 300   # Ограничение по времени в секундах
# CLOSESPIDER_ITEMCOUNT = 3   # Ограничение по колличеству item вовзращенных из функций *_parse
# CLOSESPIDER_PAGECOUN = 300  # Ограничение по колличеству страниц
CLOSESPIDER_ERRORCOUNT = 5   # Ограничение по колличеству поднятых встроенных ошибок scrapy

SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 300,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

EXTENSIONS = {
    'scrapy.extensions.closespider.CloseSpider': 100,
    # 'scrapy.extensions.corestats.CoreStats': 200,
    # 'scrapy.extensions.logstats.LogStats': 300
}

ITEM_PIPELINES = {
    'src.scrapy_app.pipelines.MongoPipeline': 100,
}
