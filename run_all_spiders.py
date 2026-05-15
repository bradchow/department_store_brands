#!/usr/bin/env python3
"""
依序執行所有百貨公司爬蟲，驗證輸出 MD，最後執行 merge_json.py
"""

import subprocess
import json
import os
import re
import sys
import time

SCRAPY_DIR = os.path.join(os.path.dirname(__file__), "department_store_brands")
MD_DIR = SCRAPY_DIR
JSON_DIR = os.path.join(SCRAPY_DIR, "json")
MERGE_SCRIPT = os.path.join(JSON_DIR, "merge_json.py")

SPIDERS = [
    {"name": "breeze",             "output": "breeze.md",     "min_brands": 100},
    {"name": "FEDS",               "output": "FEDS.md",       "min_brands": 50},
    {"name": "Sogo",               "output": "sogo.md",       "min_brands": 100},
    {"name": "ShinKongMitsukoshi", "output": "shin.md",       "min_brands": 100},
    {"name": "UniUStyle",          "output": "uni_ustyle.md", "min_brands": 50},
    {"name": "TAIPEI101",          "output": "101.md",        "min_brands": 50,
     "script": "department_store_brands/spiders/TAIPEI101.py"},
    {"name": "Eslite",             "output": "eslite.md",     "min_brands": 100},
]

def log(msg):
    print(f"\n{'='*60}")
    print(msg)
    print('='*60)

def run_spider(spider_info):
    name = spider_info["name"]
    log(f"執行爬蟲：{name}")
    start = time.time()
    if "script" in spider_info:
        cmd = [sys.executable, spider_info["script"]]
    else:
        cmd = ["scrapy", "crawl", name]
    result = subprocess.run(cmd, cwd=SCRAPY_DIR, capture_output=False)
    elapsed = time.time() - start
    print(f"\n耗時：{elapsed:.1f} 秒")
    return result.returncode == 0

LINK_PATTERN = re.compile(r'^\[.+\]\(https?://.+\)')

def validate_md(spider_info):
    md_path = os.path.join(MD_DIR, spider_info["output"])
    name = spider_info["name"]
    min_brands = spider_info["min_brands"]

    # 檔案存在
    if not os.path.exists(md_path):
        print(f"  [FAIL] {name}：找不到 {md_path}")
        return False

    # 檔案大小
    size = os.path.getsize(md_path)
    if size == 0:
        print(f"  [FAIL] {name}：檔案是空的")
        return False

    with open(md_path, encoding="utf-8") as f:
        lines = [line.rstrip() for line in f if line.strip()]

    link_lines = [l for l in lines if LINK_PATTERN.match(l)]
    brand_lines = [l for l in lines if not LINK_PATTERN.match(l)]

    # 品牌數量
    brand_count = len(brand_lines)
    if brand_count < min_brands:
        print(f"  [FAIL] {name}：品牌數量 {brand_count} 低於最小值 {min_brands}")
        return False

    # 至少有一個連結
    if not link_lines:
        print(f"  [FAIL] {name}：找不到任何位置連結")
        return False

    print(f"  [OK] {name}：{brand_count} 個品牌，{len(link_lines)} 個位置，檔案大小 {size:,} bytes")
    return True

def run_merge():
    log("執行 merge_json.py")
    result = subprocess.run(
        [sys.executable, "merge_json.py"],
        cwd=JSON_DIR,
        capture_output=False,
    )
    return result.returncode == 0

def main():
    failed_spiders = []

    for spider_info in SPIDERS:
        # 執行爬蟲
        success = run_spider(spider_info)
        if not success:
            print(f"  [WARN] {spider_info['name']} 爬蟲回傳非零 exit code，繼續驗證...")

        # 驗證輸出
        log(f"驗證：{spider_info['name']}")
        if not validate_md(spider_info):
            failed_spiders.append(spider_info["name"])

    print(f"\n{'='*60}")
    print("爬蟲執行結果總結")
    print('='*60)

    if failed_spiders:
        print(f"[FAIL] 以下爬蟲驗證失敗：{', '.join(failed_spiders)}")
        print("請修正後重新執行，不執行 merge_json.py")
        sys.exit(1)

    print("[OK] 所有爬蟲驗證通過！")

    # 執行 merge
    if not run_merge():
        print("[FAIL] merge_json.py 執行失敗")
        sys.exit(1)

    merged_path = os.path.join(JSON_DIR, "merged_data.json")
    if os.path.exists(merged_path):
        size = os.path.getsize(merged_path)
        with open(merged_path, encoding="utf-8") as f:
            merged = json.load(f)
        brand_count = len(merged.get("brands", {}))
        print(f"\n[OK] merge_json.py 完成：{brand_count} 個品牌，{size:,} bytes → {merged_path}")
    else:
        print("[FAIL] merged_data.json 未產生")
        sys.exit(1)

if __name__ == "__main__":
    main()
