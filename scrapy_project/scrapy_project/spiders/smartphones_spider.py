import scrapy
import time

from selenium.webdriver.common.by import By

from services.selenium_services import selenium_webdriver
from spider_settings import TARGET_COUNT


class SmartphonesSpider(scrapy.Spider):
    smartphones = set()

    name = 'smartphones'
    start_urls = ["https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating",
                  'https://www.ozon.ru/category/smartfony-15502/?sorting=rating']

    def start_requests(self):
        driver = selenium_webdriver()
        driver.get(self.start_urls[1])
        time.sleep(5)

        while len(self.smartphones) < TARGET_COUNT:
            product_links = driver.find_elements(By.CLASS_NAME, 'tile-hover-target')
            time.sleep(5)

            yield self.parse(product_links)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.find_element(By.XPATH, '//*[contains(@class,"ep5 b239-a0")]').click()

            time.sleep(3)

        driver.close()
        driver.quit()

    def parse(self, response):
        for link in response:
            url = link.get_attribute('href')
            if '-smartfon-' in url and len(self.smartphones) < TARGET_COUNT:
                self.smartphones.add(url)

        print(len(self.smartphones))
