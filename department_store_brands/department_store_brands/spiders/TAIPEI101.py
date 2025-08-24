import requests
import re
import json

url = "https://ws.taipei-101.com.tw/api/v1/shopping/search?lang=zh-tw"
data = {}
response = requests.get(url)
json_data = response.json()
mall = "台北 101"
prefix_brand_url = "https://www.taipei-101.com.tw/tw/shopping/brandsearch/content/"
OUTPUT_TO_JSON = 1

def update_data(brand_name, mall, floor, url):
    if brand_name not in data:
        data[brand_name] = []

    location = {
        "mall": mall,
        "floor": floor,
        "url": url
    }

    data[brand_name].append(location)

for item in json_data:
    name = item["name"].strip()
    identifier = item["id"]
    floor = item["floor"]
    brand_url = prefix_brand_url + (str)(identifier)
    #print(name + " " + " ")
    if re.match(r'\d+F(,\d+F)*$', floor):
        multiple_floors = re.findall(r'\d+F', floor)
        for floor in multiple_floors:
            #print(f"[{mall} {floor}]({brand_url})  ")
            update_data(brand_name=name, mall=mall, floor=floor, url=brand_url)
    else:
        #print(f"[{mall} {floor}]({brand_url})  ")
        update_data(brand_name=name, mall=mall, floor=floor, url=brand_url)
    
sorted_data = sorted(data.keys())
for key in sorted_data:
    print(key + " " + " ")
    tmp_data = data[key]
    for item in tmp_data:
        if isinstance(item, dict):
            print(f"[{item['mall']} {item['floor']}]({item['url']})" + " " + " ")
if OUTPUT_TO_JSON == 1:
    sorted_dict = {key: data[key] for key in sorted_data}
    json_data = json.dumps(sorted_dict, ensure_ascii=False)
    with open('json/TAIPEI101.json', 'w', encoding='utf-8') as file:
        file.write(json_data)