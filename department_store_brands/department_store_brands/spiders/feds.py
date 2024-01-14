import time
import scrapy
import pprint
from urllib.parse import urlparse, urlunparse
from scrapy_selenium import SeleniumRequest
import json
import logging
import os

class FEDSSpider(scrapy.Spider):
    
    logfile_path = "FEDSSpider.log"
    if os.path.exists(logfile_path):
        os.remove(logfile_path)
    logging.basicConfig(filename=logfile_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    name = "FEDS"

    #output to .md format and it can be pasted on github
    OUTPUT_TO_MD = 1

    #output to json format
    OUTPUT_TO_JSON = 1

    DEBUG = 0

    search_strings = {
        "55": "遠百信義 A13",
        "50": "遠百板橋",
        "54": "Mega City 板橋大遠百",
        "40": "遠百桃園",
        "72": "遠百竹北",
        "42": "新竹大遠百",
        "53": "Top City 台中大遠百",
        "37": "遠百嘉義",
        "48": "台南大遠百 成功店",
        "34": "台南大遠百 公園店",
        "51": "高雄大遠百",
        "52": "遠百花蓮",
    }
    success_num = 0
    urls = [
        #遠百信義A13
        'https://www.feds.com.tw/tw/55/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #遠百板橋
        'https://www.feds.com.tw/tw/50/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #Mega City 板橋大遠百
        'https://www.feds.com.tw/tw/54/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #遠百桃園
        'https://www.feds.com.tw/tw/40/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #遠百竹北
        'https://www.feds.com.tw/tw/72/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #新竹大遠百
        'https://www.feds.com.tw/tw/42/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #Top City 台中大遠百
        'https://www.feds.com.tw/tw/53/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #遠百嘉義
        'https://www.feds.com.tw/tw/37/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #台南大遠百 成功店
        'https://www.feds.com.tw/tw/48/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #台南大遠百 公園店
        'https://www.feds.com.tw/tw/34/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #高雄大遠百
        'https://www.feds.com.tw/tw/51/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
        #遠百花蓮
        'https://www.feds.com.tw/tw/52/MallInfo?tab=floor&Source=Website&EntryPoint=info_floors',
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
                if self.OUTPUT_TO_MD == 0:
                    print (display_str)
                break
        domain = parsed_url.scheme + "://" + parsed_url.netloc 
        if self.DEBUG == 1:
            print(f"Parse for: {parsed_url}")
            print(f"domain: {domain}")

        counters_list = response.xpath('//ul[@class="counters-list b-text-left"]')

        for li_element in counters_list.xpath('li[@class="list"]'):
            href = li_element.xpath('a/@href').get()
            text = li_element.xpath('a/text()').get()
            tab_floor = li_element.xpath('a/@href').re_first(r'tab=floor-([^\&]+)')
            if self.DEBUG == 1:
                print(f'url: {domainn+href}, text: {text}, tab=floor: {tab_floor}')
            self.update_data(brand_name=text, mall=display_str, floor=tab_floor, url=domain+href)

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
            print(key + " " + " ")
            data = self.data[key]
            for item in data:
                if isinstance(item, dict):
                    print(f"[{item['mall']} {item['floor']}]({item['url']})" + " " + " ")
        if self.OUTPUT_TO_JSON == 1:
            sorted_dict = {key: self.data[key] for key in sorted_data}
            json_data = json.dumps(sorted_dict, ensure_ascii=False)
            with open('json/FEDS.json', 'w', encoding='utf-8') as file:
                file.write(json_data)