import time
import scrapy
import pprint
from urllib.parse import urlparse, urlunparse
from scrapy_selenium import SeleniumRequest
import json
import logging
import os

class FEDSSpider(scrapy.Spider):
    
    logfile_path = "breezeSpider.log"
    if os.path.exists(logfile_path):
        os.remove(logfile_path)
    logging.basicConfig(filename=logfile_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    name = "breeze"

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

        yield SeleniumRequest(url=self.urls[self.curr_url_num], callback=self.parse, meta={'retry': 100})
 
    def parse(self, response):
        parsed_url = urlparse(response.url)
        for search_str, display_str in self.search_strings.items():
            if search_str in response.url:
                if self.DEBUG == 1:        
                    print (display_str)
                    print (search_str)
                break    
        domain = parsed_url.scheme + "://" + parsed_url.netloc 
        if self.DEBUG == 1:
            print(f"Parse for: {parsed_url}")
            print(f"domain: {domain}")

        divs = response.xpath("//div[contains(@class, 'mix') and contains(@class, 'identity') and contains(@class, 'show_detail')]")

        for index, div in enumerate(divs):
            # 提取 class 属性
            class_attr = div.xpath('./@class').get()

            # 查找并提取包含 floorX 的部分
            floor = next((cls for cls in class_attr.split() if cls.startswith('floor')), 'Unknown')
            floor_number = floor[5:] if floor != 'Unknown' else floor

            if self.DEBUG == 1:
                print(f"floor: {floor}")
                print(f"floor_number: {floor_number}")
            
            real_floor = self.get_actual_floor(floor_number=floor_number, mall_number=search_str)
            if real_floor:
                if self.DEBUG == 1:
                    print(f"real floor: {real_floor}")

            href = div.xpath('./parent::a/@href').get()
            if href:
                if self.DEBUG == 1:
                    print(f"Found href: {href}")

            title = div.xpath('./@title').get()

            # 特別的品牌縮寫會撞到別的品牌的處理
            if title == 'MK':
                title = 'MAISON KAYSER'

            if title:
                if self.DEBUG == 1:
                    print(f"Found title: {title}")

            self.update_data(brand_name=title, mall=display_str, floor=real_floor, url=href)

            self.curr_url_num += 1

            if self.curr_url_num < self.urls_num:
                yield SeleniumRequest(url=self.urls[self.curr_url_num], callback=self.parse, meta={'retry': 100})
            else:
                if self.OUTPUT_TO_MD == 0:
                    print("All brands(" + (str)(self.urls_num) + ") parsed done") 

    def get_actual_floor(self, floor_number, mall_number):
        if self.DEBUG == 1:
            print(f"get_actual_floor({floor_number}, {mall_number})")

        floor_mapping = {
            '001': {15: 'B2', 14: 'B1', 17: 'GF', 1: '1F', 2: '2F', 3: '3F', 8: '4F', 9: '5F', 10: '6F', 11: '7F', 12: '8F', 13: '9F'},
            '003': {14: 'B1', 1: '1F', 2: '2F'},
            '005': {15: 'B2', 14: 'B1', 1: '1F', 2: '2F', 3: '3F', 8: '4F'},
            '006': {14: 'B1'},
            '007': {15: 'B2', 14: 'B1', 1: '1F', 2: '2F', 3: '3F', 8: '4F'},
            '009': {16: 'B3', 14: 'B1', 1: '1F', 2: '2F', 3: '3F', 8: '4F', 4: '45F', 5: '46F', 6: '47F'},
            '011': {23: '1F'},
            '012': {15: 'B2', 14: 'B1', 1: '1F', 2: '2F', 3: '3F', 8: '4F', 9: '5F', 10: '6F', 11: '7F', 5: '46F', 6: '47F', 7: '48F'},
            '014': {1: '1F', 3: '3F', 25: 'RF'},
        }

        if mall_number in floor_mapping:
            actual_floor = floor_mapping[mall_number].get((int)(floor_number), None)
            if actual_floor:
                return actual_floor
            else:
                return "Invalid number for the given mall."
        else:
            return "Mall not found."

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
            print(key + " " + " ")
            data = self.data[key]
            for item in data:
                if isinstance(item, dict):
                    print(f"[{item['mall']} {item['floor']}]({item['url']})" + " " + " ")
        if self.OUTPUT_TO_JSON == 1:
            sorted_dict = {key: self.data[key] for key in sorted_data}
            json_data = json.dumps(sorted_dict, ensure_ascii=False)
            with open('json/breeze.json', 'w', encoding='utf-8') as file:
                file.write(json_data)