"""見本に入れる「無難なJS」の候補を、実際のページで試すためのサンプル生成。

生成済みの index.html に <script> と少しのCSSを差し込むだけで、modern.py は触らない。
採用が決まったら、その番号のものを modern.py 側に移す。

    python3 js_samples.py     # js-sample/ 以下に k1..k6, kall, s1..s6, sall と一覧を作る

決まりごと（候補を出したときの条件）:
  - 外部リソースを読み込まない（1ファイル完結のまま）
  - JSが無効でも今と同じ見た目（消えたまま・隠れたままにしない）
  - prefers-reduced-motion のときは動かさない
  - 印刷に影響しない
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "js-sample")

#: 見本にする2ページ（建設の型・製造の型を1つずつ）
BASES = {"k": "setta", "s": "okamoto8"}

# ---------------------------------------------------------------------------
# 候補。(番号, 名前, 説明, CSS, JS) の順。CSS/JS は全部インラインで入れる。
# JSが動いた時だけ効かせたい CSS は、先頭で html に付ける .js を条件にする。
# ---------------------------------------------------------------------------

BOOT = "document.documentElement.classList.add('js');"
NOMOTION = "var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;"

CAND = {}

CAND[1] = ("スクロールで節がふわっと現れる", """
@media(prefers-reduced-motion:no-preference){
  .js .rv{opacity:0;transform:translateY(18px);transition:opacity .7s ease,transform .7s ease}
  .js .rv.in{opacity:1;transform:none}
}
@media print{.rv{opacity:1!important;transform:none!important}}
""", """
(function(){
  if(reduce||!('IntersectionObserver' in window))return;
  var sel='.sechead,.card,.step,.gframe,.stats div,.info,.mapbox,.news .pill';
  var els=document.querySelectorAll(sel);
  // 同じ親の中では少しずつ遅らせて、順に出す
  var seen=new Map();
  els.forEach(function(el){
    var p=el.parentNode,n=seen.get(p)||0;seen.set(p,n+1);
    el.classList.add('rv');el.style.transitionDelay=(Math.min(n,5)*80)+'ms';
  });
  var io=new IntersectionObserver(function(es){
    es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});
  },{threshold:.12,rootMargin:'0px 0px -6% 0px'});
  els.forEach(function(el){io.observe(el);});
})();
""")

CAND[2] = ("数字のカウントアップ", "", """
(function(){
  if(reduce||!('IntersectionObserver' in window))return;
  var bs=document.querySelectorAll('.stats b');
  var io=new IntersectionObserver(function(es){
    es.forEach(function(x){
      if(!x.isIntersecting)return;io.unobserve(x.target);
      var t=x.target.firstChild;if(!t||t.nodeType!==3)return;
      var raw=t.nodeValue.trim(),n=parseInt(raw.replace(/,/g,''),10);
      if(!/^[0-9,]+$/.test(raw)||isNaN(n))return;   // 「一級」「自社」などは動かさない
      var from=n>1000?n-48:0,t0=null,dur=1100,comma=raw.indexOf(',')>=0;
      function step(ts){
        if(t0===null)t0=ts;var p=Math.min(1,(ts-t0)/dur);p=1-Math.pow(1-p,3);
        var v=Math.round(from+(n-from)*p);
        t.nodeValue=comma?v.toLocaleString('ja-JP'):String(v);
        if(p<1)requestAnimationFrame(step);
      }
      t.nodeValue=String(from);requestAnimationFrame(step);
    });
  },{threshold:.6});
  bs.forEach(function(b){io.observe(b);});
})();
""")

CAND[3] = ("メニューの現在地ハイライト", """
nav a{transition:color .2s}
nav a.on{color:var(--accent);text-decoration:underline;text-underline-offset:.45em;
         text-decoration-thickness:2px}
@media print{nav a.on{text-decoration:none}}
""", """
(function(){
  var links=[].slice.call(document.querySelectorAll('nav a[href^="#"]'));
  var targets=[];
  links.forEach(function(a){
    var id=a.getAttribute('href').slice(1),el=id&&document.getElementById(id);
    if(el&&targets.indexOf(el)<0)targets.push(el);
  });
  if(!targets.length)return;
  targets.sort(function(a,b){return a.compareDocumentPosition(b)&4?-1:1;});
  var ticking=false;
  function update(){
    ticking=false;
    var line=innerHeight*0.38,cur=null;
    // 画面の上から 38% の線を越えている中で、いちばん下にあるもの＝いま見ている場所
    targets.forEach(function(el){if(el.getBoundingClientRect().top<=line)cur=el;});
    if(innerHeight+scrollY>=document.body.scrollHeight-2)cur=targets[targets.length-1];
    links.forEach(function(a){a.classList.toggle('on',!!cur&&a.getAttribute('href')==='#'+cur.id);});
  }
  addEventListener('scroll',function(){if(!ticking){ticking=true;requestAnimationFrame(update);}},{passive:true});
  update();
})();
""")

CAND[4] = ("ヘッダーがスクロールで細くなる", """
.hd,.hd .call,.hd .call2,.logo{transition:min-height .25s,padding .25s,font-size .25s}
header{transition:box-shadow .25s}
.js .sc header{box-shadow:0 8px 24px rgba(40,50,45,.12)}
.js .sc .hd{min-height:44px}
.js .sc .hd .call,.js .sc .hd .call2{padding-top:7px;padding-bottom:7px}
@media(min-width:900px){.js .sc .logo{font-size:15px}}
@media(prefers-reduced-motion:reduce){.hd,.hd .call,.hd .call2,.logo,header{transition:none}}
""", """
(function(){
  var w=document.querySelector('.hdwrap');if(!w)return;
  var on=false,ticking=false;
  function update(){
    ticking=false;var s=scrollY>48;
    if(s!==on){on=s;w.classList.toggle('sc',s);}
  }
  addEventListener('scroll',function(){if(!ticking){ticking=true;requestAnimationFrame(update);}},{passive:true});
  update();
})();
""")

CAND[5] = ("ページの上へ戻るボタン", """
.totop{position:fixed;left:14px;bottom:14px;z-index:45;width:44px;height:44px;border-radius:50%;
       background:var(--paper);border:1px solid var(--line);box-shadow:0 4px 14px rgba(40,50,45,.14);
       display:grid;place-items:center;color:var(--accent);text-decoration:none;
       opacity:0;pointer-events:none;transform:translateY(8px);transition:opacity .3s,transform .3s}
.totop.show{opacity:1;pointer-events:auto;transform:none}
.totop svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
@media(prefers-reduced-motion:reduce){.totop{transition:none}}
@media print{.totop{display:none}}
""", """
(function(){
  var a=document.createElement('a');a.className='totop';a.href='#';a.setAttribute('aria-label','ページの上へ');
  a.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 14l6-6 6 6"/></svg>';
  document.body.appendChild(a);
  a.addEventListener('click',function(ev){ev.preventDefault();scrollTo({top:0,behavior:reduce?'auto':'smooth'});});
  var ticking=false;
  function update(){ticking=false;a.classList.toggle('show',scrollY>innerHeight*0.8);}
  addEventListener('scroll',function(){if(!ticking){ticking=true;requestAnimationFrame(update);}},{passive:true});
  update();
})();
""")

# 6 だけは、ページごとに違うメニューの折り返し幅（navbp）を CSS に埋める
CAND[6] = ("スマホのメニューをハンバーガーに", """
/* 390px 幅で 社名＋電話＋ボタン が1段に収まるよう、アイコンの下に小さく「メニュー」 */
.mbtn{display:none;order:2;flex-direction:column;align-items:center;gap:4px;background:none;
      border:0;padding:4px 6px;font:inherit;font-size:9px;font-weight:700;
      letter-spacing:.04em;color:var(--ink);cursor:pointer;line-height:1}
.mbtn i{display:block;width:20px;height:14px;position:relative}
.mbtn i::before,.mbtn i::after,.mbtn i span{content:"";position:absolute;left:0;right:0;height:2px;
      background:currentColor;border-radius:2px;transition:transform .25s,opacity .2s}
.mbtn i::before{top:0}.mbtn i span{top:6px}.mbtn i::after{bottom:0}
.hd.open .mbtn i::before{transform:translateY(6px) rotate(45deg)}
.hd.open .mbtn i span{opacity:0}
.hd.open .mbtn i::after{transform:translateY(-6px) rotate(-45deg)}
@media(max-width:%(navbp_max)spx){
  .js .mbtn{display:inline-flex}
  .js nav{display:none;flex-direction:column;row-gap:0;font-size:14px;padding:4px 0 6px}
  .js nav a{padding:10px 4px;border-bottom:1px dashed var(--line);color:var(--ink)}
  .js nav a:last-child{border-bottom:0}
  .js .hd.open nav{display:flex}
}
@media(prefers-reduced-motion:reduce){.mbtn i::before,.mbtn i::after,.mbtn i span{transition:none}}
@media print{.mbtn{display:none}nav{display:flex!important}}
""", """
(function(){
  var hd=document.querySelector('.hd'),nav=hd&&hd.querySelector('nav'),call=hd&&hd.querySelector('.call,.calls');
  if(!hd||!nav)return;
  var b=document.createElement('button');b.type='button';b.className='mbtn';
  b.setAttribute('aria-expanded','false');b.setAttribute('aria-controls','gnav');
  b.innerHTML='<i><span></span></i>メニュー';nav.id='gnav';
  hd.insertBefore(b,call||null);
  b.addEventListener('click',function(){
    var o=hd.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');
  });
  nav.addEventListener('click',function(ev){
    if(ev.target.tagName==='A'){hd.classList.remove('open');b.setAttribute('aria-expanded','false');}
  });
})();
""")

SETS = {str(n): [n] for n in CAND}
SETS["all"] = [1, 2, 3, 4]      # おすすめの組み合わせ


def navbp_of(html):
    m = re.search(r"@media\(min-width:(\d+)px\)\{\s*\.hd\{flex-wrap:nowrap", html)
    return int(m.group(1)) if m else 900


def inject(html, nums, label):
    css, js = [], [BOOT, NOMOTION]
    for n in nums:
        name, c, j = CAND[n]
        if n == 6:
            c = c % {"navbp_max": navbp_of(html) - 1}
        css.append(f"/* JS見本 {n}: {name} */" + c)
        js.append(f"// {n}: {name}" + j)
    style = "<style>" + "".join(css) + "</style>\n"
    script = "<script>\n" + "\n".join(js) + "\n</script>\n"
    html = html.replace("</head>", style + "</head>", 1)
    html = html.replace("</body>", script + "</body>", 1)
    # どの見本かが分かるように、断りの帯の頭に印を付ける
    html = html.replace("<b>これは EasyWebCraft が作成した提案用の見本です。</b>",
                        f"<b>【JS見本 {label}】これは EasyWebCraft が作成した提案用の見本です。</b>", 1)
    html = html.replace("<title>【提案見本】", f"<title>【JS見本 {label}】", 1)
    return html


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for key, sid in BASES.items():
        src = open(os.path.join(HERE, sid, "index.html"), encoding="utf-8").read()
        assert "<script" not in src, f"{sid} にはもう script がある"
        for tag, nums in SETS.items():
            label = ("1〜4（おすすめの組み合わせ）" if tag == "all"
                     else f"{tag}：{CAND[int(tag)][0]}")
            d = os.path.join(OUT, key + tag)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
                f.write(inject(src, nums, label))
            rows.append((key, tag, label))
    # 一覧
    base = "https://easywebcraft.github.io/ewc-proposals/js-sample/"
    li = {"k": [], "s": []}
    for key, tag, label in rows:
        li[key].append(f'<li><a href="{key}{tag}/">{label}</a></li>')
    page = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<title>JS見本の一覧｜EasyWebCraft（社内用）</title>
<style>body{{font-family:system-ui,sans-serif;max-width:720px;margin:32px auto;padding:0 16px;line-height:1.8;color:#222}}
h2{{font-size:16px;margin-top:28px;border-left:4px solid #2a5d4b;padding-left:10px}}
li{{margin:4px 0}}a{{color:#1a4f8a}}p.note{{font-size:13px;color:#555}}</style></head><body>
<h1 style="font-size:20px">見本に入れるJSの候補（社内用）</h1>
<p class="note">同じページに候補を1つずつ入れてあります。スマホでも開いて確かめてください。
「動きを減らす」をONにした端末では動かない設計です。</p>
<h2>建設の型（{BASES['k']}）</h2><ul>{''.join(li['k'])}</ul>
<h2>製造の型（{BASES['s']}）</h2><ul>{''.join(li['s'])}</ul>
</body></html>"""
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print(f"{len(rows)} 件 → {base}")


if __name__ == "__main__":
    main()
