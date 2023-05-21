import scrapy
import os

class ShinKongMitsukoshiSpider(scrapy.Spider):
    name = "ShinKongMitsukoshi"
    original_url = "https://www.skm.com.tw/brand_list/?brand_capital=&brand_category=&query=&page="
    page_num = 1
    start_urls = [ original_url + (str)(page_num)  ]
    
    def parse(self, response):
        print("Parse for: " + response.url)

        content = ''
        content += '# 百貨公司品牌爬蟲\n'
        content += '透過台灣各大百貨公司官網，爬出裡面所有品牌及樓層\n'
        content += '## [新光三越](https://www.skm.com.tw/brand_list/?brand_capital=&brand_category=&query=&page=1)\n'

        brands_num = len(response.xpath('//div[@class="grid-container grid-lg-4 grid-md-3 grid-xxs-2"]/div'))
        if (brands_num > 0):
            infos = response.xpath('//div[@class="grid-container grid-lg-4 grid-md-3 grid-xxs-2"]/div')
            for info in infos:
                print(info.xpath('.//a/div/text()').get())
                content += "[" + info.xpath('.//a/div/text()').get() + "]"
                print(info.xpath('.//a/@href').get())
                content += "(" + info.xpath('.//a/@href').get() + ")\n"
                locations = info.xpath('.//div/ul/li')
                for location in locations:
                    print("	" + "location: " + (str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '').split('\xa0')))
                    content += (str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '')) + "\n"
#                    print("	" + "location: " + (str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '').split('\xa0')[0]))
#                    print("	" + "floor: " + (str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '').split('\xa0')[1]))
            #Yield for next page
            self.page_num = self.page_num + 1
            url = self.original_url + (str)(self.page_num)
            yield scrapy.Request(url, callback=self.parse)
        else:
            print("No brands at: " + (str)(response.url))
        
        content += '## 作者\n'
        content += '本項目由 [Brad Chou](https://github.com/bradchow) 開發\n'
        content += '## 授權\n'
        content += '本項目使用 [MIT 授權條款](./LICENSE.md) 進行授權\n'

        with open('README.md', 'a') as out:
            out.write(content)
