import scrapy
import json
import logging
import os


class EsliteSpider(scrapy.Spider):

    logfile_path = "EsliteSpider.log"
    if os.path.exists(logfile_path):
        os.remove(logfile_path)
    logging.basicConfig(filename=logfile_path, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    name = "Eslite"
    OUTPUT_TO_MD = 1
    OUTPUT_TO_JSON = 1

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2,
    }

    BASE_URL = "https://meet.eslite.com"
    AREA_ID = "e0a7c75a-7cbd-e711-a974-06d9a90704e1"

    TAIWAN_STORES = {
        "誠品美麗華店":                         "583a89dd-343a-4f0b-96df-9383984aba66",
        "誠品生活林口三井店":                   "bbed254f-507a-4598-a6ce-b31b7ed3edc1",
        "誠品書店南港中信園區限定店":           "af5be388-011e-f111-9a4b-00224818e9f2",
        "誠品桃園台茂店":                       "06f1b360-b908-439f-8319-5a1bb4e3f315",
        "誠品R79":                              "a0081859-25d1-4a7d-8e9b-1ea503a30380",
        "誠品生活南西":                         "5ed624cf-1696-e811-80c2-000d3a802aef",
        "誠品台北車站捷運店":                   "d3bb2f7f-158e-eb11-b566-00155db22d01",
        "誠品生活站前店":                       "28770895-4064-ef11-9c36-00224816323a",
        "誠品酒窖松菸門市":                     "da9fbd3a-45b5-f011-8194-000d3a85d154",
        "誠品生活武昌":                         "91253550-021d-45b2-88fd-e4ad8241629e",
        "誠品行旅":                             "3f37d8a5-20e1-ea11-a522-00155db5431c",
        "誠品生活松菸":                         "01401b81-1c63-4e62-bffa-474162268ddd",
        "誠品生活西門":                         "0ea488d8-5816-4162-9ee9-70b42763c619",
        "誠品生活捷運敦化店":                   "fa80156e-0d8c-ed11-9d7a-000d3a8066b5",
        "誠品酒窖新光三越Diamond Towers門市":   "d2138b42-2dba-f011-8194-000d3a85d154",
        "誠品酒窖安和門市":                     "6da03779-7af8-e811-9f2a-000d3a802a52",
        "誠品台大店":                           "4ffd2ced-a628-47fc-bb83-14ce47f1d388",
        "誠品生活新板":                         "6e18bb08-db39-4478-a7dc-a947a1dcbebf",
        "誠品生活板橋":                         "3997b90b-91b8-4762-b8f6-53bf2cd3e05f",
        "誠品雙和比漾店":                       "0d217d07-e4a7-4068-8d67-b73a3a7fe811",
        "誠品生活桃園統領店":                   "9342aa2c-59b2-e811-80c2-000d3a8034ab",
        "誠品生活新店":                         "43172393-e547-ee11-9937-000d3a815448",
        "誠品酒窖新店門市":                     "c2022f49-62b9-f011-8194-000d3a85d154",
        "誠品生活竹北遠百店":                   "09335e8b-3274-ec11-94f6-501ac587522b",
        "誠品新竹巨城店":                       "220bee3f-db43-4f7e-9484-739b5e24f5d1",
        "誠品宜蘭店":                           "c12cf3a9-8465-4b63-89d4-5dd82a8e5064",
        "誠品生活台中三井店":                   "b8d5b232-d9f9-e811-9f2a-000d3a802a52",
        "誠品生活台中大遠百店":                 "ac3dfafa-ab7e-4369-b73c-3fda6c584a60",
        "誠品生活480":                          "04e0e10f-186c-ee11-a535-0022481927f0",
        "誠品生活中友店":                       "938fef17-0aad-448e-826f-c9c5a8025a70",
        "誠品酒窖台中480門市":                  "e8bc263e-fd4e-eb11-a607-00155db22dd4",
        "誠品生活園道店":                       "b92729c9-8c01-4c1b-8d9f-dcbf0e534079",
        "誠品生活花蓮遠百店":                   "544ace3b-b45d-e811-80c2-000d3a803374",
        "誠品生活虎尾店":                       "98847151-c526-42ed-b921-c10b9eb6f53d",
        "誠品書店新港培桂堂限定店":             "da190be1-28b4-ee11-b660-0022481920f4",
        "誠品書店嘉義市立美術館限定店":         "b08696a5-1b62-eb11-988a-00155db22a9d",
        "誠品酒窖台南門市":                     "c6c984a2-d6ba-f011-8194-000d3a85d154",
        "誠品生活南紡店":                       "0280e32a-7c8b-4c8a-a440-3779f327f093",
        "誠品生活台南":                         "be4b6f29-20e9-ef11-90cb-002248169423",
        "誠品書店屏東總圖限定店":               "cbb07283-a528-eb11-9fb4-00155db22f67",
        "誠品生活屏東店":                       "857a2a34-6940-41e5-9d01-b0e73bd2d18f",
        "誠品生活義享店":                       "c5672c44-1559-ee11-9937-002248192ed9",
        "誠品書店衛武營限定店":                 "0dac2289-3d8f-ed11-9d7a-000d3a8066b5",
        "誠品生活駁二":                         "3be5cbfb-d844-4c90-8a71-5e05f1c013ed",
        "誠品生活高雄大遠百店":                 "159d1da0-f51c-4008-b8cc-9f9f294e25b7",
        "誠品書店東港王船限定店":               "1b1c5ccd-d1b6-ef11-88f8-002248ed2547",
        "誠品書店恆春限定店":                   "bf8fea92-a8be-f011-8194-000d3a85d154",
    }

    data = {}  # {brand_name: [{mall, floor, url}]}

    def start_requests(self):
        for store_name, store_uuid in self.TAIWAN_STORES.items():
            url = (f"{self.BASE_URL}/tw/tc/cooperationbrand"
                   f"?area={self.AREA_ID}&store={store_uuid}")
            yield scrapy.Request(
                url=url,
                callback=self.parse_first_page,
                cb_kwargs={'store_name': store_name, 'store_uuid': store_uuid},
            )

    def parse_first_page(self, response, store_name, store_uuid):
        total_pages = int(
            response.css('ul.content-list::attr(data-pagecount)').get('1') or '1'
        )
        for page in range(2, total_pages + 1):
            url = (f"{self.BASE_URL}/tw/tc/cooperationbrand"
                   f"?area={self.AREA_ID}&store={store_uuid}&page={page}")
            yield scrapy.Request(
                url=url,
                callback=self.parse_page,
                cb_kwargs={'store_name': store_name},
            )
        yield from self.parse_page(response, store_name=store_name)

    def parse_page(self, response, store_name):
        for item in response.css('ul.content-list > li'):
            brand_name = item.css('p::text').get('').strip()
            brand_path = item.css('a.img::attr(href)').get('')
            if not brand_name or not brand_path:
                continue
            brand_url = self.BASE_URL + brand_path
            yield scrapy.Request(
                url=brand_url,
                callback=self.parse_brand,
                cb_kwargs={'brand_name': brand_name, 'brand_url': brand_url},
            )

    def parse_brand(self, response, brand_name, brand_url):
        for link in response.css('div.brand-store > ul > li > a'):
            text = link.css('::text').get('').strip()
            if ' - ' in text:
                parts = text.rsplit(' - ', 1)
                mall = parts[0].strip()
                floor = parts[1].strip()
            else:
                mall = text.strip()
                floor = ''
            if mall:
                self._add_entry(brand_name, mall, floor, brand_url)

    def _add_entry(self, brand_name, mall, floor, url):
        if not brand_name or not mall:
            return
        if brand_name not in self.data:
            self.data[brand_name] = []
        entry = {"mall": mall, "floor": floor, "url": url}
        if entry not in self.data[brand_name]:
            self.data[brand_name].append(entry)
            logging.info(f"{brand_name} @ {mall}")

    def closed(self, reason):
        sorted_data = dict(sorted(self.data.items()))
        if self.OUTPUT_TO_MD:
            md_lines = []
            for key, entries in sorted_data.items():
                md_lines.append(key + "  ")
                for item in entries:
                    md_lines.append(f"[{item['mall']} {item['floor']}]({item['url']})  ")
            with open('eslite.md', 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_lines) + '\n')
        if self.OUTPUT_TO_JSON:
            with open('json/Eslite.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(sorted_data, ensure_ascii=False))
        print(f"\nDone. {len(sorted_data)} brands across {len(self.TAIWAN_STORES)} stores.")
