import multiprocessing


wsgi_app = "wsgi:app"
# pythonpath = '/home/www/...' # Абсл. пути для sys.path, через запятую
bind = '127.0.0.1:8001'
workers = multiprocessing.cpu_count() * 2 + 1
limit_request_fields = 32000  # Ограничение колличества полей в HTTP head
limit_request_field_size = 0  # Ограничение размера HTTP head (0 - не огран.)
# raw_env = ["TESTING=True"]  # Переменные среды для запуска