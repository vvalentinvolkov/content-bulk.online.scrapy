import re

from itemloaders import ItemLoader
from itemloaders.processors import Compose, TakeFirst


class ZenLoader(ItemLoader):
    """Loader для статей из Zen -
    обрабатывает полчаемые <Selector> в каждом поле для загрузки в бд"""

    default_output_processor = TakeFirst()  # по умолчанию вощвращает str в неизменном виде

    def add_str_value(self, field_name: str, value: str, *processors, **kw):
        """ItemLoader.add_value() с проверкой типа для значения value"""
        assert isinstance(value, str), 'Spider должен отдавать в ZenLoader значение типа str'
        super().add_value(field_name, value, *processors, **kw)

    @staticmethod
    def _get_reads_or_views(s):
        try:
            number = float(re.search(r'[\d,]*', s)[1].replace(',', '.'))
            is_thousand = re.search(r'[\d,]*k|[\d,]*(\s|&nbsp;)тыс', s)
            if is_thousand is None:
                number *= 1000
            return int(number)
        except (ValueError, TypeError):
            return 0

    # @staticmethod
    # def _get_read_time(s):
    #     try:
    #         date_s = s.split('&nbsp;')
    #         if is_minutes is None:
    #             number *= 60
    #         return int(number)
    #     except (ValueError, TypeError):
    #         return 0

    @staticmethod
    def _get_subscribers(s):
        try:
            number = re.match(r'\d+(\s|&nbsp;)*\d*', s)[1].replace(' ', '').replace('&nbsp;', '')
            return int(number)
        except (ValueError, TypeError):
            return 0

    # @staticmethod
    # def _get_public_date(s):
    #     try:
    #         day = re.match(r'\d{1,2}\s', s)[1]
    #         month =
    #         return int(number)
    #     except (ValueError, TypeError):
    #         return 0

    # source_out = Compose(lambda v: v)
    # title_out = Compose(lambda v: v)
    # url_out = Compose(lambda v: v)

    reads_out = Compose(lambda v: v)
    visitors_out = Compose(lambda v: v)
    read_time_out = Compose(lambda v: v)
    subscribers_out = Compose(lambda v: v)

    likes_out = Compose(lambda v: v)
    comments_out = Compose(lambda v: v)

    parsing_date_out = Compose(lambda v: v)
    public_date_out = Compose(lambda v: v)

    length_out = Compose(lambda v: v)
    num_images_out = Compose(lambda v: v)
