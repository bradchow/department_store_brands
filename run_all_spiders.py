#!/usr/bin/env python3
"""
依序執行所有百貨公司爬蟲，驗證輸出 JSON，最後執行 merge_json.py
"""

import subprocess
import json
import os
import sys
import time

SCRAPY_DIR = os.path.join(os.path.dirname(__file__), "department_store_brands")
JSON_DIR = os.path.join(SCRAPY_DIR, "json")
MERGE_SCRIPT = os.path.join(JSON_DIR, "merge_json.py")

SPIDERS = [
    {"name": "breeze",              "output": "breeze.json",              "min_brands": 100},
    {"name": "FEDS",                "output": "FEDS.json",                "min_brands": 50},
    {"name": "Sogo",                "output": "sogo.json",                "min_brands": 100},
    {"name": "ShinKongMitsukoshi",  "output": "ShinKongMitsukoshi.json",  "min_brands": 100},
    {"name": "UniUStyle",           "output": "UniUStyle.json",           "min_brands": 50},
    {"name": "TAIPEI101",           "output": "TAIPEI101.json",           "min_brands": 50},
]

def log(msg):
    print(f"\n{'='*60}")
    print(msg)
    print('='*60)

def run_spider(spider_name):
    log(f"執行爬蟲：{spider_name}")
    start = time.time()
    result = subprocess.run(
        ["scrapy", "crawl", spider_name],
        cwd=SCRAPY_DIR,
        capture_output=False,
    )
    elapsed = time.time() - start
    print(f"\n耗時：{elapsed:.1f} 秒")
    return result.returncode == 0

def validate_json(spider_info):
    json_path = os.path.join(JSON_DIR, spider_info["output"])
    name = spider_info["name"]
    min_brands = spider_info["min_brands"]

    # 檔案存在
    if not os.path.exists(json_path):
        print(f"  [FAIL] {name}：找不到 {json_path}")
        return False

    # 檔案大小
    size = os.path.getsize(json_path)
    if size == 0:
        print(f"  [FAIL] {name}：檔案是空的")
        return False

    # 可以解析 JSON
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  [FAIL] {name}：JSON 解析失敗 - {e}")
        return False

    # 是 dict
    if not isinstance(data, dict):
        print(f"  [FAIL] {name}：JSON 根節點不是 dict")
        return False

    # 品牌數量
    brand_count = len(data)
    if brand_count < min_brands:
        print(f"  [FAIL] {name}：品牌數量 {brand_count} 低於最小值 {min_brands}")
        return False

    # 每個品牌的 entry 格式
    errors = []
    for brand, entries in data.items():
        if not isinstance(entries, list) or len(entries) == 0:
            errors.append(f"品牌「{brand}」的 entries 不是非空 list")
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append(f"品牌「{brand}」有非 dict entry")
                break
            missing = [k for k in ("mall", "floor", "url") if k not in entry]
            if missing:
                errors.append(f"品牌「{brand}」缺少欄位：{missing}")
                break
        if len(errors) >= 5:
            break

    if errors:
        print(f"  [FAIL] {name}：資料格式錯誤")
        for e in errors:
            print(f"    - {e}")
        return False

    print(f"  [OK] {name}：{brand_count} 個品牌，檔案大小 {size:,} bytes")
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
        success = run_spider(spider_info["name"])
        if not success:
            print(f"  [WARN] {spider_info['name']} 爬蟲回傳非零 exit code，繼續驗證...")

        # 驗證輸出
        log(f"驗證：{spider_info['name']}")
        if not validate_json(spider_info):
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
