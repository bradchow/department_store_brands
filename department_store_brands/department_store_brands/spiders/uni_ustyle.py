import scrapy
import json
import logging
import os
import re


class UniUStyleSpider(scrapy.Spider):

    logfile_path = "UniUStyleSpider.log"
    if os.path.exists(logfile_path):
        os.remove(logfile_path)
    logging.basicConfig(filename=logfile_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    name = "UniUStyle"

    OUTPUT_TO_MD = 1
    OUTPUT_TO_JSON = 1
    DEBUG = 0

    base_url = "https://www.uni-ustyle.com.tw/zh-tw/brand-floor"
    data = {}
    total_pages = None

    def start_requests(self):
        yield scrapy.Request(self.base_url, callback=self.parse)

    def parse(self, response):
        # 第一頁：擷取 CSRF token，解析總頁數，發出後續 POST 請求
        token = response.css('input[name="_token"]::attr(value)').get('')

        # 從 onclick 屬性解析頁碼（li 文字節點含空白，用 onclick 更可靠）
        page_numbers = [
            int(m)
            for onclick in response.css('.page ul li a::attr(onclick)').getall()
            for m in re.findall(r'advanced_search_page\((\d+)\)', onclick)
        ]
        self.total_pages = max(page_numbers) if page_numbers else 1

        if self.DEBUG == 1:
            print(f"total_pages: {self.total_pages}, token: {token[:10]}...")

        for page in range(2, self.total_pages + 1):
            yield scrapy.FormRequest(
                url=self.base_url,
                formdata={'_token': token, 'searcpage': str(page)},
                callback=self.parse_page,
                dont_filter=True,
                headers={'Referer': self.base_url}
            )

        self.parse_page(response)

    def parse_page(self, response):
        items = response.css('.litem')
        if self.DEBUG == 1:
            print(f"parse_page: {response.url}, items: {len(items)}")

        for item in items:
            brand_name = item.css('.subject > a::text').get()
            if not brand_name:
                continue

            brandstore = item.css('.brandstore::text').get()
            if not brandstore or '｜' not in brandstore:
                logging.warning(f"unexpected brandstore format: {brandstore}")
                continue

            parts = brandstore.split('｜', 1)
            mall = parts[0].strip()
            floor = parts[1].strip()

            url = item.css('a.itemlink::attr(href)').get()
            if not url:
                continue

            self.update_data(brand_name=brand_name, mall=mall, floor=floor, url=url)

    def update_data(self, brand_name, mall, floor, url):
        brand_name = brand_name.strip()
        if brand_name not in self.data:
            self.data[brand_name] = []
        self.data[brand_name].append({"mall": mall, "floor": floor, "url": url})

    def closed(self, reason):
        sorted_data = sorted(self.data.keys())
        for key in sorted_data:
            print(key + "  ")
            for item in self.data[key]:
                if isinstance(item, dict):
                    print(f"[{item['mall']} {item['floor']}]({item['url']})" + "  ")
        if self.OUTPUT_TO_JSON == 1:
            sorted_dict = {key: self.data[key] for key in sorted_data}
            with open('json/UniUStyle.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(sorted_dict, ensure_ascii=False))
