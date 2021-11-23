import os

#Database
DB_HOST = os.environ.get('DB_HOST', default='localhost')
DB_PORT = int(os.environ.get('DB_PORT', default=27017))
DEFAULT_DB_NAME = 'articles'


SPIDER_MODULES = ['default.spiders']
NEWSPIDER_MODULE = 'default.spiders'

FAKEUSERAGENT_PROVIDERS = [
    'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
    'scrapy_fake_useragent.providers.FakerProvider',  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
    'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
]
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36.'

COOKIES_ENABLED = False
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 2

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

CLOSESPIDER_ITEMCOUNT = 3   # Ограничение по колличеству item вовзращенных из функций *_parse
CLOSESPIDER_ERRORCOUNT = 10   # Ограничение по колличеству поднятых встроенных ошибок scrapy

ITEM_PIPELINES = {
   'default.pipelines.MongoPipeline': 100,
}
