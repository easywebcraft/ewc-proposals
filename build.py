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
import sys

# 業種ごとの色と言い回し。型はここだけ変えれば増やせる。
INDUSTRY = {
    "kensetsu": {"label": "建設・住宅", "layout": "modern",
                 "navy": "#1f3a5f", "navy_d": "#16293f", "accent": "#1f7a4d",
                 "ground": "#f3f1ea", "ink2": "#2f3a33",
                 "svc": "できること", "svc_lead": "住まいの小さな修繕から、大きな工事まで。",
                 "flow_h": "ご相談から完成まで",
                 "flow": [("ご相談・現地の確認", "お電話をいただいたあと、現地を拝見します。費用はかかりません。"),
                          ("ご提案・お見積り", "やり方が複数あるときは、費用と工期を並べてお出しします。"),
                          ("ご契約・着工", "工程をお渡ししてから始めます。近隣へのご挨拶も当社で行います。"),
                          ("お引渡し・その後", "お引渡しのあとも、気になるところが出たらご連絡ください。")],
                 "cta": "まずはお電話ください", "cta_sub": "「これは直せるのか」だけでも構いません。",
                 "hours": "受付時間 平日 8:00–17:00"},
    "seizo": {"label": "製造", "navy": "#26323c", "navy_d": "#171f27", "accent": "#c2703a",
              "svc": "できること", "svc_lead": "一点ものから、continuousな生産まで。",
              "flow_h": "ご発注までの流れ",
              "flow": [("ご相談", "図面が無い段階でも構いません。用途をお聞かせください。"),
                       ("お見積り", "数量と納期の見通しを添えてお出しします。"),
                       ("試作・ご確認", "かたちにしてから直すほうが早いこともあります。"),
                       ("量産・納品", "継続してご発注いただく場合の体制もご相談ください。")],
              "cta": "図面をお持ちでなくても", "cta_sub": "「こういうものが作れないか」からご相談ください。",
              "hours": "受付時間 平日 8:30–17:30"},
    "car": {"label": "自動車", "navy": "#1d3b4a", "navy_d": "#132836", "accent": "#c8552f",
            "svc": "できること", "svc_lead": "車検から、急なトラブルまで。",
            "flow_h": "車検・修理の流れ",
            "flow": [("ご連絡・ご来店", "お電話ください。動かないときは伺います。"),
                     ("お見積り", "何をどこまでやるかを、先にご説明します。"),
                     ("作業", "追加が要るときは、その都度ご相談してから進めます。"),
                     ("お引渡し", "やったことをご説明してからお返しします。")],
            "cta": "まずはお電話ください", "cta_sub": "動かないときも、そのままお電話ください。",
            "hours": "受付時間 8:00–18:00／日曜定休"},
    "clinic": {"label": "クリニック", "navy": "#1e5361", "navy_d": "#143b46", "accent": "#3f9a86",
               "svc": "診療のご案内", "svc_lead": "気になることがあれば、早めにご相談ください。",
               "flow_h": "受診の流れ",
               "flow": [("ご来院・受付", "保険証をお持ちください。はじめての方は問診票をご記入いただきます。"),
                        ("診察", "気になることは遠慮なくお話しください。"),
                        ("検査・ご説明", "必要な検査をご説明してから行います。"),
                        ("お会計・次回のご案内", "次にいつ来ていただくかをお伝えします。")],
               "cta": "お電話でご予約ください", "cta_sub": "急なご相談も、まずはお電話を。",
               "hours": "受付時間 平日 9:00–12:00／15:00–18:00"},
    "shigyo": {"label": "士業", "navy": "#26344a", "navy_d": "#1a2433", "accent": "#8a7a4f",
               "svc": "承っていること", "svc_lead": "小さな会社と、個人事業の方へ。",
               "flow_h": "ご相談からのお付き合い",
               "flow": [("初回のご相談", "顧問契約の前に、まずお話をうかがいます。費用はかかりません。"),
                        ("ご提案・お見積り", "何をどこまでお手伝いするかを、費用と一緒にお示しします。"),
                        ("毎月のお付き合い", "数字を見ながら、いまの状態をご説明します。"),
                        ("決算・申告", "期限に追われないよう、早めに段取りします。")],
               "cta": "まずはお話をお聞かせください", "cta_sub": "digitsの前に、事業のことから。",
               "hours": "受付時間 平日 9:00–17:00"},
    "chiryo": {"label": "治療院", "navy": "#2b4a3f", "navy_d": "#1c3128", "accent": "#c07a3e",
               "svc": "施術のご案内", "svc_lead": "痛みの出ている場所だけを見ません。",
               "flow_h": "はじめての方へ",
               "flow": [("ご予約", "お電話ください。当日でも空いていればお受けします。"),
                        ("お話をうかがう", "いつから、どんなときに痛むかを教えてください。"),
                        ("検査・ご説明", "姿勢を撮影して、原因になっている動きをお見せします。"),
                        ("施術・通院の目安", "何回くらいで変わるかをお伝えします。無理に続けさせません。")],
               "cta": "お電話でご予約ください", "cta_sub": "「これは治るのか」だけでも構いません。",
               "hours": "受付時間 平日 9:00–13:30／16:00–19:00　土 9:00–18:00"},
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
OVERRIDABLE = ("svc", "svc_lead", "flow_h", "cta", "cta_sub", "hours")


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
    <p class="lead">はじめての方にも、順番が分かるように。</p>
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
</div>

<footer>
  <span class="ph">この見本は EasyWebCraft が作成した提案資料です。</span><span class="ph">{e(name)}さまの公式サイトではありません。</span><br>
  <span class="ph">実際の制作では、</span><span class="ph">御社の写真・実績・文章に差し替えて仕上げます。</span>
  <p class="by"><span class="ph">EasyWebCraft（担当：田代）</span><span class="ph"><a href="mailto:info@easywebcraft.jp">info@easywebcraft.jp</a></span></p>
</footer>

</body>
</html>
"""


def main(only=None):
    root = pathlib.Path(__file__).resolve().parent
    sites = json.loads((root / "sites.json").read_text(encoding="utf-8"))
    for sid, d in sites.items():
        if only and sid != only:
            continue
        out = root / sid
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(render(sid, d), encoding="utf-8")
        print(f"  {sid:<14} {d['name'][:22]:<24} {len(render(sid, d)):>6} バイト")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
