from mongoengine import QuerySet
from pandas import DataFrame


class ConvertibleQuerySet(QuerySet):
    """Расширение класса QuerySet методами конвертации"""

    def to_data_frame(self) -> DataFrame:
        """Возвращает DataFrame с колонками-полями"""
        fields = self._loaded_fields.fields
        return DataFrame(data=self.scalar(*fields), columns=fields)

    def to_excel(self, path) -> str:
        self.to_data_frame().to_excel('./')
        return path

    def to_html(self) -> str:
        return self.to_data_frame().to_html()

