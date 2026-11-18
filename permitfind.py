#!/usr/bin/env python3
"""見本を作る先のサイトの建設業許可の表記を、国土交通省の建設業者検索の記録と比べる（見本作りの2のあと）。

    python3 permitfind.py nav_todo.tsv            # 照合して結果を表示するだけ（sites.json は変えない）
    python3 permitfind.py nav_todo.tsv --apply    # 表記が古い先の sites.json に所見と最新の許可を入れる

入力: nav_todo.tsv（キー / サイトURL / 社名）。sites.json の型が kensetsu の先だけ見る（先に3で書いておく）。
表記が1回分以上の更新で古い先に、次の2つを入れる。
  - 所見（intro.findings）の末尾に「許可表記が古い(般-19→般-5・令和5年更新)」
    見本の冒頭の囲みと営業メールの一番上のほうに出る（ewc-crm/salesmail.py の PITCHES）
  - permits（会社案内の許可）を国の記録どおりの表記に。同じ番号の古い表記は消す
CRM の所見には、登録（register.py --apply）のあとに permit_register.py で足す。

★国の検索（ https://etsuran2.mlit.go.jp/TAKKEN/ ）は公共データ利用規約で使える。1回ごとに3秒あける。
  代表者名は読まない・記録しない。相手のサイトは1回ごとに1秒あける。
★次の先は入れない（2026-11-19 の全件照合で決めた）:
  - 国の記録の社名がサイトの社名と違う（番号の読み違い・別の会社）
  - サイトに同じ番号で許可の年が2つある・国の記録で業種ごとに許可の年が違う（どれが今の表記か決められない）
  - 番号が国の記録に無い・表記が最新・サイトに表記が無い
★サイトの「般-19」の年は、令和なら8以下、それより大きければ平成（平成32＝令和2）、33以上は昭和と読む。
"""
import html
import http.cookiejar
import json
import re
import ssl
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

ETSU = "https://etsuran2.mlit.go.jp/TAKKEN/"
UA = "Mozilla/5.0 (Macintosh) EasyWebCraft-permitfind"
KEN = {"北海道": "01", "青森県": "02", "岩手県": "03", "宮城県": "04", "秋田県": "05", "山形県": "06", "福島県": "07",
       "茨城県": "08", "栃木県": "09", "群馬県": "10", "埼玉県": "11", "千葉県": "12", "東京都": "13", "神奈川県": "14",
       "新潟県": "15", "富山県": "16", "石川県": "17", "福井県": "18", "山梨県": "19", "長野県": "20", "岐阜県": "21",
       "静岡県": "22", "愛知県": "23", "三重県": "24", "滋賀県": "25", "京都府": "26", "大阪府": "27", "兵庫県": "28",
       "奈良県": "29", "和歌山県": "30", "鳥取県": "31", "島根県": "32", "岡山県": "33", "広島県": "34", "山口県": "35",
       "徳島県": "36", "香川県": "37", "愛媛県": "38", "高知県": "39", "福岡県": "40", "佐賀県": "41", "長崎県": "42",
       "熊本県": "43", "大分県": "44", "宮崎県": "45", "鹿児島県": "46", "沖縄県": "47"}
# サイトの許可の表記。例「愛知県知事許可（般-19）第12345号」「許可(知事般-2)第100378号」
PAT = re.compile(r"((?:国土交通大臣|[^\s、。]{2,4}?知事)?\s*(?:許可)?\s*[（(]\s*(?:知事)?\s*([般特])\s*[-‐－ー]?\s*(\d{1,2})"
                 r"\s*[)）]\s*第?\s*0*(\d{3,6})\s*号?)")
PREF = re.compile(r"(国土交通大臣|北海道|東京都|京都府|大阪府|[一-龥]{2,3}県)")   # 「】愛知県」の記号を県名に含めない

_jar = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
_jar.addheaders = [("User-Agent", UA)]
# 相手のサイトは証明書が壊れていても中身を読む（壊れていること自体は sitecheck.py が所見にする）
_loose = ssl.create_default_context()
_loose.check_hostname = False
_loose.verify_mode = ssl.CERT_NONE


def nfkc(s):
    return unicodedata.normalize("NFKC", s or "")


def text(raw):
    s = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


def decode(raw, cs):
    if not cs:
        m = re.search(rb"charset=[\"']?([\w-]+)", raw[:3000])
        cs = m.group(1).decode() if m else "utf-8"
    try:
        return raw.decode(cs, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


def site_get(url):
    time.sleep(1.0)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20, context=_loose) as r:
        return decode(r.read(), r.headers.get_content_charset())


def etsu_get(path, data):
    time.sleep(3.0)
    body = urllib.parse.urlencode(data, encoding="cp932").encode() if data else None
    with _jar.open(ETSU + path, body, timeout=25) as r:
        return r.read().decode("cp932", errors="replace")


def site_permits(url):
    """トップと、会社概要らしいページを3枚まで読み、許可の表記を拾う。開けなければ None。"""
    try:
        raw = site_get(url)
    except Exception:  # noqa: BLE001
        if not url.startswith("https://"):
            return None
        try:
            url = "http://" + url[8:]
            raw = site_get(url)
        except Exception:  # noqa: BLE001
            return None
    pages = []
    for href, label in re.findall(r"(?is)<a[^>]+href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", raw):
        if re.search(r"(?i)会社概要|会社案内|企業情報|会社情報|概要|company|about|profile|gaiyo|outline|corporate",
                     text(label) + " " + href):
            u = urllib.parse.urljoin(url, href)
            if urllib.parse.urlparse(u).netloc == urllib.parse.urlparse(url).netloc and u not in pages and u != url:
                pages.append(u)
    texts = [text(raw)]
    for u in pages[:3]:
        try:
            texts.append(text(site_get(u)))
        except Exception:  # noqa: BLE001
            pass
    found, seen = [], set()
    for t in texts:
        for m in PAT.finditer(nfkc(t)):
            k = (m.group(2), m.group(3), m.group(4))
            if k not in seen:
                seen.add(k)
                found.append({"kind": m.group(2), "year": int(m.group(3)), "num": m.group(4), "raw": m.group(1).strip()})
    return found


def etsu_find(kbn, ken, num):
    """許可番号で国の記録を引く。見つかった先の詳細（社名・許可・有効期間の始まりの年）。無ければ None。"""
    etsu_get("kensetuKensaku.do?outPutKbn=1", None)
    raw = etsu_get("kensetuKensaku.do", {
        "CMD": "search", "caller": "KS", "rdoSelect": "1", "rdoSelectJoken": "1", "rdoSelectSort": "1",
        "comNameKanjiOnly": "", "comNameKanaOnly": "", "licenseNoKbn": kbn, "licenseNoFrom": num,
        "licenseNoTo": num, "choice": "2", "kenCode": ken, "gyosyuType": "", "gyosyu": "", "keyWord": "",
        "dispCount": "10", "sortValue": "1", "dispPage": "1"})
    ids = list(dict.fromkeys(re.findall(r"js_ShowDetail\('(\d+)'\)", raw)))
    if not ids:
        return None
    t = text(etsu_get("ksGaiyo.do", {"sv_licenseNo": ids[0], "caller": "KS", "CMD": ""}))
    m = re.search(r"許可番号\s*(\S+許可)\s*第\s*(\d+)号", t)
    v = re.search(r"有効期間\s*R(\d+)年", t)
    years = set(re.findall(r"R(\d\d)/\d\d/\d\d", t))   # 業種ごとの許可の年
    n = re.search(r"商号又は名称\s*(.*?)\s*代表者", t)
    if not (m and v):
        return None
    return {"who": m.group(1), "num": str(int(m.group(2))), "reiwa": int(v.group(1)), "name": n.group(1) if n else "",
            "years": len(years)}


def short_name(s):
    s = nfkc(s)
    s = re.sub(r"株式会社|有限会社|合同会社|合資会社|合名会社|\((株|有|同|資)\)|㈱|㈲", "", s)
    return re.sub(r"\s+", "", s)


def western(y, latest_reiwa):
    """サイトの表記の年（数字だけ）を西暦に。"""
    if y <= 8 and y <= latest_reiwa:
        return 2018 + y
    if y <= 32:
        return 1988 + y
    return 1925 + y


def check(url, name, addr):
    """1社を照合する。(判定, 足す内容 or None)"""
    found = site_permits(url)
    if found is None:
        return "サイトが開けない", None
    if not found:
        return "サイトに表記なし", None
    f = found[0]
    pm = PREF.search(nfkc(f["raw"]))
    pref = pm.group(1) if pm else next((p for p in KEN if (addr or "").startswith(p)), "")
    if pref == "国土交通大臣":
        kbn, ken = "00", ""
    elif pref in KEN:
        kbn, ken = "01", KEN[pref]
    else:
        return "県が分からない（%s）" % f["raw"], None
    rec = etsu_find(kbn, ken, f["num"])
    if not rec:
        return "番号が国の記録に無い（%s）" % f["raw"], None
    if short_name(name) not in short_name(rec["name"]):
        return "国の記録の社名が違う（%s）" % rec["name"], None
    if rec["years"] > 1:
        return "国の記録で許可の年が2つ以上（業種ごとに更新の年が違う）", None
    same = sorted({x["year"] for x in found if x["num"] == f["num"] and x["kind"] == f["kind"]})
    if len(same) > 1:
        return "サイトに許可の年が2つ（%s）" % " / ".join(x["raw"] for x in found), None
    old = western(same[0], rec["reiwa"])
    new = 2018 + rec["reiwa"]
    miss = round((new - old) / 5)
    if miss < 1:
        return "最新", None
    code_old = "%s-%d" % (f["kind"], same[0])
    code_new = "%s-%d" % (f["kind"], rec["reiwa"])
    permit = "%s（%s）第%s号" % (rec["who"], code_new, rec["num"])
    return "表記が古い（%d回分）" % miss, {
        "token": "許可表記が古い(%s→%s・令和%d年更新)" % (code_old, code_new, rec["reiwa"]),
        "permit": permit, "num": rec["num"]}


def patch(lines, key, add):
    """sites.json の行を直接直す（ほかの先の書き方を崩さないため）。直せなければ理由を返す。"""
    tops = [i for i, l in enumerate(lines) if re.match(r'^ "[^"]+": \{$', l)]
    s = next((i for i in tops if lines[i] == ' "%s": {' % key), None)
    if s is None:
        return "sites.json に無い"
    e = next((i for i in tops if i > s), len(lines))
    ii = [i for i in range(s, e) if lines[i].startswith('  "intro": {"findings": "')]
    if not ii:
        lines.insert(s + 1, '  "intro": {"findings": ""},')
        e += 1
        ii = [s + 1]
    m = re.match(r'(  "intro": \{"findings": ")(.*)("\},?)$', lines[ii[0]])
    if len(ii) != 1 or not m:
        return "所見の行の形が違う"
    if "許可表記が古い" not in m.group(2):
        lines[ii[0]] = m.group(1) + (m.group(2) + " / " + add["token"] if m.group(2) else add["token"]) + m.group(3)
    pi = [i for i in range(s, e) if lines[i].startswith('  "permits":')]
    if pi:
        a = b = pi[0]
        if lines[a].rstrip().endswith("["):
            b = next(i for i in range(a, e) if lines[i].strip() in ("]", "],"))
        txt = " ".join(lines[a:b + 1]).split(":", 1)[1].strip()
        arr = json.loads(txt.rstrip(",")) or []
        arr = [add["permit"]] + [x for x in arr if add["num"] not in re.sub(r"\D", "", x) and x != add["permit"]]
        lines[a:b + 1] = ['  "permits": ' + json.dumps(arr, ensure_ascii=False) + ("," if txt.endswith(",") else "")]
    else:
        lines.insert(ii[0] + 1, '  "permits": ' + json.dumps([add["permit"]], ensure_ascii=False) + ",")
    return ""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    apply = "--apply" in sys.argv
    sites = json.load(open("sites.json", encoding="utf-8"))
    todo = [l.rstrip("\n").split("\t") for l in open(sys.argv[1], encoding="utf-8") if "\t" in l]
    adds = {}
    for c in todo:
        key, url = c[0], c[1]
        d = sites.get(key)
        if not d or d.get("industry") != "kensetsu" or key == "marushin-kaitai" or not url.startswith("http"):
            continue
        res, add = check(url, d["name"], d.get("addr", ""))
        print("  %-20s %-16s %s" % (res, key, d["name"]) + ("\n      足す所見：%s\n      会社案内の許可：%s"
                                                             % (add["token"], add["permit"]) if add else ""), flush=True)
        if add:
            adds[key] = add
    print("— 表記が古い先 %d件" % len(adds))
    if not adds or not apply:
        if adds:
            print("（--apply を付けると sites.json に入れる。そのあと build.py で見本を作り直す）")
        return
    lines = open("sites.json", encoding="utf-8").read().split("\n")
    for key, add in adds.items():
        ng = patch(lines, key, add)
        if ng:
            print("  入れられなかった：%s（%s）" % (key, ng))
    body = "\n".join(lines)
    json.loads(body)   # 壊れた JSON は書かない
    open("sites.json", "w", encoding="utf-8").write(body)
    print("sites.json に入れた")


if __name__ == "__main__":
    main()
