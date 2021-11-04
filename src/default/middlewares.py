from scrapy import signals

from scrapy.exceptions import IgnoreRequest

# SHOULDBE: Оптимизация процеса не очень - каждый раз запрос в бд
#  и одна коллекция для каждого паука, хотя корневой url уникальный для каждого
#  и можно для каждого источника сделать свою коллекцию
# FIXME: Обработка исключения IgnoreRequest
class DuplicateFromDbMiddleware:
    """Фильтрует дупликаты, проверяя ссылку запроса по бд"""
    def process_request(self, request, spider):
        """Проверяет наличие документа с url запроса и подымает IgnoreRequest если находит
        работает по flag='dup_middleware_active'"""
        print('DownLoadmiddle')
        # if 'dup_middleware' in request.flags and spider.collection.find_one({'url': request.url}):
        #     print('DuplicateFromDbMiddleware - IgnoreRequest')
        #     raise IgnoreRequest
        return None
