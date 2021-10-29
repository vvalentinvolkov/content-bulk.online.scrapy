from scrapy.selector import Selector
import pytest
from scrapy.http.response import Response

class TestSelectors:
    """"""
    pass

def test_returning_type_of_selector():
    response = Response()
    p = '<p>Some text</p>'
    value = Selector(text=p).css('p::text').get()
    print(type(value))
    print(value)


if __name__ == '__main__':
    test_returning_type_of_selector()