import scrapy

class ShinKongMitsukoshiSpider(scrapy.Spider):
    name = "ShinKongMitsukoshi"
    original_url = "https://www.skm.com.tw/brand_list/?brand_capital=&brand_category=&query=&page="
    page_num = 1
    start_urls = [ original_url + (str)(page_num)  ]
    OUTPUT_TO_MD = 1
    
    def parse(self, response):
        if self.OUTPUT_TO_MD == 0:
            print("Parse for: " + response.url)

        brands_num = len(response.xpath('//div[@class="grid-container grid-lg-4 grid-md-3 grid-xxs-2"]/div'))
        if (brands_num > 0):
            infos = response.xpath('//div[@class="grid-container grid-lg-4 grid-md-3 grid-xxs-2"]/div')
            for info in infos:
                if self.OUTPUT_TO_MD == 0:
                    print(info.xpath('.//a/div/text()').get())
                if self.OUTPUT_TO_MD == 1:
                    print("[" + info.xpath('.//a/div/text()').get() + "](" + info.xpath('.//a/@href').get() + ")  ")
                if self.OUTPUT_TO_MD == 0:
                    print(info.xpath('.//a/@href').get())
                locations = info.xpath('.//div/ul/li')
                for location in locations:
                    if self.OUTPUT_TO_MD == 0:
                        print("	" + "location: " + (str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '').split('\xa0')))
                    if self.OUTPUT_TO_MD == 1:
                        print((str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '')) + " " + " ")
#                    print("	" + "location: " + (str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '').split('\xa0')[0]))
#                    print("	" + "floor: " + (str)(location.xpath('.//text()').get().replace('\n', '').replace('\t', '').replace(' ', '').split('\xa0')[1]))
            #Yield for next page
            self.page_num = self.page_num + 1
            url = self.original_url + (str)(self.page_num)
            yield scrapy.Request(url, callback=self.parse)
        else:
            if self.OUTPUT_TO_MD == 0:
                print("No brands at: " + (str)(response.url))
