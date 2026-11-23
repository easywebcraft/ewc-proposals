#!/usr/bin/env python3
"""「更新が○年前まで」の所見を、相手の今のサイトで確かめ直す（2026-11-23）。

    python3 yearcheck.py keys_urls.tsv > yearcheck.tsv     # 入力：キー<TAB>URL

出力：キー / 前の所見 / 新しい所見（空＝外す）/ 一番新しい年 / その年が出てくる文

★採点の道具（~/kmtools/sitecheck.py の last_year）は「2025.10.13」の点区切りを数えず、
  「since 2010」のような創業の表記を数えていた。高広工業はお知らせが 2025年10月まであるのに「11年前」、
  アーキ名城は創業の 2010 を拾って「16年前」になっていた。ここでは
  ・点区切り・「/」・「年」で区切った日付と、著作権の表示（© 2003-2019 の後ろの年まで）を数える
  ・直前に since・創業・設立・創立・開業・Est があり、日付の形でない年は数えない
  sitecheck.py は点の物差しを変えないため触らない。
"""
import datetime
import re
import sys
import time

sys.path.insert(0, __import__("os").path.expanduser("~/kmtools"))
import listweb as W   # noqa: E402

STALE_YEARS = 3
THIS = datetime.date.today().year
DATE = r"((?:19|20)\d{2})\s*[./／年-]\s*(?:1[0-2]|0?[1-9])\s*[./／月-]\s*(?:3[01]|[12]\d|0?[1-9])(?!\d)"
COPY = r"(?:©|&copy;|\(c\)|copyright)[^0-9<]{0,20}((?:19|20)\d{2})(?:\s*[-–~〜]\s*((?:19|20)\d{2}))?"
FOUND = r"(?i)(?:since|創業|設立|創立|開業|est\.?)\s*[:：]?\s*$"


def newest(html):
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&nbsp;|\s+", " ", s)
    best, where = None, ""
    for p in (DATE, COPY):
        for m in re.finditer(p, s, re.I):
            if p is DATE and re.search(FOUND, s[max(0, m.start() - 12):m.start()]):
                continue
            for y in (int(g) for g in m.groups() if g):
                if 1995 <= y <= THIS and (best is None or y > best):
                    best, where = y, s[max(0, m.start() - 20):m.end() + 20].strip()
    return best, where


def main(path):
    print("キー\t前の所見\t新しい所見\t一番新しい年\tその年が出てくる文", flush=True)
    for line in open(path, encoding="utf-8"):
        key, url = line.rstrip("\n").split("\t")[:2]
        page, err = W.get_any(url)
        if page is None:
            print(f"{key}\t?\t（取れない {err}）\t\t", flush=True)
            continue
        y, where = newest(page.html)
        new = "" if y is None or THIS - y < STALE_YEARS else f"更新が{THIS - y}年前まで"
        print(f"{key}\t\t{new}\t{y or ''}\t{where}", flush=True)
        time.sleep(1.5)


if __name__ == "__main__":
    main(sys.argv[1])
