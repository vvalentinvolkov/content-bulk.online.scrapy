import pymongo
from pymongo.errors import ConnectionFailure
from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.job import job_dir


class DbDupeFilter(RFPDupeFilter):
    """Расширение родного фильтра дубликатов - изночально содержет множество адресов из бд"""

    def __init__(self, path=None, debug=False, mongo_url=None):
        print('DbDupeFilter - __init__')
        client = pymongo.MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        try:
            client.admin.command('ping')
        except ConnectionFailure as e:
            print("Mongo not available:\n", e)
        else:
            self.mongo_db = client[kwargs['mongo_db']]
            if kwargs['col_name'] not in self.mongo_db.list_collection_names():
                self.collection = self.mongo_db.create_collection(kwargs['col_name'])
                # cmd = OrderedDict([('collMod', kwargs['col_name']),
                #                    ('validator', self.scheme)])
                # self.mongo_db.command(cmd)
            else:
                self.collection = self.mongo_db[kwargs['col_name']]
        super().__init__(path, debug)

    @classmethod
    def from_settings(cls, settings):
        print('DbDupeFilter - from_settings')
        mongo_url = f"mongodb://{settings.get('MONGO_URL')}/",
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls(job_dir(settings), debug, mongo_url)

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