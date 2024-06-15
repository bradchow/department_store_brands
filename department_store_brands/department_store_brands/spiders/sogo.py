import time
import scrapy
import pprint
from urllib.parse import urlparse, urlunparse
from scrapy_selenium import SeleniumRequest
import json
import logging
import os

class SogoSpider(scrapy.Spider):
    
    logfile_path = "SogoSpider.log"
    if os.path.exists(logfile_path):
        os.remove(logfile_path)
    logging.basicConfig(filename=logfile_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    name = "Sogo"

    #output to .md format and it can be pasted on github
    OUTPUT_TO_MD = 1

    #output to json format
    OUTPUT_TO_JSON = 1

    search_strings = {
        "tp1": "SOGO 台北忠孝館",
	    "tp2": "SOGO 台北復興館",
        "tp3": "SOGO 台北敦化館",
        "tm": "SOGO 天母店",
        "zl": "SOGO 中壢店",
        "hcbc": "SOGO 新竹店",
        "ks": "SOGO 高雄店",
    }
    success_num = 0
    urls = [
        #台北忠孝館
        'https://info.sogo.com.tw/tp1/floors/B2',
        'https://info.sogo.com.tw/tp1/floors/B1',
        'https://info.sogo.com.tw/tp1/floors/1F',
        'https://info.sogo.com.tw/tp1/floors/2F',
        'https://info.sogo.com.tw/tp1/floors/3F',
        'https://info.sogo.com.tw/tp1/floors/4F',
        'https://info.sogo.com.tw/tp1/floors/5F',
        'https://info.sogo.com.tw/tp1/floors/6F',
        'https://info.sogo.com.tw/tp1/floors/7F',
        'https://info.sogo.com.tw/tp1/floors/8F',
        'https://info.sogo.com.tw/tp1/floors/9F',
        'https://info.sogo.com.tw/tp1/floors/10F',
        'https://info.sogo.com.tw/tp1/floors/11F',
        'https://info.sogo.com.tw/tp1/floors/12F',
        #台北復興館
        'https://info.sogo.com.tw/tp2/floors/B3',
        'https://info.sogo.com.tw/tp2/floors/B2',
        'https://info.sogo.com.tw/tp2/floors/B1',
        'https://info.sogo.com.tw/tp2/floors/1F',
        'https://info.sogo.com.tw/tp2/floors/2F',
        'https://info.sogo.com.tw/tp2/floors/3F',
        'https://info.sogo.com.tw/tp2/floors/4F',
        'https://info.sogo.com.tw/tp2/floors/5F',
        'https://info.sogo.com.tw/tp2/floors/6F',
        'https://info.sogo.com.tw/tp2/floors/7F',
        'https://info.sogo.com.tw/tp2/floors/8F',
        'https://info.sogo.com.tw/tp2/floors/9F',
        'https://info.sogo.com.tw/tp2/floors/10F',
        'https://info.sogo.com.tw/tp2/floors/11F',
        #台北敦化館
        'https://info.sogo.com.tw/tp3/floors/B2',
        'https://info.sogo.com.tw/tp3/floors/B1',
        'https://info.sogo.com.tw/tp3/floors/1F',
        'https://info.sogo.com.tw/tp3/floors/2F',
        'https://info.sogo.com.tw/tp3/floors/3F',
        'https://info.sogo.com.tw/tp3/floors/4F',
        'https://info.sogo.com.tw/tp3/floors/5F',
        'https://info.sogo.com.tw/tp3/floors/6F',
        'https://info.sogo.com.tw/tp3/floors/7F',
        #天母店
        'https://info.sogo.com.tw/tm/floors/B1',
        'https://info.sogo.com.tw/tm/floors/1F', 
        'https://info.sogo.com.tw/tm/floors/2F', 
        'https://info.sogo.com.tw/tm/floors/3F', 
        'https://info.sogo.com.tw/tm/floors/4F', 
        'https://info.sogo.com.tw/tm/floors/5F', 
        'https://info.sogo.com.tw/tm/floors/6F', 
        'https://info.sogo.com.tw/tm/floors/7F', 
        'https://info.sogo.com.tw/tm/floors/8F', 
        #中壢店
        'https://info.sogo.com.tw/zl/floors/B1',
        'https://info.sogo.com.tw/zl/floors/1F',
        'https://info.sogo.com.tw/zl/floors/2F',
        'https://info.sogo.com.tw/zl/floors/3F',
        'https://info.sogo.com.tw/zl/floors/4F',
        'https://info.sogo.com.tw/zl/floors/5F',
        'https://info.sogo.com.tw/zl/floors/6F',
        'https://info.sogo.com.tw/zl/floors/7F',
        'https://info.sogo.com.tw/zl/floors/8F',
        'https://info.sogo.com.tw/zl/floors/9F',
        'https://info.sogo.com.tw/zl/floors/10F',
        'https://info.sogo.com.tw/zl/floors/11F',
        #新竹店
        'https://info.sogo.com.tw/hcbc/floors/B1',
        'https://info.sogo.com.tw/hcbc/floors/1F',
        'https://info.sogo.com.tw/hcbc/floors/2F',
        'https://info.sogo.com.tw/hcbc/floors/3F',
        'https://info.sogo.com.tw/hcbc/floors/4F',
        'https://info.sogo.com.tw/hcbc/floors/5F',
        'https://info.sogo.com.tw/hcbc/floors/6F',
        #高雄店
        'https://info.sogo.com.tw/ks/floors/B2',
        'https://info.sogo.com.tw/ks/floors/B1',
        'https://info.sogo.com.tw/ks/floors/1F', 
        'https://info.sogo.com.tw/ks/floors/2F', 
        'https://info.sogo.com.tw/ks/floors/3F', 
        'https://info.sogo.com.tw/ks/floors/4F', 
        'https://info.sogo.com.tw/ks/floors/5F', 
        'https://info.sogo.com.tw/ks/floors/6F', 
        'https://info.sogo.com.tw/ks/floors/7F', 
        'https://info.sogo.com.tw/ks/floors/12F', 
        'https://info.sogo.com.tw/ks/floors/15F',
    ]
    urls_num = 0
    curr_url_num = 0
    data = {}

    def start_requests(self):
        self.urls_num = len(self.urls)
        if self.OUTPUT_TO_MD == 0:
            print("total urls: " + (str)(self.urls_num))

        yield SeleniumRequest(url=self.urls[self.curr_url_num], callback=self.parse, meta={'retry': 100})
 
    def parse(self, response):
        if self.OUTPUT_TO_MD == 0:
            print("Parse for: " + response.url)
        for search_str, display_str in self.search_strings.items():
            if search_str in response.url:
                if self.OUTPUT_TO_MD == 0:
                    print (display_str)
                break

        url_parts = response.url.split("/")
        floor = response.xpath('//div[@id="dk4-combobox"]/text()').get()
        logging.info(f"floor: {floor}")
        if self.OUTPUT_TO_MD == 0:
            print(floor)

        parsed_url = urlparse(response.url)
        domain = parsed_url.scheme + "://" + parsed_url.netloc 

        title_num = len(response.xpath('//div[@class="tab-content"]//a[@class="brandBox"]'))
        if self.OUTPUT_TO_MD == 0:
            print("title_num: " + (str)(title_num))
        if (title_num > 0):
            titles = response.xpath('//div[@class="tab-content"]//a[@class="brandBox"]')
            for title in titles:
                brand_name = title.xpath('.//span[@class="title"]/text()').get()
                if self.OUTPUT_TO_MD == 0:
                    print(brand_name)
                
                if brand_name != None:
                    url = title.xpath('.//@href').get()
                    target_url = (str)(domain) + (str)(url)
                    if self.OUTPUT_TO_MD == 0:
                        print(target_url)
                    self.update_data(brand_name=brand_name, mall=display_str, floor=floor, url=target_url)

            self.success_num += 1
            if self.OUTPUT_TO_MD == 0:
                print("success_num: " + (str)(self.success_num))
            
            self.curr_url_num += 1
            
            if self.curr_url_num < self.urls_num:
#            if self.curr_url_num < 1:
                yield SeleniumRequest(url=self.urls[self.curr_url_num], callback=self.parse, meta={'retry': 100})
            else:
                if self.OUTPUT_TO_MD == 0:
                    print("All brands(" + (str)(self.urls_num) + ") parsed done") 
            
        else:
            retry_count = response.meta.get('retry', 0)
            logging.info(f"retry_count: {retry_count}")
            if retry_count > 0:
                time.sleep(5)
                retry_count = retry_count - 1
                # dont_filter is set to True for allowing request the same url
                yield SeleniumRequest(url=response.url, callback=self.parse, meta={'retry': retry_count}, dont_filter=True)
            else:
                logging.error("[ERR] Element not found for: " + response.url)

    def write_to_file(self, words):
        with open("logging.log", "a") as f:
            f.write(words)

    def update_data(self, brand_name, mall, floor, url):
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
            with open('json/sogo.json', 'w', encoding='utf-8') as file:
                file.write(json_data)