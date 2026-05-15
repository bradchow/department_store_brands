#!/usr/bin/env python3
"""update_readme.py – 將各百貨 .md 檔的內容同步更新到 README.md"""

from pathlib import Path

ROOT = Path(__file__).parent
README = ROOT / "README.md"
MD_DIR = ROOT / "department_store_brands"

SECTIONS = [
    ("## [新光三越",               MD_DIR / "shin.md"),
    ("## [Sogo",                   MD_DIR / "sogo.md"),
    ("## [遠東百貨",               MD_DIR / "FEDS.md"),
    ("## [台北101",                MD_DIR / "101.md"),
    ("## [微風Breeze",             MD_DIR / "breeze.md"),
    ("## [統一夢時代/DREAM_PLAZA", MD_DIR / "uni_ustyle.md"),
    ("## [誠品Eslite",             MD_DIR / "eslite.md"),
]

def find_header(lines, prefix):
    for i, line in enumerate(lines):
        if line.startswith(prefix):
            return i
    raise ValueError(f"Header not found: {prefix!r}")

def next_h2(lines, start):
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            return i
    return len(lines)

def main():
    lines = README.read_text(encoding="utf-8").splitlines(keepends=True)

    for prefix, md_path in reversed(SECTIONS):
        if not md_path.exists():
            print(f"  [SKIP] 找不到 {md_path.name}")
            continue
        header_idx = find_header(lines, prefix)
        end_idx = next_h2(lines, header_idx)
        new_content = md_path.read_text(encoding="utf-8").splitlines(keepends=True)
        lines[header_idx + 1 : end_idx] = new_content
        print(f"  [OK] {md_path.name} → README.md ({len(new_content)} 行)")

    README.write_text("".join(lines), encoding="utf-8")
    print(f"完成，README.md 共 {len(lines)} 行")

if __name__ == "__main__":
    main()
