from typing import Any
import scrapy
import json

from scrapy.http import Response

from spider_settings import TARGET_COUNT, START_URL, API_URL, API_PAYLOAD


class SmartphonesSpider(scrapy.Spider):
    next_page = ''
    product_urls = set()
    bad_tag_list = ['batareya', 'podstavka', 'stiker']
    os_keywords = ['AndroidVersion', 'iOSVer']
    os_list = []

    name = 'smartphones'
    start_urls = START_URL

    def start_requests(self):
        url = self.start_urls

        yield scrapy.Request(
            url=url,
            callback=self.parse,
        )

    def parse(self, response: Response, **kwargs: Any) -> Any:
        urls = response.css('a.tile-hover-target::attr(href)').getall()
        nav_pages = response.css('a.b239-a0::attr(href)').getall()
        for url in nav_pages:
            if 'page' in url:
                self.next_page = url

        for url in urls:
            if len(self.product_urls) < TARGET_COUNT:
                self.url_validator(url)

        if len(self.product_urls) < TARGET_COUNT:
            yield response.follow(
                url=self.next_page,
                callback=self.parse,
            )

        for product in self.product_urls:
            yield response.follow(
                url=f'{API_URL}{product}{API_PAYLOAD}',
                callback=self.get_os_version,
            )

    def url_validator(self, url):
        '''
            Отбраковка неподходящих под категорию ссылок
        '''
        bad = False
        if '-smartfon-' in url:
            for tag in self.bad_tag_list:
                if tag in url:
                    bad = True
            if bad is False:
                self.product_urls.add(url)

    def get_os_version(self, response):
        '''
            Парсинг JSON-ответа API.
            Позволяет извлечь блоки, предположительно содержащие информацю об ОС
            и далее, с помощью метода get_os_info, получить более детальную информацию
            или убедиться в её отсутствии.
        '''
        all_characteristics = []
        short_characteristics = []

        json_response = json.loads(response.css('pre::text').get())
        result = json_response['widgetStates']
        for key, value in result.items():
            if 'webCharacteristics' in key:
                all_characteristics = json.loads(value).get('characteristics')

        for _ in all_characteristics:
            title = _.get('title')
            if title == 'Общие':
                short_characteristics = _.get('short')

        os = self.get_os_info(short_characteristics, 'OSWithoutVer')
        version = None
        if os:
            for _ in self.os_keywords:
                result = self.get_os_info(short_characteristics, _)
                if result is not None:
                    version = result
        if os and version is None:
            self.os_list.append(f'{os}')

    def get_os_info(self, characteristics_list, key_to_search):
        '''
            На основании переданного списка и ключа поиска позволяет получить данные о типе и версии ОС
            или убедиться в их отсутствии
        '''
        os_type_list = ['Android', 'iOS']

        keys_list = []

        for _ in characteristics_list:
            key = _.get('key')
            keys_list.append(key)
            if key_to_search in key:
                value = _.get('values')[0].get('text')
                if value == 'Другая':
                    self.os_list.append('Other')
                elif value in os_type_list:
                    return value
                for os in os_type_list:
                    if os in value:
                        self.os_list.append(value[0:10])
                        return value
        if (key_to_search == 'OSWithoutVer') and (key_to_search not in keys_list):
            self.os_list.append('OS is not specified')
