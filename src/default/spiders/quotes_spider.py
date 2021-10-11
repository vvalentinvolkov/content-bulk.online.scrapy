import scrapy
# TODO: Выбрать нужную инфу со страницы

class QuotesSpider(scrapy.Spider):
    name = 'quotes'

    def start_requests(self):
        urls = [
            'https://zen.yandex.ru/media/eda_bez_povoda/gustoi-i-navaristyi-sup-mashhurda-dlia-vkusnogo-obeda-6160a9c838058f32816d0f7e',
            'https://zen.yandex.ru/media/eda_bez_povoda/profitroli-s-tvorojnym-kremom-legkii-desert-ponravitsia-ne-tolko-detiam-no-i-vzroslym-615f51b631f18d0e59891fe3'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split('/')[-1]
        filename = f'quotes - {page[:10]}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')