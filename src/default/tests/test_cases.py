"""This module contains the base test cases for the ``scrapy_selenium`` package"""

from shutil import which
import unittest

import scrapy


class BaseScrapySeleniumTestCase(unittest.TestCase):
    """Base test case for the ``scrapy-selenium`` package"""
    class SimpleSpider(scrapy.Spider):
        name = 'simple_spider'
        allowed_domains = ['python.org']
        start_urls = ['http://python.org']

        def parse(self, response):
            pass

    @classmethod
    def setUpClass(cls):
        """Create a scrapy process and a spider class to use in the tests"""
        print('smth')
        cls.settings = {
            'SELENIUM_DRIVER_NAME': 'chrome',
            'SELENIUM_DRIVER_EXECUTABLE_PATH': which('chromedriver'),
            # 'SELENIUM_DRIVER_ARGUMENTS': ['-headless']
        }
        cls.spider_klass = cls.SimpleSpider


if __name__ == "__main__":
    unittest.main()
