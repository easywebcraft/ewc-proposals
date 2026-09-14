#!/usr/bin/env python3
"""相手のサイトから「その会社らしい色」の候補を拾う。

なぜ要るか: 提案見本の色は業種ごとの既定（建設なら深緑）で全件同じだった。
相手のコーポレートカラーに寄せると「うちのために作った」と伝わる。

★ここが出すのはあくまで候補。必ず目で見てから sites.json の "accent" に書くこと。
  よくある外し方:
  - 見出しの下線やリンクの青など、会社の色ではない色が一番多く出る
  - 写真のまわりの飾り枠の色を拾う
  - 古いサイトは bgcolor= の指定が多く、背景色を拾ってしまう

使い方:
    python3 colorfind.py            # nav_todo.tsv の全件
    python3 colorfind.py shin-ei    # 1件だけ

出力は colors.tsv（id / URL / 候補を多い順に5つ / 採用案）。
採用案は「灰色でない・明るすぎない」色のうち最も多かったもので、
白抜き文字が読める濃さまで落としてある（modern.py の accent_of と同じ計算）。
"""
import re
import sys
import urllib.request
import urllib.parse

UA = {"User-Agent": "Mozilla/5.0 (compatible; EasyWebCraft-colorfind/1.0)"}
HEX = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")
LINK = re.compile(r'<link[^>]+rel=["\']?stylesheet["\']?[^>]*>', re.I)
HREF = re.compile(r'href=["\']([^"\']+)["\']', re.I)


def fetch(url, limit=400000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read(limit)
    for enc in ("utf-8", "cp932", "euc_jp"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def to_rgb(h):
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(rgb):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def darken_to_readable(rgb):
    """白抜きの文字が読める濃さまで落とす（白に対して 4.5:1）。"""
    rgb = tuple(float(x) for x in rgb)
    for _ in range(40):
        if 1.05 / (lum(rgb) + 0.05) >= 4.5:
            break
        rgb = tuple(x * 0.93 for x in rgb)
    return rgb


def hexof(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(x))) for x in rgb)


def usable(rgb):
    """灰色・白に近い色・真っ黒は会社の色として使えない。"""
    if max(rgb) - min(rgb) < 28:          # ほぼ無彩色
        return False
    y = lum(rgb)
    return 0.015 < y < 0.55               # 明るすぎ・暗すぎを外す


def colors_of(url):
    html = fetch(url)
    texts = [html]
    base = url
    for tag in LINK.findall(html)[:6]:
        m = HREF.search(tag)
        if not m:
            continue
        css = urllib.parse.urljoin(base, m.group(1))
        if urllib.parse.urlparse(css).netloc != urllib.parse.urlparse(base).netloc:
            continue                      # 外部の配布CSSは会社の色ではない
        try:
            texts.append(fetch(css))
        except Exception:
            pass

    count = {}
    for t in texts:
        for h in HEX.findall(t):
            rgb = to_rgb(h.lower())
            count[rgb] = count.get(rgb, 0) + 1
        for r, g, b in RGB.findall(t):
            rgb = (int(r), int(g), int(b))
            if max(rgb) < 256:
                count[rgb] = count.get(rgb, 0) + 1
    return count


def main(only=None):
    rows = [l.rstrip("\n").split("\t") for l in open("nav_todo.tsv", encoding="utf-8")
            if l.strip()]
    out = ["id\turl\t候補（多い順）\t採用案"]
    for sid, url, name in rows:
        if only and sid != only:
            continue
        try:
            count = colors_of(url)
        except Exception as ex:
            print(f"  ★取得できず {sid}: {ex}")
            out.append(f"{sid}\t{url}\t-\t-")
            continue
        ok = sorted(((n, c) for c, n in count.items() if usable(c)), reverse=True)
        top = "／".join(f"{hexof(c)}({n})" for n, c in ok[:5]) or "-"
        pick = hexof(darken_to_readable(ok[0][1])) if ok else "-"
        print(f"  {sid:16s} {pick:8s} {top}")
        out.append(f"{sid}\t{url}\t{top}\t{pick}")
    open("colors.tsv", "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("→ colors.tsv")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
