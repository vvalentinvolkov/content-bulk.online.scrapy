import mongoengine
import pymongo
from pymongo.errors import ConnectionFailure
from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.job import job_dir
from .items import ZenArticle


class DbDupeFilter(RFPDupeFilter):
    """Расширение родного фильтра дубликатов - изночально содержет множество адресов из бд"""


    @classmethod
    def from_settings(cls, settings):
        collection = settings.get('DEFAULT_MONGO_COLLECTION_NAME')
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls(job_dir(settings), debug, collection)

    def request_seen(self, request):
        print('DbDupeFilter - request_seen')
        return False

    def open(self):  # can return deferred
        print('DbDupeFilter - open')
        pass

    def close(self, reason):  # can return a deferred
        print('DbDupeFilter - close')
        pass

    def log(self, request, spider):  # log that a request has been filtered
        print('DbDupeFilter - log')
        pass