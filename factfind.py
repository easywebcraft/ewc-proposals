#!/usr/bin/env python3
"""相手のサイトから「事実」だけを拾う：電話・郵便番号・住所・創業（設立）年・許可番号・受付時間。

    python3 factfind.py nav_todo.tsv          # キー / サイトURL / 社名 のTSV（navfind.py と同じ形）
    python3 factfind.py nav_todo.tsv > facts.tsv

出力（TSV）: key / name / tel / zip / addr / founded / founded_kind / permits / hours / pages / note
  founded_kind は「創業」か「設立」。sites.json の "founded" は見本の上部に「創業 1948年」と出る。
  設立しか見つからない先は "founded" に入れず、数字の帯（stats）に ["1990","年","設立"] と書く
  （アメミヤ建設の形）。上部に「創業」と出て事実と違ってしまうのを避けるため。

★ここが出すのは**候補**。必ず相手のサイトを開いて目で確かめてから sites.json に書く。
  見本は相手本人が読むので、電話や住所が1文字でも違うと「適当に作った」と思われる。

★拾うのは事実だけ。文章・写真・ロゴは拾わない（README の「守ること」）。

★なぜ1枚目だけでなく会社概要のページも見るか：
  トップには電話しか無く、住所・創業・許可番号は「会社概要」「会社案内」にあることが多い。
  トップのリンクから会社概要らしいページを最大2枚だけ追加で読む。

★よくある外し方（拾い方に対処を入れてある）:
  - FAX番号を電話として拾う → 「FAX」の直後の番号は外す
  - フリーダイヤルと代表番号が両方ある → 両方出す（どちらを載せるかは人が決める）
  - 取引先・営業所の住所を拾う → 最初に出た〒付きの住所を本社とみなし、他は note に数だけ出す
  - 「設立」を「創業」として載せる → 種類を分けて出す（扱いは上の founded_kind の説明）
  - 和暦（昭和48年）→ 西暦に直して出す。元の表記も note に残す
  - https に対応していない古いサイト → http で読み直す（営業リストの作り方.md の教訓。
    これを飛ばすと一番の当たりを落とす）

1件ごとに1.2秒あける（相手のサーバーに負担をかけない）。標準ライブラリだけで動く。
"""
import gzip
import html as H
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) EasyWebCraft-FactFinder/2.0"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
WAIT = 1.2

PREFS = ("北海道|青森県|岩手県|宮城県|秋田県|山形県|福島県|茨城県|栃木県|群馬県|埼玉県|千葉県|東京都|"
         "神奈川県|新潟県|富山県|石川県|福井県|山梨県|長野県|岐阜県|静岡県|愛知県|三重県|滋賀県|京都府|"
         "大阪府|兵庫県|奈良県|和歌山県|鳥取県|島根県|岡山県|広島県|山口県|徳島県|香川県|愛媛県|高知県|"
         "福岡県|佐賀県|長崎県|熊本県|大分県|宮崎県|鹿児島県|沖縄県")
TEL = re.compile(r"(?<![\d-])(0\d{1,4})[-‐－ー（）() ]{1,2}(\d{1,4})[-‐－ー（）() ]{1,2}(\d{3,4})(?!\d)")
ZIP = re.compile(r"〒\s*(\d{3})[-‐－ー]?(\d{4})")
# 番地の後ろは「丁目・番地・番・号・ハイフン＋数字」を続けて拾う（「2丁目89番地」を「2」で切らない）
TAIL = r"\d+(?:(?:丁目|番地|番|号|[-‐－ー])\d*)*"
ADDR = re.compile(r"(%s)[^\n\r\t<>「」【】、。，,|｜/()（）]{3,40}?%s" % (PREFS, TAIL))
ADDR_NOPREF = re.compile(r"[一-龠ぁ-んァ-ヶ]{1,6}[市町村郡][^\n\r\t<>「」【】、。，,|｜/()（）]{2,30}?" + TAIL)
# 「愛知県知事登録」「岐阜県知事許可」のような許可・登録の文言は住所ではない
NOT_ADDR = re.compile(r"知事|大臣|許可|登録|免許|第\d")
YEAR = r"((?:19|20)\d{2})\s*年|((?:明治|大正|昭和|平成|令和)\s*(?:\d{1,2}|元)\s*年)"
FOUNDED = re.compile(r"(創業|創立|設立)[^0-9明大昭平令]{0,12}(?:%s)" % YEAR)
PERMIT = re.compile(
    r"((?:%s|国土交通大臣)\s*(?:知事)?\s*(?:許可)?\s*[（(]\s*[般特][-‐－ー]\s*\d+\s*[)）]\s*第?\s*[\d-]+\s*号?)"
    r"|(宅地建物取引業[^\s<>。]{0,4}免許[^\s<>。]{0,30}?第\s*[\d-]+\s*号)"
    r"|(ISO\s*(?:9001|14001|45001))" % PREFS)
HOURS = re.compile(r"(?:営業時間|受付時間|受付)[：:\s　]*([0-2]?\d[:：]\d{2}\s*[〜～~\-－ー]\s*[0-2]?\d[:：]\d{2})")
ERA = {"明治": 1867, "大正": 1911, "昭和": 1925, "平成": 1988, "令和": 2018}
COMPANY_LINK = re.compile(r"会社概要|会社案内|企業情報|会社情報|企業概要|事業所概要|アクセス|"
                          r"company|about|profile|gaiyou|gaiyo|outline|corporate|access", re.I)


def get(url):
    r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(r, timeout=20, context=CTX) as f:
        b = f.read(600_000)
        final = f.geturl()
        if f.headers.get("Content-Encoding") == "gzip":
            try:
                b = gzip.decompress(b)
            except Exception:
                pass
    m = re.search(rb'charset=["\']?([\w-]+)', b[:4000])
    enc = (m.group(1) if m else b"utf-8").decode("ascii", "ignore").lower()
    if enc in ("x-sjis", "shift-jis", "shift_jis", "sjis"):
        enc = "cp932"
    if enc in ("euc-jp", "x-euc-jp"):
        enc = "euc_jp"
    try:
        return b.decode(enc, "replace"), final
    except LookupError:
        return b.decode("utf-8", "replace"), final


def get_with_fallback(url):
    """https で読めなければ http で、その逆も試す（古いサイト対策）。"""
    try:
        return get(url)
    except Exception as e1:
        alt = re.sub(r"^https://", "http://", url) if url.startswith("https://") else \
            re.sub(r"^http://", "https://", url)
        time.sleep(WAIT)
        try:
            return get(alt)
        except Exception:
            raise e1


def text_of(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</(p|div|li|tr|td|th|dd|dt|h\d)>", "\n", h)
    t = H.unescape(re.sub(r"<[^>]+>", " ", h))
    t = t.translate(str.maketrans("０１２３４５６７８９－（）：", "0123456789-():"))
    return re.sub(r"[ \t　]+", " ", t)


def company_pages(h, base):
    host = urllib.parse.urlparse(base).netloc
    out = []
    for m in re.finditer(r'<a[^>]+href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', h, re.S | re.I):
        href, label = m.group(1), re.sub(r"<[^>]+>|\s", "", m.group(2))
        if not (COMPANY_LINK.search(label) or COMPANY_LINK.search(href)):
            continue
        u = urllib.parse.urljoin(base, href)
        if urllib.parse.urlparse(u).netloc != host or u.rstrip("/") == base.rstrip("/"):
            continue
        if re.search(r"\.(pdf|jpe?g|png|gif|zip)$", u, re.I):
            continue
        if u not in out:
            out.append(u)
    return out[:2]


def era_to_year(s):
    m = re.match(r"(明治|大正|昭和|平成|令和)\s*(\d{1,2}|元)", s)
    if not m:
        return None
    n = 1 if m.group(2) == "元" else int(m.group(2))
    return ERA[m.group(1)] + n


def find_tels(t):
    tels = []
    for m in TEL.finditer(t):
        before = t[max(0, m.start() - 8):m.start()]
        if re.search(r"FAX|Fax|fax|ＦＡＸ|ファックス|ﾌｧｯｸｽ", before):
            continue
        num = "-".join(m.groups())
        if len(re.sub(r"\D", "", num)) not in (10, 11):
            continue
        if num not in tels:
            tels.append(num)
    return tels


def facts(text):
    f = {"tels": find_tels(text)}
    z = ZIP.search(text)
    f["zip"] = "%s-%s" % z.groups() if z else ""
    addrs = []
    for m in ADDR.finditer(text):
        a = re.sub(r"\s+", "", m.group(0))
        if NOT_ADDR.search(a):
            continue
        if a not in addrs:
            addrs.append(a)
    if not addrs and z:
        m = ADDR_NOPREF.search(text, z.end(), z.end() + 80)
        if m:
            addrs.append(re.sub(r"\s+", "", m.group(0)))
    f["addrs"] = addrs
    found = []
    for m in FOUNDED.finditer(text):
        kind = "創業" if m.group(1) in ("創業", "創立") else "設立"
        if m.group(2):
            y, raw = int(m.group(2)), ""
        else:
            y, raw = era_to_year(m.group(3)), m.group(3)
        if y and 1868 <= y <= 2026:
            found.append((kind, y, raw))
    f["founded"] = found
    permits = []
    for m in PERMIT.finditer(text):
        p = re.sub(r"\s+", "", next(g for g in m.groups() if g))
        if p not in permits:
            permits.append(p)
    f["permits"] = permits
    hm = HOURS.search(text)
    f["hours"] = re.sub(r"\s+", "", hm.group(1)) if hm else ""
    return f


def merge(a, b):
    for k in ("tels", "addrs", "founded", "permits"):
        for x in b[k]:
            if x not in a[k]:
                a[k].append(x)
    for k in ("zip", "hours"):
        a[k] = a[k] or b[k]
    return a


def one(url):
    h, final = get_with_fallback(url)
    pages = [final]
    f = facts(text_of(h))
    for u in company_pages(h, final):
        time.sleep(WAIT)
        try:
            h2, f2 = get(u)
            f = merge(f, facts(text_of(h2)))
            pages.append(f2)
        except Exception:
            pass
    return f, pages


def row(key, name, f, pages):
    note = []
    sou = [x for x in f["founded"] if x[0] == "創業"]
    pick = sou[0] if sou else (f["founded"][0] if f["founded"] else None)
    if pick and pick[2]:
        note.append("和暦: %s" % pick[2])
    if len(f["addrs"]) > 1:
        note.append("住所の候補ほか%d件" % (len(f["addrs"]) - 1))
    if len(f["tels"]) > 1:
        note.append("電話の候補: " + " / ".join(f["tels"][1:4]))
    if not f["tels"]:
        note.append("電話が見つからない")
    return "\t".join([
        key, name,
        f["tels"][0] if f["tels"] else "",
        f["zip"],
        f["addrs"][0] if f["addrs"] else "",
        str(pick[1]) if pick else "",
        pick[0] if pick else "",
        "／".join(f["permits"]),
        f["hours"],
        " ".join(pages),
        "；".join(note)])


HEAD = "key\tname\ttel\tzip\taddr\tfounded\tfounded_kind\tpermits\thours\tpages\tnote"


def main(path):
    print(HEAD, flush=True)
    for line in open(path, encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        key, url, name = (line.rstrip("\n").split("\t") + ["", ""])[:3]
        try:
            f, pages = one(url)
            print(row(key, name, f, pages), flush=True)
        except Exception as e:
            print("\t".join([key, name] + [""] * 7 + [url, "取得できず(%s)" % type(e).__name__]), flush=True)
        time.sleep(WAIT)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
