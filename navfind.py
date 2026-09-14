#!/usr/bin/env python3
"""相手のサイトからメニュー項目の候補を拾う。

    python3 navfind.py nav_todo.tsv        # キー / サイトURL / 社名 のTSV

★**拾った候補をそのまま使わない。** お知らせの見出し・取引先名・商品カテゴリが
  混ざる（2026-09-14、セッタで「施工事例を更新しました。」、小川木工家具で
  「飛騨産業（株）」「ソファ」を拾った）。**必ず人が目を通して選ぶ。**

★なぜ要るか: 提案の見本はトップページ1枚だが、メニューが既定の4項目だと、
  下層ページを持つ相手には**構成が劣化して見える**。メニューだけ相手の構成に
  合わせると「この構成のまま作り直す」という提案になる。
"""
import gzip, html as H, re, ssl, sys, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EasyWebCraft-FactFinder/1.0"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
# メニューに出したくないもの。トップ・言語・規約・リンク集など
SKIP = re.compile(r'(home|top|トップ|ホーム|english|sitemap|サイトマップ|プライバシー|'
                  r'privacy|個人情報|リンク集?$|^リンク$|copyright|ページトップ)', re.I)


def get(url):
    r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(r, timeout=20, context=CTX) as f:
        b = f.read(300_000)
        if f.headers.get("Content-Encoding") == "gzip":
            try: b = gzip.decompress(b)
            except Exception: pass
    enc = (re.search(rb'charset=["\']?([\w-]+)', b[:3000]) or [None, b"utf-8"])[1].decode("ascii", "ignore")
    if enc.lower() in ("x-sjis", "shift-jis", "sjis"): enc = "cp932"
    return b.decode(enc, "replace")


def candidates(url):
    h = get(url)
    host = urllib.parse.urlparse(url).netloc
    out = []
    for m in re.finditer(r'<a[^>]+href="([^"#]+?)"[^>]*>(.*?)</a>', h, re.S):
        href = m.group(1)
        label = H.unescape(re.sub(r'<[^>]+>', '', m.group(2)))
        label = re.sub(r'\s+', '', label)
        if not (2 <= len(label) <= 12) or SKIP.search(label):
            continue
        if label.endswith(("。", "！", "？")):      # お知らせの見出しを弾く
            continue
        if not re.search(r'\.(html?|php)$|/$', href):
            continue
        if href.startswith(("http", "//")) and host not in href:
            continue
        if label not in out:
            out.append(label)
    return out


def main(path):
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        key, url, name = (line.rstrip("\n").split("\t") + ["", ""])[:3]
        try:
            c = candidates(url)
        except Exception as e:
            c = []
            print(f"# {key}\t{name}\t取得できず({type(e).__name__})")
        if c:
            print(f"# {key}\t{name}")
            print("   " + " / ".join(c))
        time.sleep(1.2)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "nav_todo.tsv")
