#!/usr/bin/env python3
"""sites.json から提案用トップページを生成する。

    python3 build.py            # 全部
    python3 build.py yak-k      # 1つだけ

★1件ずつ手書きしない理由
  相手の会社を名乗るページを公開するので、noindex と「見本です」の帯は
  絶対に落とせない。生成器が必ず付ける形にして、書き忘れる余地をなくす。

★載せるのは事実だけ（社名・電話・住所・創業年・事業の種類）。
  相手の文章・写真・ロゴは使わない。複製になるうえ、本人が読む。
  文章は sites.json に自分のことばで書く。
"""
import html as H
import json
import pathlib
import re
import sys

# 業種ごとの色と言い回し。型はここだけ変えれば増やせる。
INDUSTRY = {
    "kensetsu": {"label": "建設・住宅", "layout": "modern",
                 "navy": "#1f3a5f", "navy_d": "#16293f", "accent": "#1f7a4d",
                 "ground": "#f3f1ea", "ink2": "#2f3a33",
                 "svc": "できること", "svc_lead": "住まいの小さな修繕から、大きな工事まで。",
                 "flow_h": "ご相談から完成まで",
                 # ★流れ・受付時間・お知らせは「どの会社にも当てはまる言い方」だけにする（2026-09-29）。
                 #   「現地確認は無料」「近隣へのご挨拶も当社で」「平日8時から」のように相手の実際の
                 #   運用と違うことを書くと、読んだ本人に「適当に作った」と見抜かれる。
                 #   受付時間は相手のサイトで確かめた先だけ sites.json の "hours" に書く
                 "flow": [("ご相談", "ご要望をうかがいます。"),
                          ("現地の確認", "現地を拝見します。"),
                          ("ご提案・お見積り", "内容と費用をご説明します。"),
                          ("施工", "工事を進めます。")],
                 "cta": "まずはお電話ください", "cta_sub": "小さなご相談でも構いません。",
                 "hours": "受付時間が入ります",
                 "news_items": ["施工事例を追加しました", "休業日のご案内", "お知らせのタイトルが入ります"]},
    # 製造: 骨格は modern（建設と同じ）で、皮だけ references/seizo.md の型（2026-09-19）
    "seizo": {"label": "製造", "layout": "modern", "skin": "seizo",
              "navy": "#26323c", "navy_d": "#171f27", "accent": "#0e3f8a", "sub": "#d4420a",
              "ground": "#f4f5f7", "ink2": "#1f2733",
              "shot": "工場のようす・設備・製品など",
              "news_hint": "お知らせが入ります（新製品・展示会・休業日など）",
              "news_items": ["製品情報を更新しました", "休業日のご案内", "お知らせのタイトルが入ります"],
              "svc": "できること", "svc_lead": "一点ものから、継続の量産まで。",
              "flow_h": "ご発注までの流れ",
              "flow": [("ご相談", "用途や数量をうかがいます。"),
                       ("お見積り", "内容と費用をご説明します。"),
                       ("製作", "製作を進めます。"),
                       ("納品", "ご指定の方法でお届けします。")],
              "cta": "まずはご相談ください", "cta_sub": "小さなご相談でも構いません。",
              "hours": "受付時間が入ります"},
    "car": {"label": "自動車", "layout": "modern", "navy": "#1d3b4a", "navy_d": "#132836", "accent": "#c8552f",
            "ground": "#f2f3f3", "ink2": "#2c3439",
            "svc": "できること", "svc_lead": "車検から、急なトラブルまで。",
            "flow_h": "車検・修理の流れ",
            "flow": [("ご連絡・ご来店", "ご用件をうかがいます。"),
                     ("お見積り", "内容と費用をご説明します。"),
                     ("作業", "作業を進めます。"),
                     ("お引渡し", "お車をお返しします。")],
            "cta": "まずはお電話ください", "cta_sub": "小さなご相談でも構いません。",
            "hours": "受付時間が入ります"},
    "clinic": {"label": "クリニック", "navy": "#1e5361", "navy_d": "#143b46", "accent": "#3f9a86",
               "svc": "診療のご案内", "svc_lead": "気になることがあれば、早めにご相談ください。",
               "flow_h": "受診の流れ",
               "flow": [("ご来院・受付", "受付をお済ませください。"),
                        ("診察", "お話をうかがいます。"),
                        ("ご説明", "診察の内容をご説明します。"),
                        ("お会計", "お会計をお済ませください。")],
               "cta": "お電話でお問い合わせください", "cta_sub": "小さなご相談でも構いません。",
               "hours": "診療時間が入ります"},
    "shigyo": {"label": "士業", "navy": "#26344a", "navy_d": "#1a2433", "accent": "#8a7a4f",
               "svc": "承っていること", "svc_lead": "小さな会社と、個人事業の方へ。",
               "flow_h": "ご相談からのお付き合い",
               "flow": [("ご相談", "ご用件をうかがいます。"),
                        ("ご提案・お見積り", "内容と費用をご説明します。"),
                        ("ご契約", "ご納得いただいてから始めます。"),
                        ("業務の開始", "業務を進めます。")],
               "cta": "まずはお話をお聞かせください", "cta_sub": "小さなご相談でも構いません。",
               "hours": "受付時間が入ります"},
    "chiryo": {"label": "治療院", "navy": "#2b4a3f", "navy_d": "#1c3128", "accent": "#c07a3e",
               "svc": "施術のご案内", "svc_lead": "痛みの出ている場所だけを見ません。",
               "flow_h": "はじめての方へ",
               "flow": [("ご予約", "ご都合をうかがいます。"),
                        ("お話をうかがう", "お体の状態をうかがいます。"),
                        ("施術", "施術を行います。"),
                        ("次回のご案内", "次回のご予定をご相談します。")],
               "cta": "お電話でご予約ください", "cta_sub": "小さなご相談でも構いません。",
               "hours": "受付時間が入ります"},
}

CSS = """
:root{
  --ink:#232a33; --muted:#6b7480; --line:#e3e6ea; --line-s:#f2f4f6;
  --navy:%(navy)s; --navy-d:%(navy_d)s; --clay:%(accent)s;
  --bg:#fff; --panel:#f7f8fa;
  --serif:"Noto Serif JP","游明朝体","Yu Mincho",YuMincho,"ヒラギノ明朝 ProN W3",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Yu Gothic",Meiryo,
         "Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:var(--sans);color:var(--ink);background:var(--bg);
     line-height:1.9;-webkit-text-size-adjust:100%%}
img{max-width:100%%;display:block}
a{color:inherit}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
.notice{position:sticky;top:0;z-index:50;background:var(--clay);color:#fff;
        font-size:13px;line-height:1.6;padding:9px 16px;text-align:center}
.notice b{font-weight:700}
.notice span{display:block;opacity:.9;font-size:12px}
.ph{display:inline-block}
.mapbox{margin-top:22px;background:#eceef0;border:1px solid var(--line);border-radius:4px;
        aspect-ratio:16/7;display:grid;place-items:center;align-content:center;
        text-align:center;color:#6b7075;font-size:11.5px}
.mapbox b{display:block;font-family:var(--serif);font-size:14px;color:#4c5257;
          margin-bottom:4px;font-weight:500}
.gal{display:grid;gap:14px}
.gframe{background:#eceef0;border:1px solid var(--line);border-radius:4px;aspect-ratio:4/3;
        display:grid;place-items:center;align-content:center;text-align:center;
        color:#6b7075;font-size:12px;padding:0 14px}
.gframe b{display:block;font-family:var(--serif);font-size:14px;color:#4c5257;
          margin-bottom:4px;font-weight:500}
.notice .ph,footer .ph{display:inline-block;margin-right:.15em}
footer .by{margin:14px 0 0;font-size:11.5px}
footer .by .ph{margin:0 .5em}
footer .by a{color:inherit;text-decoration:underline;text-underline-offset:2px}
header{position:sticky;top:0;background:rgba(255,255,255,.94);
       backdrop-filter:blur(6px);border-bottom:1px solid var(--line);z-index:40}
.hd{display:flex;align-items:center;justify-content:space-between;gap:12px;
    min-height:62px;flex-wrap:wrap}
.logo{font-family:var(--serif);font-size:19px;letter-spacing:.06em;font-weight:600}
.logo small{display:block;font-family:var(--sans);font-size:10px;
            letter-spacing:.18em;color:var(--muted);font-weight:400}
nav{display:flex;order:3;flex:1 0 100%%;flex-wrap:wrap;
    column-gap:16px;row-gap:5px;font-size:12px;
    border-top:1px solid var(--line);margin:0;padding:8px 0 9px}
nav a{text-decoration:none;color:var(--muted)}
nav a:hover{color:var(--navy)}
.tel{display:inline-flex;flex-direction:column;align-items:flex-end;
     text-decoration:none;line-height:1.3}
.tel b{font-size:17px;color:var(--navy);letter-spacing:.02em}
.tel small{font-size:10px;color:var(--muted)}
.hero{position:relative;background:
      linear-gradient(135deg,var(--navy) 0%%,var(--navy-d) 62%%,#0f1f30 100%%);
      color:#fff;overflow:hidden}
.hero::after{content:"";position:absolute;inset:auto -10%% -40%% 40%%;height:70%%;
             background:radial-gradient(closest-side,rgba(0,0,0,.25),transparent);
             pointer-events:none}
.hero .wrap{position:relative;padding:64px 20px 56px}
.hero .eyebrow{font-size:12px;letter-spacing:.22em;opacity:.75;margin:0 0 18px}
.hero h1{font-family:var(--serif);font-weight:500;font-size:31px;line-height:1.55;
         margin:0 0 20px;letter-spacing:.03em}
.hero h1 em{font-style:normal;border-bottom:2px solid var(--clay);padding-bottom:2px}
.hero p{margin:0 0 30px;opacity:.9;font-size:15px;max-width:34em}
.cta{display:flex;flex-wrap:wrap;gap:12px}
.btn{display:inline-block;white-space:nowrap;padding:15px 26px;border-radius:3px;text-decoration:none;
     font-size:15px;font-weight:600;letter-spacing:.04em;transition:.2s}
.btn.p{background:var(--clay);color:#fff}
.btn.p:hover{filter:brightness(.9)}
.btn.g{border:1px solid rgba(255,255,255,.5);color:#fff}
.btn.g:hover{background:rgba(255,255,255,.1)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;
       background:var(--line);border-bottom:1px solid var(--line)}
.stats div{background:#fff;padding:22px 10px;text-align:center}
.stats b{display:block;font-family:var(--serif);font-size:34px;color:var(--navy);line-height:1.15}
.stats b small{font-size:13px}
.stats span{font-size:11px;color:var(--muted);letter-spacing:.06em}
section{padding:58px 0}
section.alt{background:var(--panel)}
h2{font-family:var(--serif);font-weight:500;font-size:24px;letter-spacing:.05em;
   margin:0 0 8px;text-align:center}
.lead{text-align:center;color:var(--muted);font-size:14px;margin:0 0 34px}
.cards{display:grid;gap:16px}
.card{background:#fff;border:1px solid var(--line);border-radius:4px;padding:24px 22px}
.card h3{font-size:17px;margin:0 0 10px;letter-spacing:.03em}
.card p{margin:0;font-size:14px;color:var(--muted)}
.flow{display:grid;gap:14px;counter-reset:s}
.step{background:#fff;border:1px solid var(--line);border-radius:4px;
      padding:20px 22px 20px 62px;position:relative}
.step::before{counter-increment:s;content:counter(s);position:absolute;left:20px;top:18px;
              width:28px;height:28px;border-radius:50%%;background:var(--navy);color:#fff;
              font-size:13px;display:grid;place-items:center;font-family:var(--serif)}
.step h3{font-size:16px;margin:0 0 6px}
.step p{margin:0;font-size:13.5px;color:var(--muted)}
table.info{width:100%%;border-collapse:collapse;font-size:14px}
table.info th,table.info td{border-bottom:1px solid var(--line);padding:14px 4px;
                            text-align:left;vertical-align:top}
table.info th{width:7.5em;color:var(--muted);font-weight:500}
.contact{background:var(--navy);color:#fff;text-align:center;padding:52px 20px}
.contact h2{color:#fff}
.contact .lead{color:rgba(255,255,255,.8)}
.contact .big{font-family:var(--serif);font-size:32px;letter-spacing:.04em;
              display:inline-block;margin:6px 0 4px;text-decoration:none;color:#fff}
.contact small{display:block;font-size:12px;opacity:.75;margin-bottom:22px}
footer{background:var(--navy-d);color:rgba(255,255,255,.62);font-size:12px;
       padding:26px 20px;text-align:center}
@media(min-width:768px){
  .hero .wrap{padding:96px 20px 84px}
  .hero h1{font-size:42px}
  .hd{flex-wrap:nowrap;min-height:62px}
  nav{order:0;flex:0 1 auto;flex-wrap:nowrap;column-gap:26px;font-size:14px;
      border-top:0;padding:0}
  .cards{grid-template-columns:repeat(3,1fr)}
  .gal{grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:18px}
  .gframe:first-child{grid-column:span 2;grid-row:span 2;aspect-ratio:auto}
  .stats b{font-size:42px}
  h2{font-size:29px}
  section{padding:78px 0}
}

/* ★紙に出したときのため（modern.py と同じ考え方）。
   背景色が落ちると、濃い地に白抜きの箇所が消える。
   断り書きの帯・ヒーロー・お問い合わせ・フッターを白地に置き換える。 */
@media print{
  html,body{background:#fff}
  header{position:static;border-bottom:1px solid var(--line)}
  .notice{position:static;background:#fff;color:#000;border:2px solid #000;
          padding:8px 12px;margin-bottom:10px}
  .notice b{color:#000}
  .hero{background:#fff;color:var(--ink);border-bottom:1px solid var(--line)}
  .hero h1,.hero .eyebrow,.hero p{color:var(--ink)}
  .hero .btn{background:#fff;color:var(--ink);border:1px solid var(--ink)}
  .contact{background:#fff;color:var(--ink);
           border-top:2px solid var(--line);border-bottom:2px solid var(--line)}
  .contact .big{color:var(--ink)}
  footer{background:#fff;color:#333;border-top:1px solid var(--line)}
  footer .by a{color:#333}
  footer .by a[href^="http"]::after{content:" (" attr(href) ")"}
  .card,.step,.gframe,.mapbox,.stats div{break-inside:avoid;page-break-inside:avoid}
  section{padding:26px 0}
  @page{margin:14mm}
}
"""


# 日本語は語の途中でも折り返るので、読点・句点で区切った句を
# inline-block にして切れ目をそこだけに限る（modern.py の phrase と同じ）。
def phrase(text, e):
    out, buf = [], ""
    for c in text:
        buf += c
        if c in "、。":
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return "".join(f'<span class="ph">{e(x)}</span>' for x in out)


def e(x):
    return H.escape(str(x or ""), quote=True)


# 会社ごとに上書きしてよい言い回し。業種の既定が合わないときに sites.json へ書く。
# ★業種の既定は「その業種で最も多い形」にしてあるが、同じ建設系でも
#   資材の販売と工務店では言うことが違う（2026-09-14、進英産業＝空調資材の販売で
#   「住まいの小さな修繕から、大きな工事まで」が合わなかった）。
# "flow"（流れの4段）も上書きできる（2026-10-04）。不動産の会社に建設の流れ（現地の確認→施工）が出ると
#   事実と違うため。上書きするときも「どの会社にも当てはまる言い方」だけにする。
OVERRIDABLE = ("svc", "svc_lead", "flow_h", "flow", "cta", "cta_sub", "hours")


def render(sid, d):
    ind = dict(INDUSTRY[d["industry"]])
    for k in OVERRIDABLE:
        if d.get(k):
            ind[k] = d[k]
    # 建設系は別の型（modern）。参考サイトから抜き出した作りは modern.py 側に置く。
    if ind.get("layout") == "modern":
        import modern
        return modern.render(sid, d, ind)
    tel = d.get("tel", "")
    tel_link = tel.replace("-", "")
    name = d["name"]
    import modern
    nav = modern.nav_html(d, ind, e)
    if d.get("accent"):
        navy, navy_d, _ = modern.accent_of(d, ind)
    else:
        navy, navy_d = ind["navy"], ind["navy_d"]
    css = CSS % {"navy": navy, "navy_d": navy_d, "accent": ind["accent"]}

    stats = "".join(
        f'<div><b>{e(a)}<small>{e(b)}</small></b><span>{e(c)}</span></div>'
        for a, b, c in d["stats"])
    cards = "".join(
        f'<div class="card" id="svc{i}"><h3>{e(t)}</h3><p>{e(p)}</p></div>'
        for i, (t, p) in enumerate(d["services"], 1))
    gal = d.get("gallery")
    gallery = ""
    if gal:
        frames = "".join(f'<div class="gframe"><b>お写真が入ります</b>{e(c)}</div>' for c in gal[:3])
        gallery = f"""<section class="alt" id="gallery">
  <div class="wrap">
    <h2>{e(d.get("gallery_h", "これまでの仕事"))}</h2>
    <p class="lead">お預かりしたお写真を、ここに並べます。</p>
    <div class="gal">{frames}</div>
  </div>
</section>"""

    steps = "".join(
        f'<div class="step"><h3>{e(t)}</h3><p>{e(p)}</p></div>' for t, p in ind["flow"])

    info = [("商号", name)]
    if d.get("addr"):
        info.append(("所在地", (f'〒{d["zip"]} ' if d.get("zip") else "") + d["addr"]))
    if tel:
        info.append(("電話", f'<a href="tel:{e(tel_link)}">{e(tel)}</a>'))
    if d.get("founded"):
        info.append(("創業", f'{e(d["founded"])}年'))
    info.append(("事業内容", "／".join(t for t, _ in d["services"][:5])))
    info_rows = "".join(f"<tr><th>{e(k)}</th><td>{v if k in ('電話',) else e(v)}</td></tr>"
                        for k, v in info)

    tel_block = (f'<a class="tel" href="tel:{e(tel_link)}"><b>{e(tel)}</b>'
                 f'<small>お電話でのご相談</small></a>' if tel else "")
    hero_btn = (f'<a class="btn p" href="tel:{e(tel_link)}">電話で相談する</a>'
                if tel else "")
    contact_tel = (f'<a class="big" href="tel:{e(tel_link)}">{e(tel)}</a>'
                   f'<small>{e(ind["hours"])}</small>'
                   f'<div><a class="btn p" href="tel:{e(tel_link)}">電話をかける</a></div>'
                   if tel else
                   f'<small>{e(ind["hours"])}</small>')

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- ★提案用の見本。検索に載せない。本物と誤認されないための最低条件 -->
<meta name="robots" content="noindex, nofollow, noarchive">
<!-- 一番上（FV）の写真の有無。この型には写真の枠が無いので常に0（CRMが毎朝7時に読む） -->
<meta name="ewc-fv-photo" content="0">
<title>【提案見本】{e(name)}さま トップページ案｜EasyWebCraft</title>
<style>{css}</style>
</head>
<body>

<div class="notice">
  <b>これは EasyWebCraft が作成した提案用の見本です。</b>
  <span><span class="ph">{e(name)}さまの公式サイトではありません。</span><span class="ph"><b>トップページだけを形にした見本</b>で、</span><span class="ph">メニューの各ページは実際の制作でお作りします。</span><span class="ph">写真・文章は当社が用意したものです。</span></span>
</div>

<header>
  <div class="wrap hd">
    <div class="logo">{e(name)}<small>{e(d.get("roman",""))} ／ {e(d.get("addr","").split("市")[0] + "市" if "市" in d.get("addr","") else "岐阜県")}</small></div>
    <nav>{nav}</nav>
    {tel_block}
  </div>
</header>

<div class="hero">
  <div class="wrap">
    <p class="eyebrow">{e(ind["label"])}{" ／ 創業 " + e(d["founded"]) + "年" if d.get("founded") else ""}</p>
    <h1>{phrase(d["catch"], e)}<br><em>{phrase(d["catch_em"], e)}</em></h1>
    <p>{phrase(d["sub"], e)}</p>
    <div class="cta">{hero_btn}<a class="btn g" href="#works">{e(ind["svc"])}を見る</a></div>
  </div>
</div>

<div class="stats">{stats}</div>

<section id="works">
  <div class="wrap">
    <h2>{e(ind["svc"])}</h2>
    <p class="lead">{e(ind["svc_lead"])}</p>
    <div class="cards">{cards}</div>
  </div>
</section>

{gallery}

<section class="alt" id="flow">
  <div class="wrap">
    <h2>{e(ind["flow_h"])}</h2>
    <p class="lead">流れの一例です。実際の制作では、御社の進め方に合わせて書き換えます。</p>
    <div class="flow">{steps}</div>
  </div>
</section>

<section id="company">
  <div class="wrap" style="max-width:720px">
    <h2>概要</h2>
    <p class="lead">&nbsp;</p>
    <table class="info">{info_rows}</table>
    <div class="mapbox"><b>地図が入ります</b>最寄り駅・駐車場のご案内もここに</div>
  </div>
</section>

<div class="contact" id="contact">
  <h2>{e(ind["cta"])}</h2>
  <p class="lead">{e(ind["cta_sub"])}</p>
  {contact_tel}
  <p class="lead" style="font-size:12px;opacity:.75">見本の電話のボタンは、御社の電話番号につながります。</p>
</div>

<footer>
  <span class="ph">この見本は EasyWebCraft が作成した提案資料です。</span><span class="ph">{e(name)}さまの公式サイトではありません。</span><br>
  <span class="ph">実際の制作では、</span><span class="ph">御社の写真・実績・文章に差し替えて仕上げます。</span>
  <p class="by"><span class="ph">EasyWebCraft（担当：田代）</span><span class="ph"><a href="mailto:info@easywebcraft.jp">info@easywebcraft.jp</a></span></p>
</footer>

{modern.ewc_bar(name)}
</body>
</html>
"""


# 全件の作り直しから外す見本（丸信は見本のまま残す。2026-11-11 松本さん）
KEEP = {"marushin-kaitai"}


def main(only=None):
    root = pathlib.Path(__file__).resolve().parent
    sites = json.loads((root / "sites.json").read_text(encoding="utf-8"))
    for sid, d in sites.items():
        if only and sid != only:
            continue
        if sid in KEEP and sid != only:
            continue
        out = root / sid
        out.mkdir(exist_ok=True)
        html = render(sid, d)
        # 写真のある型（建設・製造・自動車）には参考サイトの考え方を入れる（2026-11-15 松本さん「全てに適用」）
        if INDUSTRY[d["industry"]].get("layout") == "modern":
            html = apply_pick(html, d)
        html = apply_fast(html)   # 冒頭の演出を約2秒に（2026-11-15 松本さん「全てのサイトに適用」）
        if INDUSTRY[d["industry"]].get("layout") == "modern":
            html = apply_intro(html, d)   # 提案の説明・料金・デモ表示（2026-11-17 松本さん「全てに公開して」）
        (out / "index.html").write_text(html, encoding="utf-8")
        print(f"  {sid:<14} {d['name'][:22]:<24} {len(html):>6} バイト")


def trial(sid):
    """試作（v2）を <キー>-v2/ に作る。今の見本（<キー>/）は変えない（2026-10-31）。
    写真は ../photos を参照するので、出力はキーと同じ深さに置く。"""
    root = pathlib.Path(__file__).resolve().parent
    d = dict(json.loads((root / "sites.json").read_text(encoding="utf-8"))[sid])
    d["_v2"] = True
    out = root / (sid + "-v2")
    out.mkdir(exist_ok=True)
    html = render(sid, d)
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"  {sid}-v2  {d['name']}  {len(html)} バイト（試作）")


def trial_v3(sid):
    """試作（v3）を <キー>-v3/ に作る。sites.json の "v3" の中身で上書きしてから組む（2026-11-02）。
    今の見本（<キー>/）は変えない。"""
    root = pathlib.Path(__file__).resolve().parent
    d = dict(json.loads((root / "sites.json").read_text(encoding="utf-8"))[sid])
    d.update(d.pop("v3", {}))
    d["_v3"] = True
    out = root / (sid + "-v3")
    out.mkdir(exist_ok=True)
    html = render(sid, d)
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"  {sid}-v3  {d['name']}  {len(html)} バイト（試作）")


def trial_3d(sid):
    """立体版の試作を <キー>-3d/ に作る（2026-11-12 松本さん「見本を立体的にしたい」）。今の見本（<キー>/）は変えない。"""
    root = pathlib.Path(__file__).resolve().parent
    d = dict(json.loads((root / "sites.json").read_text(encoding="utf-8"))[sid])
    d["_3d"] = True
    out = root / (sid + "-3d")
    out.mkdir(exist_ok=True)
    html = render(sid, d)
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"  {sid}-3d  {d['name']}  {len(html)} バイト（立体版の試作）")


# 試作（2026-11-15）：松本さんが持ってきた参考サイト（sitepick の工務店の見本）の考え方を6つ入れる。
#   参考は売り物のデザインなので、コードは写さず考え方だけ。試作は <キー>-pick/、2026-11-15 から写真のある型の全見本に入れた
#   （トップの写真の上の説明文と小さな英字の社名は出さない。メインコピーは大きな英字と同じ出し方＝松本さんの指示）
#   1 見出しが長すぎても画面からはみ出さない  2 下の写真も画面に入ったらゆっくり元の大きさに
#   3 トップの写真の下端に英字の社名を細く大きく（出るときに字の間が詰まる）
#   4 各見出しの英字を細く大きく  5 流れを細い線と大きな番号に  6 欄ごとに地の色を変える
PICK_CSS = """<style>
h1 .cp,h2 .cp{max-width:100%;white-space:normal;word-break:keep-all;overflow-wrap:anywhere}
.pkz-o{position:relative;overflow:hidden}
.pkz{position:absolute;inset:0;background-size:cover;background-position:center;
  transform:scale(1.07);transition:transform 3.2s cubic-bezier(.2,.7,.2,1)}
.pkz-o.is-in .pkz{transform:none}
.pkz-o>:not(.pkz){position:relative;z-index:1}
.hero .bigen{display:none}
.hero .sub,.hero .meta .en{display:none}
.shot{position:relative}
.pk-big{position:absolute;left:0;right:0;bottom:4%;z-index:2;margin:0;text-align:center;color:#fff;
  font-family:"Helvetica Neue","Segoe UI",Arial,sans-serif;font-weight:200;line-height:.9;
  letter-spacing:.04em;white-space:nowrap;pointer-events:none;text-shadow:0 2px 20px rgba(0,0,0,.22);
  animation:pkTrack 2.6s cubic-bezier(.2,.7,.2,1) .8s both}
@media(min-width:760px){.hero.full .pk-big{bottom:150px}.hero.full .inner{padding-bottom:calc(var(--pkh,0px) + 40px)}}
@media(max-width:759px){.pk-big{bottom:62px}}
html.ewl-on:not(.ewl-txt) .pk-big{animation-play-state:paused}
/* メインコピー：下の大きな英字と同じ出し方（字の間が広い状態から、薄く出ながら詰まる） */
.hero h1.pk-tr{animation:pkTrackH 2.6s cubic-bezier(.2,.7,.2,1) .3s both}
.hero h1.pk-tr:not(.pk-done) .cp{max-width:none}
html.ewl-on:not(.ewl-txt) .hero h1.pk-tr{animation-play-state:paused}
@keyframes pkTrackH{from{opacity:0;letter-spacing:calc(var(--pkls) + .14em)}to{opacity:1;letter-spacing:var(--pkls)}}
@keyframes pkTrack{from{opacity:0;letter-spacing:.18em}to{opacity:1;letter-spacing:.04em}}
.sechead .en,.abtx .en{font-family:"Helvetica Neue","Segoe UI",Arial,sans-serif;font-weight:200;
  font-size:clamp(38px,5vw,64px);letter-spacing:.04em;line-height:1;color:inherit;text-transform:uppercase;margin-bottom:6px}
.sechead h2::after{display:none}
#flow{background:#1f2522;color:#fff}
#flow .sechead h2,#flow .step h3{color:#fff}
#flow .step p{color:rgba(255,255,255,.72)}
#flow .flow{gap:28px 32px}
#flow .step{background:none;border:0;border-top:1px solid rgba(255,255,255,.3);border-radius:0;box-shadow:none;padding:20px 0 0}
#flow .step::before,#flow .step::after,#flow .step .si{display:none}
#flow .step .sn{display:block;position:static;margin:0 0 12px;font-family:"Helvetica Neue","Segoe UI",Arial,sans-serif;
  font-weight:200;font-size:40px;line-height:1;letter-spacing:.04em;color:#fff;background:none;border:0}
section.alt{background:#f4f2ee}
section.alt.about{background:#e9e4da}
@media(prefers-reduced-motion:reduce){.pk-big,.hero h1.pk-tr{animation:none;opacity:1}.pkz{transform:none;transition:none}}
</style>
"""

PICK_JS = """<script>
(function(){
  var big=document.querySelector('.pk-big');
  function fit(){
    if(!big)return;
    var w=big.parentElement.clientWidth*.92, a=big.style.animation;
    big.style.animation='none';big.style.fontSize='100px';
    var s=big.scrollWidth;big.style.fontSize=Math.min(140,w*.15,100*w/s)+'px';big.style.animation=a;
    var h=big.closest('.hero');if(h)h.style.setProperty('--pkh',big.offsetHeight+'px');
  }
  fit();addEventListener('resize',fit);
  var still=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var h1=document.querySelector('.hero h1');
  if(h1&&!still){
    h1.style.setProperty('--pkls',getComputedStyle(h1).letterSpacing);
    h1.classList.add('pk-tr');
    h1.addEventListener('animationend',function(e){if(e.target===h1)h1.classList.add('pk-done');});
  }
  var els=[].slice.call(document.querySelectorAll('.cph.ph,.abph.ph,.gframe.ph'));
  els=els.filter(function(el){
    var bg=el.style.backgroundImage;if(!bg)return false;
    var i=document.createElement('i');i.className='pkz';i.style.backgroundImage=bg;
    el.style.backgroundImage='none';el.classList.add('pkz-o');el.insertBefore(i,el.firstChild);return true;
  });
  if(still||!('IntersectionObserver' in window)){els.forEach(function(el){el.classList.add('is-in')});return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(x){
    if(x.isIntersecting){x.target.classList.add('is-in');io.unobserve(x.target);}});},{rootMargin:'0px 0px -8% 0px'});
  els.forEach(function(el){io.observe(el)});
})();
</script>
"""


def apply_pick(html, d):
    """組み上がった見本に、参考サイトの考え方（PICK_CSS・PICK_JS・トップの大きな英字）を足す。"""
    html = html.replace("</head>", PICK_CSS + "</head>", 1)
    s = html.find('class="shot')
    lb = html.find('<div class="lb">', s)
    if s >= 0 and lb >= 0 and d.get("roman"):
        html = html[:lb] + f'<p class="pk-big" aria-hidden="true">{H.escape(d["roman"])}</p>' + html[lb:]
    return html.replace("</body>", PICK_JS + "</body>", 1)


def trial_pick(sid):
    """参考サイトの考え方を入れた試作を <キー>-pick/ に作る（2026-11-15 から本番の見本にも入っている）。"""
    root = pathlib.Path(__file__).resolve().parent
    d = json.loads((root / "sites.json").read_text(encoding="utf-8"))[sid]
    html = apply_pick(render(sid, d), d)
    out = root / (sid + "-pick")
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"  {sid}-pick  {d['name']}  {len(html)} バイト（参考サイトの試作）")



# 試作（2026-11-15）：冒頭の演出を約2秒に縮める。形はそのまま（輪が満ちる→社名→左上へ吸い込む）で、間合いだけ詰める。
#   今は文字が出始めるまで約4秒（輪1.6秒＋待ち0.25秒＋社名0.9秒＋吸い込み0.85秒）。試作は約1.8秒（輪0.9＋0.1＋社名0.5＋0.3）
#   社名を左上へ移す動きは省き、幕と一緒にその場で消す。社名を消し始めると同時に幕も薄くし始め、白い画面だけが残る間を作らない（松本さん「白い画面が残るのが違和感」）。
#   社名は0.4秒で先に消え、幕は1.2秒（はじめはゆっくり）なので、社名とページが重なって見えることもない
FAST_REPL = (
    ("var C=2*Math.PI*54,D=1600", "var C=2*Math.PI*54,D=900"),
    ("setTimeout(absorb,900);},250);", "setTimeout(absorb,500);},100);"),
    # 社名を左上のロゴへ移す動きは省く（2026-11-15 松本さん）。社名は幕と一緒にその場で薄れて消える
    ("    if(real&&copy){\n      // 中央に拡大して置いた社名を", "    if(false){\n      // 中央に拡大して置いた社名を"),
    ("setTimeout(function(){if(real)real.style.opacity='1';},950);", "setTimeout(function(){if(real)real.style.opacity='1';},300);"),
    ("setTimeout(function(){r.classList.add('ewl-txt');},850);", "setTimeout(function(){r.classList.add('ewl-txt');},600);"),
    ("setTimeout(end,1200);", "setTimeout(end,1300);"),
    ("L.remove();},500);", "L.remove();},350);"),
    ("transition:background-color .9s ease .25s,opacity .5s ease", "transition:background-color 1.2s ease-in,opacity .5s ease"),
    ("transition:opacity .6s ease .1s}", "transition:opacity .35s ease}"),
    ("transition:transform 1s cubic-bezier(.65,0,.35,1),opacity .45s ease .95s}", "transition:opacity .4s ease}"),
    ("transition:transform 1s cubic-bezier(.65,0,.35,1),opacity .45s ease .95s,color .8s ease}", "transition:opacity .4s ease}"),
    # PC の写真の上の型では、社名が白へ色を変えながら消えていた。日本語は一瞬で白くなり、英字だけ遅れて残って見えたので、
    # 色は変えずに日本語と英字を一緒に薄くする（2026-11-15 松本さん）
    ("html:has(.hdwrap.ovl) .ewl.is-absorb .logo{color:#fff;", "html:has(.hdwrap.ovl) .ewl.is-absorb .logo{"),
    ("html:has(.hdwrap.ovl) .ewl.is-absorb .logo small{color:rgba(255,255,255,.85);transition:color .8s ease}", ""),
)


def apply_fast(html):
    """冒頭の演出の間合いを FAST_REPL に置き換える。演出の無い型（士業・医院・治療院）はそのまま返す。"""
    if "var C=2*Math.PI*54,D=1600" not in html:
        return html
    for a, b in FAST_REPL:
        if a not in html:
            raise SystemExit(f"演出の間合いが見つからない: {a}")
        html = html.replace(a, b)
    return html


def trial_fast(sid):
    """冒頭の演出を約2秒にした試作を <キー>-fast/ に作る。今の見本（<キー>/）は変えない。"""
    root = pathlib.Path(__file__).resolve().parent
    d = json.loads((root / "sites.json").read_text(encoding="utf-8"))[sid]
    html = render(sid, d)
    if INDUSTRY[d["industry"]].get("layout") == "modern":
        html = apply_pick(html, d)
    html = apply_fast(html)
    out = root / (sid + "-fast")
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"  {sid}-fast  {d['name']}  {len(html)} バイト（演出を約2秒にした試作）")


# 試作（2026-11-17 松本さん）：「提案の説明」と「サイト見本」を分ける。
#   今は開くといきなり相手のサイトの見本に入り、EWC への相談の案内は下へ進んだ後の帯と末尾にしか無い。
#   受け手は自社名に引かれて開いても、何を判断すればよいか分からないので、見本の前に短い提案の説明を置き、
#   末尾に「制作範囲・料金」をまとめる。説明の文は会社ごとに今のサイトを見て書く（sites.json の "intro"）。
INTRO_CSS = """
.pintro{position:relative;z-index:3;background:linear-gradient(180deg,#f3f6fa 0%,#e9eef5 100%);color:#10294f;
  padding:22px 16px 20px;border-top:3px solid #10294f;border-bottom:1px solid #d5deea}
.pintro .pi-in{max-width:680px;margin:0 auto}
.pintro .pi-head{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px}
.pintro .pi-from{margin:0;padding:2px 10px;border-radius:999px;background:#10294f;color:#fff;font-size:11.5px;font-weight:700;letter-spacing:.06em}
.pintro .pi-to{margin:0;font-size:clamp(17px,3.4vw,20px);font-weight:700;letter-spacing:.04em;line-height:1.4}
.pintro .pi-box{margin:12px 0 0;padding:12px 16px;background:#fff;border-radius:10px;box-shadow:0 1px 2px rgba(16,41,79,.06),0 6px 18px rgba(16,41,79,.08)}
.pintro .pi-bh{margin:0;font-size:13px;font-weight:700;color:#4a5b75}
.pintro .pi-pairs{margin:0;padding:0;list-style:none}
.pintro .pi-pairs li{display:grid;gap:2px;padding:8px 0;border-top:1px solid #e3e9f1}
.pintro .pi-pairs li:first-child{margin-top:6px}
.pintro .pi-pairs p{margin:0;font-size:13.5px;line-height:1.6}
.pintro .pi-pairs span{display:inline-block;margin-right:8px;padding:0 7px;border-radius:3px;font-size:11px;font-weight:800;vertical-align:1px}
.pintro .pi-q{color:#4a5b75}
.pintro .pi-q span{background:#eef1f5;color:#4a5b75}
.pintro .pi-a{font-weight:700;color:#10294f}
.pintro .pi-a span{background:#ffc93c;color:#10294f}
@media(min-width:760px){.pintro .pi-pairs li{grid-template-columns:1fr 1fr;gap:16px}
  .pintro .pi-pairs span{display:block;width:max-content;margin:0 0 2px}}
.pintro .pi-more{padding-top:6px;border-top:1px solid #e3e9f1;font-size:12.5px;line-height:1.6;color:#4a5b75}
.pintro .pi-more b{margin-right:6px;color:#10294f}
.pintro .pi-bt{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.pintro .pi-bt a{flex:1 1 200px;display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 16px;
  border-radius:999px;font-size:14.5px;font-weight:700;text-decoration:none;transition:transform .2s,box-shadow .2s}
.pintro .pi-bt a:hover{transform:translateY(-2px);box-shadow:0 8px 18px rgba(16,41,79,.18)}
.pintro .pi-go{background:#10294f;color:#fff}
.pintro .pi-plan{background:#fff;color:#10294f;border:2px solid #10294f}
.pintro .pi-note{margin:6px 0 0;font-size:11.5px;color:#4a5b75}
/* 輪の上に置く（輪の下は画面の低いPCで下端に詰まるため） */
.ewl-to{position:absolute;left:16px;right:16px;top:max(14px,calc(50% - var(--ewd,112px)/2 - 64px));margin:0;text-align:center;
  font-size:15px;font-weight:700;letter-spacing:.08em;line-height:1.6;color:var(--navy,#10294f);opacity:0;transition:opacity .5s ease}
.ewl-to span{display:inline-block}
.ewl.is-in .ewl-to{opacity:1}
.ewl.is-absorb .ewl-to{opacity:0;transition:opacity .3s}
.pintro{padding-top:40px}
.pplan{background:#f3f6fa;color:#10294f;padding:56px 20px 64px}
.pplan .pp-in{max-width:860px;margin:0 auto}
.pplan h2{margin:0;font-size:clamp(22px,4vw,28px);letter-spacing:.06em;text-align:center}
.pplan .pp-sub{margin:10px 0 0;text-align:center;font-size:14.5px;color:#4a5b75}
.pplan .pp-grid{display:grid;gap:16px;margin-top:28px}
@media(min-width:760px){.pplan .pp-grid{grid-template-columns:1fr 1fr}}
.pplan .pp-card{background:#fff;border-radius:12px;padding:22px 24px;box-shadow:0 1px 2px rgba(16,41,79,.06),0 8px 22px rgba(16,41,79,.08)}
.pplan .pp-card h3{margin:0 0 10px;font-size:17px;padding-left:12px;border-left:4px solid #ffc93c}
.pplan .pp-price{margin:4px 0 0;font-size:clamp(22px,3.6vw,28px);font-weight:800;letter-spacing:.02em;line-height:1.5}
.pplan .pp-price span{display:block;white-space:nowrap}
.pplan ul{margin:0;padding-left:1.2em;font-size:15px;line-height:1.9}
.pplan .pp-wide{grid-column:1/-1}
.pplan ol{margin:0;padding-left:1.4em;font-size:15px;line-height:1.9}
.pplan .pp-bt{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;margin-top:28px}
.pplan .pp-bt a{display:inline-flex;align-items:center;justify-content:center;min-height:54px;padding:0 30px;border-radius:999px;
  font-size:16px;font-weight:700;text-decoration:none;box-shadow:0 6px 18px rgba(0,0,0,.14),inset 0 -3px 0 rgba(0,0,0,.1)}
.pplan .pp-m{background:#ffc93c;color:#10294f}
.pplan .pp-l{background:#06c755;color:#fff}
@media(max-width:759px){.pplan .pp-bt{flex-direction:column;align-items:center;gap:10px}.pplan .pp-bt a{width:min(100%,420px);text-align:center}}
/* 「詳しく聞きたい」は短いので、PC では2つのボタンを同じ幅にそろえる（黄色が小さく見えないように。2026-11-22） */
@media(min-width:760px){.pplan .pp-bt{display:grid;grid-template-columns:1fr 1fr;width:min(100%,700px);margin-left:auto;margin-right:auto}}
"""


# 問題ごとの「この案での改善」。キーと問題の言い方は営業メール（ewc-crm/salesmail.py の PITCHES）と同じものを使い、
#   メールで伝えた問題と、見本の冒頭の改善案が同じ言葉でつながるようにする（2026-11-17 松本さん）
FIXES = {
    "証明書エラー": "正しい証明書を設定した鍵付きの通信で公開し、警告が出ずにページがそのまま開くようにします",
    "許可表記が古い": "建設業許可は国土交通省の記録どおりの最新の表記で載せ、許可の更新などの書き換え含め情報更新は公開後は月額の中で当社が行います",
    "スマホ非対応": "スマートフォンの画面に合わせて、文字や写真を読みやすい大きさで表示します。この案もスマートフォンでそのままご覧いただけます",
    "https不可": "鍵付きの通信で公開し、「安全ではありません」の表示が出ないようにします",
    "Flash": "Flash を使わない作りにして、どの端末でもすべての部分が表示されるようにします",
    "更新が": "お知らせや写真の更新は、公開後も月額の中で当社がお手伝いします",
    "表組みレイアウト": "今の作り方で作り直し、文章や写真の一部だけを手軽に直せるようにします",
    "古いタグ": "今の作り方で作り直し、文章や写真の一部だけを手軽に直せるようにします",
    "レスポンシブ": "スマートフォン・タブレット・パソコンのどれで見ても、見え方が整うようにします",
}


def fix_for(key, d):
    """「この案では」の文。許可の表記だけは、所見に入れた更新年と新しい表記で会社ごとに書く（2026-11-19）。
    所見の書き方：「許可表記が古い(般-19→般-4・令和4年更新)」。国の建設業者検索で照合した先だけに入る。"""
    if key == "許可表記が古い":
        m = re.search(r"許可表記が古い\((.+?)→(.+?)・(.+?)更新\)", d.get("intro", {}).get("findings", ""))
        if m:
            return (f"国土交通省の記録では{m.group(3)}に更新されています。この案では最新の表記（{m.group(2)}）で載せ、"
                    "許可の更新などの書き換え含め情報更新は公開後は月額の中で当社が行います")
    return FIXES[key]


def _salesmail():
    """営業メールの部品（ewc-crm/salesmail.py）を読む。同じ親フォルダに ewc-crm がある前提。"""
    root = pathlib.Path(__file__).resolve().parent
    sys.path.insert(0, str(root.parent / "ewc-crm"))
    import salesmail
    return salesmail


def intro_html(d):
    """見本の前に置く提案の説明（sites.json の "intro"：findings）。一言の説明はメールと重なるので出さない（2026-11-17）。
    軸は「メールでお伝えした問題 → この案での改善」。メールに出るのは強い順に2つまでなので、
    同じ2つを大きく、残りは「あわせて改善すること」として小さく出す。"""
    import modern
    sm = _salesmail()
    # 所見が無い・メールで使う問題が見つからない会社は、宛名だけ出して改善の枠は出さない（2026-11-17 松本さん「そのままでOK」）
    m = sm.matched_pitches(d.get("intro", {}).get("findings", ""))
    if not m:
        return f"""<section class="pintro" id="proposal" aria-labelledby="pi-to">
  <div class="pi-in">
    <div class="pi-head"><p class="pi-from">EasyWebCraft からのご提案</p>
    <h2 class="pi-to" id="pi-to">{e(d["name"])}様へ</h2></div>
  </div>
</section>
"""
    main, rest = m[:2], m[2:]
    pair = "".join(
        f'<li><p class="pi-q"><span>気になった点</span>{e(ph)}</p>'
        f'<p class="pi-a"><span>この案では</span>{e(fix_for(k, d))}</p></li>' for k, ph in main)
    more = [FIXES[k] for k, _ph in rest if FIXES[k] not in {FIXES[x] for x, _ in main}]
    more_html = f'<p class="pi-more"><b>あわせて</b>{"／".join(e(x) for x in more)}</p>' if more else ""
    return f"""<section class="pintro" id="proposal" aria-labelledby="pi-to">
  <div class="pi-in">
    <div class="pi-head"><p class="pi-from">EasyWebCraft からのご提案</p>
    <h2 class="pi-to" id="pi-to">{e(d["name"])}様へ</h2></div>
    <div class="pi-box">
      <p class="pi-bh">メールでお伝えした点と、この案での改善</p>
      <ol class="pi-pairs">{pair}</ol>
      {more_html}
    </div>
  </div>
</section>
"""


def plan_html(d, pages):
    """末尾の「制作範囲・料金」。料金と月額に含まれるものは見本の帯・末尾と同じ（modern.EWC_PRICE）。
    2026-11-17 にボタンを外したが、2026-11-22 松本さん「料金の下にもボタンを戻す」：料金と進め方を読み終えたところが一番押しやすいため。
    押したときの動き（確かめの画面から送る）は帯のボタンと同じ（modern.EWCBAR の script が .pp-m にも付ける）"""
    import modern
    from urllib.parse import quote
    name = d["name"]
    body = (f"{name}様の見本について、詳しく聞きたいです。\n\n"
            "（このまま送っていただくだけで結構です。お電話でのご説明をご希望でしたら、"
            "お名前とお電話番号をお書き添えください）\n\nお名前：\nお電話番号：\n")
    mailto = "mailto:%s?subject=%s&body=%s" % (modern.EWC_MAIL, quote(f"{name}様の見本について"), quote(body))
    return f"""<section class="pplan" id="plan" aria-labelledby="pp-h">
  <div class="pp-in">
    <h2 id="pp-h">制作範囲・料金</h2>
    <p class="pp-sub">EasyWebCraft で{e(modern.short_name(name))}様のホームページを作り直す場合の内容です。</p>
    <div class="pp-grid">
      <div class="pp-card"><h3>料金</h3><p class="pp-price">{"".join(f'<span>{e(x)}</span>' for x in modern.EWC_PRICE.split("・"))}</p>
        <p style="margin:8px 0 0;font-size:14px;color:#4a5b75">まとまった制作費はかかりません。</p></div>
      <div class="pp-card"><h3>月額に含まれること</h3>
        <ul><li>制作と公開</li><li>スマートフォン対応</li><li>公開後の文章・写真の修正</li><li>安全性の対応</li><li>検索対策</li><li>運用のサポート</li></ul></div>
      <div class="pp-card pp-wide"><h3>お作りするページ</h3>
        <p style="margin:0;font-size:15px">この見本はトップページのみです。その他のページはご希望に沿った構成でお作りします。</p></div>
      <div class="pp-card pp-wide"><h3>公開までの進め方</h3>
        <ol><li>御社の写真と文章をお預かりします（見本の写真・文章は当社が用意したものです）</li>
        <li>お預かりしたものを入れて、公開まで当社で仕上げます</li>
        <li>公開後の修正やご相談も、月額の中でお受けします</li></ol></div>
    </div>
    <div class="pp-bt"><a class="pp-m" href="{e(mailto)}">{ASK_LABEL}</a><a class="pp-l" href="{e(modern.EWC_LINE)}" target="_blank" rel="noopener">{LINE_LABEL}</a></div>
  </div>
</section>
"""


# 試作（2026-11-17 松本さん）：問い合わせ先の混在をなくす。
#   見本の中の「お見積り・ご相談」「お電話」は相手の電話番号に、画面下の帯は EasyWebCraft につながり、丸い「ご相談ください」もあって、
#   どのボタンが誰への相談か迷う。ボタンを目立たせるより、押した先が分かることを優先する。
#   ・見本は枠で囲み「ここからは公開後のサイトイメージ」と書く
#   ・見本の中の電話は押してもつながらない「デモ表示」にする（押すとその旨を小さく出す）
#   ・EasyWebCraft へのボタンは「EasyWebCraftに制作内容を質問する」の1つだけを主ボタンにし、LINE は文字のリンクに下げる
#   ・丸い相談ボタンは外す
# 2026-11-22 松本さん「詳しく聞きたいにして」：メールの本文（「詳しく聞きたい」とご返信ください）とそろえる。
#   メールのリンクから開いた人には確かめの画面が出るので、前の「（メール）」も外した（前は「EasyWebCraftに制作内容を質問する（メール）」）
ASK_LABEL = '詳しく聞きたい'
LINE_LABEL = "LINEでEasyWebCraftに質問する"
DEMO_CSS = """
.pframe{position:relative}
.pframe::after{content:"";position:absolute;inset:0;z-index:70;pointer-events:none;border:4px solid #10294f}
.pf-lab,.pf-end{position:relative;z-index:71;margin:0;padding:6px 16px;background:#10294f;color:#fff;text-align:center;
  font-size:12.5px;font-weight:700;letter-spacing:.08em;line-height:1.5}
.pf-lab small,.pf-end small{display:inline-block;margin-left:8px;font-size:11px;font-weight:400;color:rgba(255,255,255,.75);letter-spacing:.02em}
a[data-demo]{cursor:not-allowed}
a.btn[data-demo]::after,.contact a.big[data-demo]::after{content:"デモ表示";display:inline-block;margin-left:10px;padding:1px 8px;border:1px solid currentColor;
  border-radius:3px;font-size:11px;font-weight:700;letter-spacing:.06em;line-height:1.5;vertical-align:middle;opacity:.85}
.contact a.big[data-demo]::after{font-size:12px;font-family:system-ui,sans-serif}
.demo-toast{position:fixed;left:16px;right:16px;top:18px;z-index:200;width:max-content;max-width:calc(100% - 32px);margin:0 auto;transform:translateY(-8px);padding:10px 16px;
  border-radius:8px;background:rgba(16,41,79,.95);color:#fff;font-size:13.5px;line-height:1.6;opacity:0;pointer-events:none;
  transition:opacity .2s,transform .2s;box-shadow:0 8px 24px rgba(0,0,0,.25)}
.demo-toast.on{opacity:1;transform:none}
.ewcbar .bt{align-items:center}
.ewcbar a.m{font-size:15.5px!important;padding:0 22px!important}
@media(max-width:899px){.ewcbar .bt{flex-direction:column;gap:8px}.ewcbar .bt a{width:100%;min-height:46px;font-size:14.5px!important;padding:0 12px!important}}
@media(min-width:900px){.ewcbar .in>p{min-width:0;flex:1 1 0!important}.ewcbar .bt{flex:none!important;max-width:none!important;width:auto!important}}
/* LINE はメールと同じ大きさの緑のボタン（2026-11-17 松本さん「前と同じ、同じ大きさの2つのボタンに戻す」） */
.ewcbar a.l{font-size:15.5px!important;padding:0 22px!important}
@media(min-width:900px){.ewcbar .bt{display:grid!important;grid-template-columns:1fr 1fr}}   /* 2つのボタンを同じ幅に（2026-11-22） */
@media(max-width:599px){.via{display:none}}
.ewcbar a .via{margin-left:-8px}
"""
DEMO_JS = """<script>
(function(){var t;document.addEventListener('click',function(ev){var a=ev.target.closest&&ev.target.closest('a[data-demo]');if(!a)return;
ev.preventDefault();if(!t){t=document.createElement('div');t.className='demo-toast';t.setAttribute('role','status');document.body.appendChild(t);}
t.textContent='見本のため、このボタンは押してもつながりません。公開後は御社のお電話につながります。';
t.classList.add('on');clearTimeout(t._h);t._h=setTimeout(function(){t.classList.remove('on');},2600);});})();
</script>"""


def apply_demo(html, d):
    """見本の中の電話をデモ表示に、EasyWebCraft へのボタンを1つにまとめる（trial_intro から呼ぶ）。"""
    import re
    import modern
    short = modern.short_name(d["name"])
    # 見本の範囲：ヘッダーの直前から、EWC の提案の説明（pintro）の直前まで
    a = html.find('<div class="hdwrap')
    b = html.find('<section class="pintro"')
    if a < 0 or b < 0:
        raise SystemExit("見本の範囲が見つからない")
    sample = html[a:b]
    # 丸い相談ボタン（見本の中の #contact へ飛ぶもの）を外す
    sample = re.sub(r'\n?<a class="badge".*?</a>', "", sample, count=1, flags=re.S)
    # 電話のリンク：ボタンはデモ表示に、会社概要の表の番号はただの文字に
    sample = re.sub(r'<a href="tel:[^"]*">([^<]*)</a>', r"\1", sample)
    sample = re.sub(r'<a (class="[^"]*") href="tel:[^"]*">', r'<a \1 href="#" data-demo aria-disabled="true">', sample)
    old_note = ('<span class="ph">見本の電話のボタンは、</span><span class="ph">御社の電話番号につながります。</span>')
    if old_note not in sample:
        raise SystemExit("見本の注意書きが見つからない")
    sample = sample.replace(old_note, '<span class="ph">見本の電話のボタンはデモ表示で、</span><span class="ph">押してもつながりません。</span>'
                                      '<span class="ph">公開後は御社のお電話につながります。</span>')
    frame = (f'<div class="pframe">\n<p class="pf-lab">ここからは公開後のサイトイメージ<small>{e(short)}様のトップページの見本</small></p>\n'
             + sample.rstrip() + '\n<p class="pf-end">サイトイメージはここまで<small>この下は EasyWebCraft からのご案内です</small></p>\n</div>\n')
    html = html[:a] + frame + html[b:]
    # 画面下の帯：文は短く、主ボタンは「EasyWebCraftに制作内容を質問する」の1つ。LINE は文字のリンク
    bar = re.search(r'(<div class="ewcbar".*?<div class="in">\s*)<p>.*?</p>(\s*<div class="bt">)(<a class="m" href="[^"]*">)(<svg.*?</svg>)[^<]*</a>(<a class="l"[^>]*>)(<svg.*?</svg>)[^<]*</a>', html, re.S)
    if not bar:
        raise SystemExit("画面下の帯が見つからない")
    p = (f'<p><b>{e(short)}様向けのリニューアル案です（EasyWebCraft 作成）。</b>'
         f'<br><i>{e(modern.EWC_PRICE)}</i> <span>EasyWebCraft　担当：{e(modern.EWC_STAFF)}</span></p>')
    html = (html[:bar.start()] + bar.group(1) + p + bar.group(2) + bar.group(3) + bar.group(4) + ASK_LABEL + "</a>"
            + bar.group(5) + bar.group(6) + LINE_LABEL + "</a>" + html[bar.end():])
    html = html.replace("</style>", DEMO_CSS + "</style>", 1)
    html = html.replace("</body>", DEMO_JS + "\n</body>", 1)
    return html


def trial_intro(sid):
    """提案の説明を見本の前に置いた試作を <キー>-intro/ に作る。今の見本（<キー>/）は変えない（2026-11-17）。"""
    root = pathlib.Path(__file__).resolve().parent
    d = json.loads((root / "sites.json").read_text(encoding="utf-8"))[sid]
    html = render(sid, d)
    if INDUSTRY[d["industry"]].get("layout") == "modern":
        html = apply_pick(html, d)
    html = apply_intro(apply_fast(html), d)
    out = root / (sid + "-intro")
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"  {sid}-intro  {d['name']}  {len(html)} バイト（提案の説明つきの試作）")


def apply_intro(html, d):
    """提案の説明・制作範囲と料金を末尾に、宛名を冒頭の演出に入れ、見本を枠で囲んで電話をデモ表示にする。
    2026-11-17 に試作から写真のある型の全見本へ（松本さん「全てに公開して」）。冒頭の演出が無い型（士業など）には使えない。"""
    import re
    # お作りするページは、見本の「サイトの構成」と同じもの
    sm = re.search(r'<section class="sitemap" id="sitemap">.*?<ul>(.*?)</ul>', html, re.S)
    pages = [H.unescape(x) for x in re.findall(r"<a [^>]*>(.*?)</a>", sm.group(1))] if sm else []
    pages = [x for x in pages if x != "トップページ"]
    html = html.replace("</style>", INTRO_CSS + "</style>", 1)   # 先に入れる（あとで入れると差し込み位置がずれる）
    # 置き場所は末尾、「制作範囲・料金」のすぐ上にまとめる（2026-11-17 松本さん。最初の画面の下 → フッターへ）。
    #   一番上だと冒頭の演出とのつながりが合わないので、冒頭の演出には「〇〇様へのご提案」の一言だけを添える
    if html.count("<footer>") != 1 or html.count('<span class="ewl-skip">') != 1:
        raise SystemExit(f"{d['name']}：差し込む場所が見つからない")
    # 見本の「サイトの構成」は、末尾の「お作りするページ」と同じ中身なので外す（二重に見せない）
    html = re.sub(r'<section class="sitemap" id="sitemap">.*?</section>\s*', "", html, count=1, flags=re.S)
    html = html.replace("<footer>", intro_html(d) + plan_html(d, pages) + "<footer>", 1)
    to = f'<p class="ewl-to"><span>{e(d["name"])}様への</span><span>ご提案</span></p>'
    html = html.replace('<span class="ewl-skip">', to + '\n  <span class="ewl-skip">', 1)
    return apply_demo(html, d)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--intro":
        for k in sys.argv[2:]:
            trial_intro(k)
        sys.exit()
    if len(sys.argv) > 2 and sys.argv[1] == "--fast":
        for k in sys.argv[2:]:
            trial_fast(k)
        sys.exit()
    if len(sys.argv) > 2 and sys.argv[1] == "--pick":
        for k in sys.argv[2:]:
            trial_pick(k)
        sys.exit()
    if len(sys.argv) > 2 and sys.argv[1] == "--trial":
        trial(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == "--3d":
        trial_3d(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == "--v3":
        trial_v3(sys.argv[2])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else None)
