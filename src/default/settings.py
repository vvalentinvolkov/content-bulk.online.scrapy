#MongoDB

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DEFAULT_MONGO_DB_NAME = 'scrapy'
DEFAULT_MONGO_COLLECTION_NAME = 'articles'


SPIDER_MODULES = ['default.spiders']
NEWSPIDER_MODULE = 'default.spiders'

FAKEUSERAGENT_PROVIDERS = [
    'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
    'scrapy_fake_useragent.providers.FakerProvider',  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
    'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
]
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'

ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1

SPIDER_MIDDLEWARES = {
   'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
   'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
   'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
   'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

EXTENSIONS = {
   'scrapy.extensions.closespider.CloseSpider': 100
}

CLOSESPIDER_ITEMCOUNT = 20   # Ограничение по колличеству item вовзращенных из функций *_parse
CLOSESPIDER_ERRORCOUNT = 10   # Ограничение по колличеству поднятых встроенных ошибок scrapy

ITEM_PIPELINES = {
   'default.pipelines.MongoPipeline': 100,
}
