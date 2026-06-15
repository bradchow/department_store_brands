import scrapy
import json
import logging
import os


class QSquareSpider(scrapy.Spider):

    logfile_path = "QSquareSpider.log"
    if os.path.exists(logfile_path):
        os.remove(logfile_path)
    logging.basicConfig(filename=logfile_path, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    name = "QSquare"
    OUTPUT_TO_MD = 1
    OUTPUT_TO_JSON = 1

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': None,
        },
        'DOWNLOAD_DELAY': 0.5,
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        },
    }

    MALL_NAME = "京站時尚廣場"
    BASE_URL = "https://www.qsquare.com.tw/m"
    FLOORS = ["4F", "3F", "2F", "1F", "B1", "B2", "B3", "R10"]

    data = {}

    def start_requests(self):
        for floor in self.FLOORS:
            url = f"{self.BASE_URL}/floor.php?lv01_type={floor}"
            yield scrapy.Request(url, callback=self.parse, cb_kwargs={"floor": floor})

    def parse(self, response, floor):
        for a in response.xpath('//a[.//h3]'):
            brand_name = a.xpath('.//h3/text()').get('').strip()
            href = a.xpath('./@href').get('')
            if brand_name and href and ('detail.php' in href):
                full_url = f"{self.BASE_URL}/{href}"
                self.update_data(brand_name, self.MALL_NAME, floor, full_url)
                logging.info(f"{brand_name} @ {self.MALL_NAME} {floor}")

    def update_data(self, brand_name, mall, floor, url):
        if brand_name not in self.data:
            self.data[brand_name] = []
        location = {"mall": mall, "floor": floor, "url": url}
        if location not in self.data[brand_name]:
            self.data[brand_name].append(location)

    def closed(self, reason):
        sorted_data = dict(sorted(self.data.items()))
        if self.OUTPUT_TO_MD:
            md_lines = []
            for key, entries in sorted_data.items():
                md_lines.append(key + "  ")
                for item in entries:
                    md_lines.append(f"[{item['mall']} {item['floor']}]({item['url']})  ")
            with open('qsquare.md', 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_lines) + '\n')
        if self.OUTPUT_TO_JSON:
            with open('json/qsquare.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(sorted_data, ensure_ascii=False))
        print(f"\nDone. {len(sorted_data)} brands.")
