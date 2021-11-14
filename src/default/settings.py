#MongoDB

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DEFAULT_MONGO_DB_NAME = 'scrapy'
DEFAULT_MONGO_COLLECTION_NAME = 'articles'


SPIDER_MODULES = ['default.spiders']
NEWSPIDER_MODULE = 'default.spiders'

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
# ROTATING_PROXY_LIST = [
#     'localhost:58200',
# ]
ROBOTSTXT_OBEY = False

#CONCURRENT_REQUESTS = 32

DOWNLOAD_DELAY = 1
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
   # 'scrapy_splash.SplashDeduplicateArgsMiddleware': 200,

}

DOWNLOADER_MIDDLEWARES = {
   # 'scrapy_splash.SplashCookiesMiddleware': 723,
   # 'scrapy_splash.SplashMiddleware': 725,
   'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,

}

EXTENSIONS = {
   'scrapy.extensions.closespider.CloseSpider': 100
}

CLOSESPIDER_ITEMCOUNT = 20
CLOSESPIDER_ERRORCOUNT = 10

ITEM_PIPELINES = {
   'default.pipelines.MongoPipeline': 100,
}

# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
#
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

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
