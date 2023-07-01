import scrapy
import json
import pprint

class ShinKongMitsukoshiSpider(scrapy.Spider):
    name = "ShinKongMitsukoshi"
    original_url = "https://www.skm.com.tw/brand_list/?brand_capital=&brand_category=&query=&page="
    page_num = 1
    start_urls = [ original_url + (str)(page_num)  ]
    data = {}
    OUTPUT_TO_MD = 1
    PREFIX_MALL_NAME = "新光三越"

    #output to json format
    OUTPUT_TO_JSON = 0
    
    def parse(self, response):
        if self.OUTPUT_TO_MD == 0:
            print("Parse for: " + response.url)

        brands_num = len(response.xpath('//div[@class="grid-container grid-lg-4 grid-md-3 grid-xxs-2"]/div'))
        if (brands_num > 0):
            infos = response.xpath('//div[@class="grid-container grid-lg-4 grid-md-3 grid-xxs-2"]/div')
            for info in infos:
                brand_name = info.xpath('.//a/div/text()').get()
                url = info.xpath('.//a/@href').get()
                print("[" + brand_name + "](" + url + ")  ")
                locations = info.xpath('.//div/ul/li')
                for location in locations:
                    mall = self.PREFIX_MALL_NAME + (str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '').split('\xa0')[0])
                    floor = (str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '').split('\xa0')[1])
                    # print((str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '')) + " " + " ")
                    print(mall + " " + floor)
                    self.update_data(brand_name = brand_name, mall = mall, floor = floor, url = url)
            #Yield for next page
            self.page_num = self.page_num + 1
            url = self.original_url + (str)(self.page_num)
            yield scrapy.Request(url, callback=self.parse)
        else:
            if self.OUTPUT_TO_MD == 0:
                print("No brands at: " + (str)(response.url))

    def update_data(self, brand_name, mall, floor, url):
        if brand_name not in self.data:
            self.data[brand_name] = []
            self.data[brand_name].append(url)

        location = {
            "mall": mall,
            "floor": floor
        }

        self.data[brand_name].append(location)

    def closed(self, reason):
        sorted_data = sorted(self.data.keys())
        for key in sorted_data:
            if self.OUTPUT_TO_MD == 0:
                print(key)
                pprint.pprint(self.data[key])
            else:
                for item in data:
                    if isinstance(item, str):
                        print(f"[{key}]({item})" + " " + " ")
                    elif isinstance(item, dict):
                        print(f"{item['mall']} {item['floor']}" + " " + " ")
        sorted_dict = {key: self.data[key] for key in sorted_data}
        if self.OUTPUT_TO_JSON == 1:
            json_data = json.dumps(sorted_dict, ensure_ascii=False)
            with open('../json/ShinKongMitsukoshi.json', 'w', encoding='utf-8') as file:
                file.write(json_data)
