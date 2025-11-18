import time
import scrapy
import pprint
from urllib.parse import urlparse, urlunparse
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
import json
import logging
import os

class BreezeSpider(scrapy.Spider):
    
    logfile_path = "breezeSpider.log"
    if os.path.exists(logfile_path):
        os.remove(logfile_path)
    logging.basicConfig(filename=logfile_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    name = "breeze"
    prefix_brand_url = "https://www.breeze.com.tw/stores/"

    #output to .md format and it can be pasted on github
    OUTPUT_TO_MD = 1

    #output to json format
    OUTPUT_TO_JSON = 1

    DEBUG = 0

    search_strings = {
        "001": "微風廣場",
        "003": "微風台北車站",
        "005": "微風南京",
        "006": "微風台大醫院商場",
        "007": "微風松高",
        "009": "微風信義",
        "011": "微風中研院店",
        "012": "微風南山",
        "014": "微風東岸",
    }
    success_num = 0

    urls = [
        #Breeze Center
        'https://www.breezecenter.com/branches/001',
        #Breeze Taipei Station
        'https://www.breezecenter.com/branches/003',
        #Breeze NAN JING
        'https://www.breezecenter.com/branches/005',
        #Breeze NTU Hospital
        'https://www.breezecenter.com/branches/006',
        #Breeze Song Gao
        'https://www.breezecenter.com/branches/007',
        #Breeze Xin Yi
        'https://www.breezecenter.com/branches/009',
        #Breeze Academia Sinica
        'https://www.breezecenter.com/branches/011',
        #Breeze Nan Shan
        'https://www.breezecenter.com/branches/012',
        #EAST COAST by BREEZE
        'https://www.breezecenter.com/branches/014',
    ]
    urls_num = 0
    curr_url_num = 0
    data = {}

    def start_requests(self):
        self.urls_num = len(self.urls)
        if self.DEBUG == 1:
            print(f"total urls: {self.urls_num}")
            print(f"urls: {self.urls_num}")

        yield SeleniumRequest(url=self.urls[self.curr_url_num], callback=self.parse, meta={'retry': 100})
 
    def parse(self, response):        
        parsed_url = urlparse(response.url)
        for search_str, display_str in self.search_strings.items():
            if search_str in response.url:
                if self.DEBUG == 1:        
                    print(f"display_str: {display_str}")
                    print(f"search_str: {search_str}")
                break    
        domain = parsed_url.scheme + "://" + parsed_url.netloc 
        if self.DEBUG == 1:
            print(f"Parse for: {parsed_url}")
            print(f"domain: {domain}")

        #print(f"response.text from parse(): {response.text}")

        script_data = response.css('#\_\_NEXT\_DATA\_\_::text').get()

        if script_data:
            next_data = json.loads(script_data)

            floors_list = next_data.get('props', {}).get('pageProps', {}).get('initialState', {}).get('branch', {}).get('data', {}).get('floors', {})
            if floors_list:
                if self.DEBUG == 1:
                    print(f"floors_list: {len(floors_list)} levels。")

                for item in floors_list:
                    floor_name = item.get('floor_name')
                    branch_shops = item.get('branch_shops', [])
                    for shop in branch_shops:
                        brand_name = shop.get('shop_name')
                        identifier = shop.get('id')
                        brand_url = self.prefix_brand_url + (str)(identifier)
                        if self.DEBUG == 1:
                            print(brand_name + " " + display_str + " " + floor_name + " " + brand_url + " ")
                        self.update_data(brand_name=brand_name, mall=display_str, floor=floor_name, url=brand_url)
        else:
            print("can not find __NEXT_DATA__ on <script>")        

        self.curr_url_num += 1

        if self.curr_url_num < self.urls_num:
            yield SeleniumRequest(url=self.urls[self.curr_url_num], callback=self.parse, meta={'retry': 100})
        else:
            if self.OUTPUT_TO_MD == 0:
                print("All brands(" + (str)(self.urls_num) + ") parsed done") 

    def write_to_file(self, words):
        with open("logging.log", "a") as f:
            f.write(words)

    def update_data(self, brand_name, mall, floor, url):
        brand_name = brand_name.strip()
        if brand_name not in self.data:
            self.data[brand_name] = []

        location = {
            "mall": mall,
            "floor": floor,
            "url": url
        }

        self.data[brand_name].append(location)

    def closed(self, reason):
        #print("closed() is called")
        sorted_data = sorted(self.data.keys())
        for key in sorted_data:
            #print(key + " " + " ")
            data = self.data[key]
            for item in data:
                if isinstance(item, dict):
                    print(f"[{item['mall']} {item['floor']}]({item['url']})" + " " + " ")
        if self.OUTPUT_TO_JSON == 1:
            sorted_dict = {key: self.data[key] for key in sorted_data}
            json_data = json.dumps(sorted_dict, ensure_ascii=False)
            with open('json/breeze.json', 'w', encoding='utf-8') as file:
                file.write(json_data)