#!/usr/bin/env python3
"""見本の会社のサイトから、本文の文字だけを手元に集める（できること・会社紹介を事実から書く材料）。

    python3 sitetext.py urls.tsv            # キー / サイトURL / 社名 のTSV
    → _src/<キー>.txt（公開しない。.gitignore 済み）

トップと、トップからリンクしている事業・製品・会社案内らしいページを最大4枚。1ページ6000字まで。
★材料は事実を拾うためのもの。相手の文章は写さない（README の「守ること」）。
★同じサイトには1.2秒あけて読む。違うサイトは8件ずつ同時に読む。
"""
import re
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from factfind import WAIT, get, get_with_fallback, text_of

LINK = re.compile(r"事業|製品|商品|サービス|業務|施工|工事|実績|事例|会社|企業|概要|沿革|特長|特徴|強み|設備|技術|"
                  r"about|company|profile|service|product|business|works|gaiyou|outline|equipment", re.I)
OUT = "_src"


def pages(h, base):
    host = urllib.parse.urlparse(base).netloc
    out = []
    for m in re.finditer(r'<a[^>]+href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', h, re.S | re.I):
        href, label = m.group(1), re.sub(r"<[^>]+>|\s", "", m.group(2))
        if not (LINK.search(label) or LINK.search(href)) or re.search(r"\.(pdf|jpe?g|png|gif|zip)$", href, re.I):
            continue
        u = urllib.parse.urljoin(base, href)
        if urllib.parse.urlparse(u).netloc != host or u.rstrip("/") == base.rstrip("/") or u in out:
            continue
        out.append(u)
    return out[:4]


def clean(t):
    return "\n".join(x.strip() for x in t.split("\n") if x.strip())[:6000]


def one(key, url):
    try:
        h, final = get_with_fallback(url)
    except Exception as e:
        return key, f"# 取得できず {url} ({type(e).__name__})\n"
    body = [f"# {final}\n{clean(text_of(h))}"]
    for u in pages(h, final):
        time.sleep(WAIT)
        try:
            h2, f2 = get(u)
            body.append(f"# {f2}\n{clean(text_of(h2))}")
        except Exception:
            pass
    return key, "\n\n".join(body) + "\n"


def main(path):
    import os
    os.makedirs(OUT, exist_ok=True)
    rows = [l.rstrip("\n").split("\t")[:2] for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")]
    rows = [(k, u) for k, u in rows if not os.path.exists(f"{OUT}/{k}.txt")]
    with ThreadPoolExecutor(8) as ex:
        for n, (k, txt) in enumerate(ex.map(lambda r: one(*r), rows), 1):
            open(f"{OUT}/{k}.txt", "w", encoding="utf-8").write(txt)
            print(n, k, len(txt), flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
