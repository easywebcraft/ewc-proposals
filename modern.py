"""建設系の型（modern）。

参考にしたのは、大洋画地・SUZUKI KENSETU・TATSUSHO の
**書体・配色・余白の取り方・レイアウトの型**。HTML/CSS は自前で書いている。
3つに共通していたのは次の4点で、それを写真なしで成立させる形に置き換えた。

  1. 巨大な英字を「文字」ではなく「面」として置く（大洋画地・SUZUKI）
  2. 縦書きの明朝で品位を出す（TATSUSHO）
  3. 生成りの地に、線画や幾何形を薄く敷く（SUZUKI）
  4. 浮いた角丸のヘッダー、丸いCONTACTバッジ、scroll の合図（SUZUKI・TATSUSHO）

★写真は使えない（相手の写真を借りられない）。参考3社はいずれも写真が主役
  なので、そこは「お写真が入ります」と分かる枠として設計する。ごまかすより、
  提案として何が入るかを示すほうが伝わる。
"""
import html as H


def e(x):
    return H.escape(str(x or ""), quote=True)


CSS = """
:root{
  --ground:%(ground)s; --ink:%(ink2)s; --muted:#667069; --line:#ddd9cf;
  --accent:%(accent)s; --accent-d:%(accent_d)s; --paper:#fff;
  --serif:"Noto Serif JP","游明朝体","Yu Mincho",YuMincho,"ヒラギノ明朝 ProN W3",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Yu Gothic",Meiryo,
         "Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:var(--sans);color:var(--ink);background:var(--ground);
     line-height:1.9;-webkit-text-size-adjust:100%%;overflow-x:hidden}
a{color:inherit}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}

/* 見本であることの明示。閉じられない。 */
.notice{position:relative;z-index:60;background:var(--accent);color:#fff;
        font-size:13px;line-height:1.6;padding:9px 16px;text-align:center}
.notice b{font-weight:700}
.notice span{display:block;opacity:.92;font-size:12px}

/* ヘッダーは画面の端まで届く帯（2026-09-18・PCも）。
   角丸で浮かせる型（SUZUKI の型）は両端に隙間ができて「ずれている」ように見えるので
   スマホ・PCともやめた。中身だけ 1160px に揃える。 */
.hdwrap{position:sticky;top:0;z-index:50;padding:0}
header{background:rgba(255,255,255,.96);backdrop-filter:blur(8px);
       border-bottom:1px solid var(--line);box-shadow:0 2px 12px rgba(40,50,45,.06)}
.hd{display:flex;align-items:center;justify-content:space-between;gap:10px;
    min-height:54px;flex-wrap:wrap;max-width:1160px;margin:0 auto;padding:0 12px 0 16px}
.logo{font-family:var(--serif);font-size:15.5px;letter-spacing:.04em;font-weight:600;
      line-height:1.25;white-space:nowrap}
.logo small{display:block;font-family:var(--sans);font-size:9.5px;
            letter-spacing:.16em;color:var(--muted);font-weight:400}
/* 狭い画面ではヘッダーの2段目に折り返して全項目を出す。
   以前は display:none で、スマホではメニューが一切見えなかった。
   横スクロールにすると端で切れて「途中で終わっている」ように見えるので折り返す。 */
nav{display:flex;order:3;flex:1 0 100%%;flex-wrap:wrap;
    column-gap:14px;row-gap:5px;font-size:11.5px;letter-spacing:.02em;
    border-top:1px solid var(--line);margin:0 -4px;padding:7px 4px 9px}
nav a{text-decoration:none;color:var(--muted);white-space:nowrap}
nav a:hover{color:var(--accent)}
.hd .call{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;
          border-radius:999px;padding:10px 15px;font-size:12.5px;font-weight:700;
          letter-spacing:.06em;white-space:nowrap}
.hd .call:hover{background:var(--accent-d)}

/* ヒーロー。巨大英字を面として敷き、縦書きの明朝を重ねる。 */
.hero{position:relative;padding:26px 0 12px;overflow:hidden}
/* 線画の地（SUZUKI の型を、街の輪郭ではなく等高線で） */
.hero::before{content:"";position:absolute;inset:0;pointer-events:none;
  background-image:repeating-linear-gradient(115deg,rgba(%(acc_rgb)s,.055) 0 1px,transparent 1px 42px);}
/* 業種の質感。上に行くほど薄くして、見出しの邪魔をしないようにする */
.tex{position:absolute;inset:0;width:100%%;height:100%%;pointer-events:none;
     -webkit-mask-image:linear-gradient(180deg,rgba(0,0,0,.35) 0%%,#000 30%%,rgba(0,0,0,0) 86%%);
     mask-image:linear-gradient(180deg,rgba(0,0,0,.35) 0%%,#000 30%%,rgba(0,0,0,0) 86%%)}
.hero.tx::before{display:none}   /* 等高線の地とは重ねない */
.contact.tx{position:relative;overflow:hidden}
.contact.tx>*{position:relative;z-index:1}
.tex.ctex{opacity:.85;
  -webkit-mask-image:linear-gradient(180deg,#000 0%%,rgba(0,0,0,.22) 58%%,rgba(0,0,0,0) 100%%);
  mask-image:linear-gradient(180deg,#000 0%%,rgba(0,0,0,.22) 58%%,rgba(0,0,0,0) 100%%)}
.hero .inner{position:relative;display:grid;gap:22px;padding:18px 0 0}
.hero .textcol{display:flex;flex-direction:column}
.hero .textcol h1{order:-1}   /* 狭い画面では見出しを先頭に */
.vt{writing-mode:horizontal-tb}
.hero h1{font-family:var(--serif);font-weight:500;margin:0;
         font-size:clamp(27px,7.4vw,40px);line-height:1.65;letter-spacing:.06em}
.hero h1 em{font-style:normal;color:var(--accent)}
.hero .sub{margin:16px 0 0;color:var(--muted);font-size:14.5px;max-width:30em}
.ph{display:inline-block}
.notice .ph,footer .ph{display:inline-block;margin-right:.15em}
footer .by{margin:14px 0 0;font-size:11.5px}
footer .by .ph{margin:0 .5em}
footer .by a{color:inherit;text-decoration:underline;text-underline-offset:2px}
.hero .en{margin:10px 0 0;font-size:11px;letter-spacing:.22em;color:var(--muted)}
.hero .acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.btn{display:inline-block;text-decoration:none;border-radius:999px;white-space:nowrap;
     padding:14px 26px;font-size:14.5px;font-weight:700;letter-spacing:.05em}
.btn.p{background:var(--accent);color:#fff}
.btn.p:hover{background:var(--accent-d)}
.btn.g{border:1px solid var(--line);background:var(--paper);color:var(--ink)}
.btn.g:hover{border-color:var(--accent);color:var(--accent)}

/* 写真の枠。ごまかさず「ここに入る」と書く。 */
.shot{position:relative;background:
      linear-gradient(135deg,#eae7de 0%%,#e3e1d8 55%%,#edebe3 100%%);
      border:1px solid var(--line);border-radius:10px;aspect-ratio:4/3;
      display:grid;place-items:center;text-align:center;overflow:hidden}
.shot::after{content:"";position:absolute;inset:0;
  background-image:repeating-linear-gradient(45deg,rgba(255,255,255,.5) 0 2px,transparent 2px 12px)}
.shot .lb{position:relative;z-index:1;color:#6f7268;font-size:12.5px;letter-spacing:.08em}
.shot .lb b{display:block;font-family:var(--serif);font-size:15px;color:#575a51;
            margin-bottom:5px;font-weight:500}
/* 実績・事例の写真枠。ヒーローの枠と同じ見た目でそろえる */
/* 地図の入る場所。写真枠と同じ見せ方でそろえる */
.mapbox{margin-top:22px;background:
        linear-gradient(135deg,#eae7de 0%%,#e3e1d8 55%%,#edebe3 100%%);
        border:1px solid var(--line);border-radius:10px;aspect-ratio:16/7;
        display:grid;place-items:center;align-content:center;text-align:center;
        color:#6f7268;font-size:11.5px;letter-spacing:.06em}
.mapbox b{display:block;font-family:var(--serif);font-size:14px;color:#575a51;
          margin-bottom:4px;font-weight:500}
.gal{display:grid;gap:14px}
.gframe{position:relative;background:
        linear-gradient(135deg,#eae7de 0%%,#e3e1d8 55%%,#edebe3 100%%);
        border:1px solid var(--line);border-radius:10px;aspect-ratio:4/3;
        display:grid;place-items:center;align-content:center;text-align:center;
        color:#6f7268;font-size:12px;letter-spacing:.06em;padding:0 14px}
.gframe{position:relative;overflow:hidden}
.gframe::after{content:"";position:absolute;inset:0;pointer-events:none;
  background-image:repeating-linear-gradient(45deg,rgba(255,255,255,.45) 0 2px,transparent 2px 12px)}
.gframe>*,.gframe b{position:relative;z-index:1}
.gframe b{display:block;font-family:var(--serif);font-size:14px;color:#575a51;
          margin-bottom:4px;font-weight:500}
.scroll{display:none;position:absolute;left:50%%;transform:translateX(-50%%);
        bottom:-2px;font-size:10px;
        letter-spacing:.2em;color:var(--muted)}

/* TATSUSHO の型（画面から・2026-09-19）: 写真の外側に細い罫の枠をもう一つ置く */
.shot{outline:1px solid rgba(%(acc_rgb)s,.35);outline-offset:8px}
/* TATSUSHO の型: 写真の右下に、お知らせを1行のピルで。日付・題名・矢印 */
.news{padding:14px 0 0}
.news .pill{display:flex;align-items:center;gap:12px;background:var(--paper);
  border:1px solid var(--line);border-radius:999px;padding:9px 16px 9px 14px;font-size:12.5px;
  max-width:560px;margin-left:auto}
.news .pill .dot{width:7px;height:7px;border-radius:50%%;background:var(--accent);flex:none}
.news .pill .date{color:var(--muted);letter-spacing:.06em;font-variant-numeric:tabular-nums;flex:none}
.news .pill .t{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.news .pill .more{margin-left:auto;flex:none;color:var(--accent);font-weight:700;text-decoration:none;
  font-size:11px;letter-spacing:.14em}
/* TATSUSHO の型: 左端に細い縦書きの一言（広い画面だけ） */
.tagline{display:none}
/* TATSUSHO の型: 丸い CONTACT のバッジ。文字を円に沿わせ、中に一言 */
.badge{display:none}
/* scroll の合図に縦の線と点 */
.scroll::after{content:"";display:block;width:1px;height:26px;margin:6px auto 0;
  background:linear-gradient(180deg,var(--accent),transparent)}

/* 帯（数字） */
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;
       margin:26px 0 0}
.stats div{background:var(--paper);border:1px solid var(--line);border-radius:8px;
           padding:18px 8px;text-align:center}
.stats b{display:block;font-family:var(--serif);font-size:34px;color:var(--accent);
         line-height:1.15;letter-spacing:.01em}
.stats b small{font-size:13px;margin-left:2px}
.stats span{display:block;margin-top:6px;font-size:11.5px;color:var(--muted);
            letter-spacing:.08em}

section{padding:60px 0}
section.alt{background:var(--paper)}
.sechead{text-align:center;margin-bottom:34px}
.sechead .en{font-size:10.5px;letter-spacing:.28em;color:var(--accent);display:block;
             margin-bottom:8px}
h2{font-family:var(--serif);font-weight:500;font-size:clamp(21px,5.4vw,28px);
   letter-spacing:.07em;margin:0}
.sechead p{color:var(--muted);font-size:13.5px;margin:10px 0 0}

.cards{display:flex;flex-wrap:wrap;justify-content:center;gap:14px}
.card{flex:0 1 100%%;min-width:0;
      background:var(--paper);border:1px solid var(--line);border-radius:10px;
      padding:24px 22px;position:relative;overflow:hidden}
section.alt .card{background:var(--ground)}
.card h3{font-size:16.5px;margin:0 0 9px;letter-spacing:.04em}
.card p{margin:0;font-size:13.5px;color:var(--muted)}

.flow{display:grid;gap:12px;counter-reset:s}
.step{background:var(--paper);border:1px solid var(--line);border-radius:10px;
      padding:20px 20px 20px 60px;position:relative}
section.alt .step{background:var(--ground)}
.step::before{counter-increment:s;content:"0" counter(s);position:absolute;left:18px;top:19px;
              font-family:var(--serif);font-size:14px;color:var(--accent);letter-spacing:.04em}
.step h3{font-size:15.5px;margin:0 0 5px}
.step p{margin:0;font-size:13px;color:var(--muted)}

table.info{width:100%%;border-collapse:collapse;font-size:14px}
table.info th,table.info td{border-bottom:1px solid var(--line);padding:14px 4px;
                            text-align:left;vertical-align:top}
table.info th{width:7.5em;color:var(--muted);font-weight:500}

/* 丸いCONTACTバッジ（TATSUSHO の型） */
.contact{position:relative;background:var(--accent);color:#fff;text-align:center;
         padding:56px 20px;overflow:hidden}
.contact::before{content:"";position:absolute;inset:auto -18%% -55%% 55%%;height:90%%;
  border-radius:50%%;background:rgba(255,255,255,.06)}
.contact h2{color:#fff;position:relative}
.contact p{color:rgba(255,255,255,.85);font-size:13.5px;margin:10px 0 20px;position:relative}
.contact .big{position:relative;font-family:var(--serif);font-size:clamp(27px,8vw,36px);
              letter-spacing:.05em;text-decoration:none;color:#fff;display:inline-block}
.contact small{display:block;font-size:11.5px;opacity:.8;margin:6px 0 20px;position:relative}
.contact .btn.w{background:#fff;color:var(--accent);position:relative}

footer{background:#242c27;color:rgba(255,255,255,.6);font-size:11.5px;
       padding:26px 20px;text-align:center;line-height:1.9}

@media(min-width:%(navbp)spx){
  .hd{flex-wrap:nowrap;min-height:58px;padding:0 20px}
  .logo{font-size:17px;letter-spacing:.08em}
  .hd .call{padding:11px 20px;font-size:13.5px}
  nav{order:0;flex:0 1 auto;flex-wrap:nowrap;column-gap:22px;
      font-size:13.5px;letter-spacing:.06em;border-top:0;margin:0;padding:0}
}

@media(min-width:900px){
  .gal{grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:18px}
  .gframe:first-child{grid-column:span 2;grid-row:span 2;aspect-ratio:auto}
  .hero{padding:34px 0 20px}
  .hero .inner{grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);
               align-items:center;gap:46px;padding:34px 0 46px}
  /* 縦書きの明朝（TATSUSHO の型）。広い画面のときだけ。 */
  .vt{writing-mode:vertical-rl;text-orientation:upright;
      max-height:470px;margin-left:auto;white-space:nowrap}
  .hero h1{line-height:2.0;letter-spacing:.14em;font-size:%(h1px)spx}
  .hero .sub,.hero .en,.hero .acts{writing-mode:horizontal-tb}
  .hero .side{display:flex;flex-direction:column;align-items:flex-end;gap:0}
  .hero .textcol{flex-direction:row;gap:26px;justify-content:flex-end}
  .hero .textcol h1{order:0}
  .hero .meta{max-width:21em}
  .scroll{display:block}
  .tagline{display:block;position:absolute;left:14px;top:40px;writing-mode:vertical-rl;
    font-size:10.5px;letter-spacing:.24em;color:var(--muted);margin:0;padding-top:26px}
  .tagline::before{content:"";position:absolute;left:50%%;top:0;width:1px;height:18px;background:var(--muted)}
  .badge{display:grid;place-items:center;position:fixed;right:22px;bottom:22px;z-index:40;
    width:104px;height:104px;border-radius:50%%;background:var(--accent);color:#fff;
    text-decoration:none;box-shadow:0 8px 24px rgba(%(acc_rgb)s,.35)}
  .badge svg{position:absolute;inset:0;width:100%%;height:100%%;animation:spin 24s linear infinite}
  .badge svg text{fill:rgba(255,255,255,.8);font-size:9.5px;letter-spacing:.3em;font-family:var(--sans)}
  .badge span{position:relative;font-size:11.5px;font-weight:700;letter-spacing:.06em;text-align:center;line-height:1.5}
  .badge span::before{content:"✉";display:block;font-size:15px;font-weight:400}
  @keyframes spin{to{transform:rotate(360deg)}}
  @media(prefers-reduced-motion:reduce){.badge svg{animation:none}}
  .cards{gap:16px}
  .card{flex:0 1 calc((100%% - 32px) / 3)}
  .flow{grid-template-columns:repeat(4,1fr)}
  section{padding:84px 0}
  .stats{gap:14px}
  .stats b{font-size:42px}
}

/* ★紙に出したときのため。提案資料は社内で回覧されることがある。
   印刷では背景色が落ちるので、**濃い地に白抜きの箇所がそのままだと消える**。
   とくに断り書きの帯（見本であることの表示）が消えるのは致命的なので、
   白地＋黒文字＋太い枠に置き換える。 */
@media print{
  html,body{background:#fff}
  .hdwrap{position:static;padding:0 0 8px}
  header{box-shadow:none;border:1px solid var(--line);backdrop-filter:none}
  .notice{position:static;background:#fff;color:#000;border:2px solid #000;
          padding:8px 12px;margin-bottom:10px}
  .notice b{color:#000}
  .tex,.scroll,.badge,.tagline{display:none}
  .shot{outline:0}
  .contact{background:#fff;color:var(--ink);
           border-top:2px solid var(--line);border-bottom:2px solid var(--line)}
  .contact .big{color:var(--ink)}
  .contact .btn.w{background:#fff;color:var(--ink);border:1px solid var(--ink)}
  footer{background:#fff;color:#333;border-top:1px solid var(--line)}
  footer .by a{color:#333}
  /* 紙では押せないので、当社のリンク先を文字で出す */
  footer .by a[href^="http"]::after{content:" (" attr(href) ")"}
  .card,.step,.gframe,.mapbox,.shot,.stats div{break-inside:avoid;page-break-inside:avoid}
  section{padding:26px 0}
  .hero{padding:6px 0 0}
  @page{margin:14mm}
}
"""


# ★動き（2026-09-19）。かみのて（~/kaminote-design）と同じ作り。候補を8つ比べて 7＋8 を採用。
#   ・ヒーローはJSを使わず CSS だけで立ち上がる（クラスを待つと、待つ間に文字が見えてしまう）
#   ・下の節は <head> の script で最初の描画より前に隠し（.anim）、スクロールで順に出す
#   ・JSが途中で止まっても消えたままにしない保険が2重（head側 4秒、body側 5秒）
#   ・「動きを減らす」設定と印刷では全部止まる。外部リソースは読み込まない
#   ★隠す対象（REVEAL_SEL）は CSS と JS で同じ並びを使う。食い違うと隠れたまま出ない要素ができる
REVEAL_SEL = ".stats > *,.sechead,.cards > *,.gal > *,.flow > *,.info,.mapbox,.news .pill"

MOTION_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes riseSp{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:none}}
@keyframes popIn{from{opacity:0;transform:scale(.97)}to{opacity:1;transform:none}}
.hero .meta > *,.hero h1{animation:rise .7s cubic-bezier(.2,.7,.3,1) both}
.hero h1{animation-delay:.1s}
.hero .meta > :nth-child(1){animation-delay:.25s}
.hero .meta > :nth-child(2){animation-delay:.4s}
.hero .meta > :nth-child(3){animation-delay:.55s}
.hero .shot{animation:popIn 1s cubic-bezier(.2,.7,.3,1) .45s both}
.anim :is(SEL){opacity:0}
.anim .on{animation:rise .7s cubic-bezier(.2,.7,.3,1) both}
@media(max-width:700px){.anim .on{animation-name:riseSp}}
/* スマホのメニュー開閉。社名＋電話＋ボタンが 390px 幅で1段に収まるよう、アイコンの下に小さく「メニュー」 */
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
@media(max-width:NAVMAXpx){
  .js .mbtn{display:inline-flex}
  .js nav{display:none;flex-direction:column;row-gap:0;font-size:14px;padding:4px 0 6px}
  .js nav a{padding:10px 4px;border-bottom:1px dashed var(--line);color:var(--ink)}
  .js nav a:last-child{border-bottom:0}
  .js .hd.open nav{display:flex}
}
@media(prefers-reduced-motion:reduce){
  .anim :is(SEL){opacity:1}
  .anim .on,.hero .meta > *,.hero h1,.hero .shot{animation:none}
  .mbtn i::before,.mbtn i::after,.mbtn i span{transition:none}
}
@media print{
  .anim :is(SEL){opacity:1!important}
  .anim .on,.hero .meta > *,.hero h1,.hero .shot{animation:none!important}
  .mbtn{display:none}nav{display:flex!important}
}
"""

# <head> に入れる分。最初の描画より前に付ける（あとから付けると、見えていたものが消えてから動く）
HEAD_JS = """<script>
document.documentElement.classList.add('anim','js');
// 保険: 下のJSが動かなかったときは、隠したまま・メニューを消したままにしない
setTimeout(function(){if(!window.__animReady){document.documentElement.classList.remove('anim','js');}},4000);
</script>"""

BODY_JS = """<script>
// スクロールで出てくる動き。隠す指定は <head> の CSS 側（.anim）。ここでは出す順番だけを決める
(function(){
  var units=[].slice.call(document.querySelectorAll('SEL'));
  function sweep(){
    var vh=innerHeight||document.documentElement.clientHeight,shown=[];
    for(var i=units.length-1;i>=0;i--){
      var r=units[i].getBoundingClientRect();
      if(r.top<vh*0.92&&r.bottom>0){shown.push(units[i]);units.splice(i,1);}  // 一度出したら見張らない
    }
    if(!shown.length)return;
    shown.sort(function(a,b){return a.getBoundingClientRect().top-b.getBoundingClientRect().top;})
      .forEach(function(el,i){el.style.animationDelay=(i*0.06)+'s';el.classList.add('on');});
    if(!units.length){removeEventListener('scroll',onScroll);removeEventListener('resize',onScroll);}
  }
  var waiting=false;
  function onScroll(){if(waiting)return;waiting=true;requestAnimationFrame(function(){waiting=false;sweep();});}
  addEventListener('scroll',onScroll,{passive:true});
  addEventListener('resize',onScroll);
  sweep();                                  // 最初から見えている分
  addEventListener('load',sweep);
  // 保険: スクロールを拾えない環境でも、文字が消えたままにはしない
  setTimeout(function(){units.forEach(function(el){el.classList.add('on');});units.length=0;},5000);
})();
// スマホのメニュー開閉。外を押す／項目を押す／Esc で閉じ、幅を広げてボタンが消えたら閉じる
(function(){
  var hd=document.querySelector('.hd'),nav=hd&&hd.querySelector('nav'),call=hd&&hd.querySelector('.call,.calls');
  if(!hd||!nav)return;
  var b=document.createElement('button');b.type='button';b.className='mbtn';
  b.setAttribute('aria-expanded','false');b.setAttribute('aria-controls','gnav');
  b.innerHTML='<i><span></span></i>メニュー';nav.id='gnav';
  hd.insertBefore(b,call||null);
  function close(){hd.classList.remove('open');b.setAttribute('aria-expanded','false');}
  b.addEventListener('click',function(e){
    e.stopPropagation();
    var o=!hd.classList.contains('open');hd.classList.toggle('open',o);
    b.setAttribute('aria-expanded',o?'true':'false');
  });
  document.addEventListener('click',function(e){if(hd.classList.contains('open')&&!hd.contains(e.target))close();});
  nav.addEventListener('click',function(e){if(e.target.closest('a'))close();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
  addEventListener('resize',function(){if(getComputedStyle(b).display==='none')close();});
})();
window.__animReady=true;                    // <head> の保険に「動いた」と伝える
</script>"""


def motion_css(navbp):
    return MOTION_CSS.replace("SEL", REVEAL_SEL).replace("NAVMAX", str(navbp - 1))


def body_js():
    return BODY_JS.replace("SEL", REVEAL_SEL)


# ★製造の型（references/seizo.md・2026-09-19）。骨格は建設と同じで、皮だけ替える。
#   地は白〜淡い灰青（生成りにしない）／主色は濃紺、差し色の橙は下線と数字だけ／
#   見出しは明朝でなくゴシック太め／縦書きにしない／ボタンとカードは角ばらせる／
#   英字ラベル→和文の大見出し→短い橙の下線（長峰の型）／数字を大きく（日亜の型）。
SKIN_SEIZO = """
:root{--ground:#f4f5f7;--line:#d8dbe0;--muted:#5f6773;--panel:#e6eaf0;--sub:%(sub)s;
      --serif:var(--sans)}
body{line-height:1.85}
.logo{font-weight:800;letter-spacing:.02em}
.hd .call,.btn,.contact .btn.w{border-radius:4px}
.hd .call{background:var(--accent)}
.hd .call2{display:inline-block;background:var(--ink);color:#fff;text-decoration:none;
           border-radius:4px;padding:10px 15px;font-size:12.5px;font-weight:700;
           letter-spacing:.06em;white-space:nowrap;margin-left:6px}
.hd .calls{display:flex;align-items:center}
.hero{background:linear-gradient(160deg,#eef1f5 0%%,#dfe4ec 55%%,#f4f5f7 100%%)}
.hero::before{background-image:none}
.hero::after{content:"";position:absolute;right:-6%%;top:-10%%;width:44vw;max-width:520px;
  aspect-ratio:1;border:1px solid rgba(%(acc_rgb)s,.16);transform:rotate(45deg);
  pointer-events:none}
.hero .inner::before{content:"";position:absolute;left:-8%%;bottom:4%%;width:26vw;max-width:300px;
  aspect-ratio:1;border-radius:50%%;border:1px solid rgba(%(acc_rgb)s,.14);pointer-events:none}
.vt{writing-mode:horizontal-tb!important;max-height:none!important;margin-left:0!important;
    white-space:normal!important}
.hero h1{font-family:var(--sans);font-weight:800;line-height:1.5!important;
         letter-spacing:.02em!important;font-size:clamp(24px,4.8vw,38px)!important}
.hero h1 em{white-space:nowrap}
.hero h1 .col{display:block}
.hero h1 em{color:var(--accent)}
.hero .textcol{flex-direction:column!important;gap:0!important}
.hero .textcol h1{order:-1!important}
.hero .side{align-items:flex-start!important}
.hero .meta{max-width:30em!important}
.hero .en{font-weight:700;letter-spacing:.24em;color:var(--accent)}
.shot,.gframe,.mapbox{border-radius:4px;background:linear-gradient(135deg,#e4e8ee 0%%,#d9dfe7 55%%,#e9ecf1 100%%)}
.shot .lb b,.gframe b,.mapbox b{font-family:var(--sans);font-weight:700}
.stats div{border-radius:4px;border-top:3px solid var(--sub)}
.stats b{font-family:var(--sans);font-weight:800;letter-spacing:-.01em}
section.alt{background:var(--panel)}
.sechead .en{font-weight:700;letter-spacing:.22em;font-size:11px}
h2{font-family:var(--sans);font-weight:800;letter-spacing:.03em}
.sechead h2::after{content:"";display:block;width:34px;height:3px;background:var(--sub);
                   margin:12px auto 0}
.card,.step{border-radius:4px;box-shadow:0 1px 2px rgba(20,30,50,.04)}
section.alt .card,section.alt .step{background:#fff}
.card h3{font-weight:800}
.step::before{font-family:var(--sans);font-weight:800;color:var(--sub)}
/* ナトコの型: ヒーローの下端に巨大な英字の宣言文を「面」として置く（白・薄く） */
.hero .bigen{position:relative;z-index:0;margin:-30px 0 -34px;padding:0 20px;
  font-weight:800;letter-spacing:-.01em;line-height:.9;color:rgba(255,255,255,.8);
  font-size:clamp(40px,9vw,120px);white-space:nowrap;overflow:hidden;pointer-events:none;
  text-shadow:0 1px 0 rgba(20,30,50,.06)}
.hero .inner,.hero .stats{position:relative;z-index:1}
.hero .scroll{display:none}
.hero .since{margin:0 0 6px;font-size:12px;font-weight:700;letter-spacing:.24em;color:var(--sub)}
/* ナトコの型: お知らせを丸い帯（ピル）で1行。長峰の型: NEWS の英字ラベル */
.news{padding:0 0 8px}
.news .pill{display:flex;align-items:center;gap:14px;background:#fff;border:1px solid var(--line);
  border-radius:999px;padding:10px 18px 10px 16px;font-size:13px;box-shadow:0 2px 10px rgba(20,30,50,.05);
  max-width:none;margin-left:0}
.shot{outline:0}
.badge,.tagline{display:none!important}
.scroll::after{display:none}
.news .pill .dot{width:8px;height:8px;border-radius:50%%;background:var(--sub);flex:none}
.news .pill .date{color:var(--muted);letter-spacing:.06em;font-variant-numeric:tabular-nums;flex:none}
.news .pill .t{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.news .pill .more{margin-left:auto;flex:none;color:var(--accent);font-weight:700;text-decoration:none;
  font-size:12px;letter-spacing:.1em}
/* 長峰の型: 青灰の面の上に白いカードをずらして重ねる（会社概要） */
section.alt#company .wrap{background:#fff;padding:28px 24px;border:1px solid var(--line);
  box-shadow:0 2px 12px rgba(20,30,50,.05)}
.contact{background:var(--accent)}
.contact::before{border-radius:0;transform:rotate(45deg);inset:auto -10%% -70%% 62%%;height:120%%}
.contact h2::after{display:none}
.contact .big{font-family:var(--sans);font-weight:800}
footer{background:#1f2733}
@media print{.hero{background:#fff}.hero::after,.hero .inner::before{display:none}}
"""


# ★相手のサイトの構成をメニューに写す。`sites.json` の "nav" に項目名を並べる。
#   **下層ページは作らない。**リンク先はトップ内の節に寄せる（押せば何か起きる）。
#   なぜ要るか: 既定の4項目のままだと、下層ページを持つ相手には**構成が劣化して見える**。
#   メニューだけ合わせれば「この構成のまま作り直す」という提案になり、手間も増えない。
#   nav を書かなければ既定のまま。既存のページは変わらない。
NAV_HINTS = (  # 項目名に含まれる語 → 飛ばす先。上から順に見る
    # 総称のメニュー（一覧ページ）は「できること」全体で受ける
    ("業務内容", "#works"), ("業務案内", "#works"), ("事業案内", "#works"),
    ("事業内容", "#works"), ("サービス", "#works"), ("商品のご案内", "#works"),
    # 工程・時間の案内
    ("できるまで", "#flow"), ("診療時間", "#contact"), ("受付時間", "#contact"),
    ("営業時間", "#contact"),
    # 実績・事例のページ。gallery を持つ先だけ（持たない先は下の照合に回す）
    ("実績", "#gallery"), ("事例", "#gallery"), ("施工例", "#gallery"), ("作業例", "#gallery"),
    ("経歴", "#gallery"), ("作品", "#gallery"), ("製作例", "#gallery"), ("納品例", "#gallery"),
    ("工事一覧", "#gallery"), ("実例", "#gallery"), ("ギャラリー", "#gallery"),
    # 会社・院・事務所の案内
    ("当院", "#company"), ("医院", "#company"), ("院長", "#company"),
    ("事務所", "#company"), ("スタッフ", "#company"), ("とは", "#company"),
    ("会社", "#company"), ("企業", "#company"), ("店", "#company"), ("アクセス", "#company"),
    ("問合", "#contact"), ("問い合", "#contact"),
    ("流れ", "#flow"), ("工程", "#flow"), ("ご相談から", "#flow"),
)


def _tw(text, px):
    """おおよその描画幅。全角は1文字、半角は0.55文字として数える。"""
    w = 0.0
    for c in text:
        w += 0.55 if (c.isascii() or c in "・") else 1.0
    return w * px


# ★ヘッダーを1行に戻す幅は、社名とメニューの長さから1件ずつ計算する。
#   固定の境目（1100px）にしたら、社名14字＋7項目の小川木工家具センターで
#   電話番号がはみ出した。項目数も社名の長さも先によって倍近く違う。
def nav_breakpoint(d, ind):
    labels = d.get("nav") or [ind["svc"], ind["flow_h"], "会社概要", "お問い合わせ"]
    nav = sum(_tw(x, 14.3) for x in labels) + (len(labels) - 1) * 22
    logo = _tw(d["name"], 18.4)
    call = _tw("お電話 " + d.get("tel", ""), 14.5) + 40
    if ind.get("skin") == "seizo":
        call += _tw("資料請求", 12.5) + 36          # 2つ目のボタンのぶん
    need = logo + nav + call + 24 * 2 + 30 + 24 + 100  # すきま・内側の余白・安全分
    return max(900, int(need // 20 * 20 + 20))


# ★色は業種の既定ではなく、相手のサイトから拾った1色に寄せられるようにする。
#   sites.json に "accent" があればそれを使う（拾い方は colorfind.py）。
#   拾った色をそのまま使うと白抜き文字が読めないことがあるので、
#   白に対して 4.5:1 を満たすまで暗くしてから使う。
def _rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lum(rgb):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(x))) for x in rgb)


def _scale(rgb, f):
    return tuple(x * f for x in rgb)


def accent_of(d, ind):
    """本文・ボタンに使う色。白抜き文字が読める濃さまで落として返す。"""
    rgb = _rgb(d.get("accent") or ind["accent"])
    for _ in range(40):
        if (1.05) / (_lum(rgb) + 0.05) >= 4.5:
            break
        rgb = _scale(rgb, 0.93)
    return _hex(rgb), _hex(_scale(rgb, 0.76)), "%d,%d,%d" % tuple(round(x) for x in rgb)


TEXTURES = {
    # 瓦。葺き足のうろこを1段ずつずらして重ねる
    "kawara": """<pattern id="tx" width="60" height="40" patternUnits="userSpaceOnUse">
 <g fill="none" stroke="rgba(%(c)s,.22)" stroke-width="1.4">
  <path d="M0 18 q10 -11 20 0 q10 -11 20 0 q10 -11 20 0"/>
  <path d="M-10 38 q10 -11 20 0 q10 -11 20 0 q10 -11 20 0 q10 -11 20 0"/>
 </g>
 <g stroke="rgba(%(c)s,.10)" stroke-width="1.2">
  <line x1="0" y1="19.3" x2="60" y2="19.3"/><line x1="0" y1="39.3" x2="60" y2="39.3"/>
 </g>
</pattern>""",
    # 金属。縞鋼板の滑り止め（2本1組を互い違いに）
    "kinzoku": """<pattern id="tx" width="48" height="48" patternUnits="userSpaceOnUse">
 <g stroke="rgba(%(c)s,.24)" stroke-width="2.6" stroke-linecap="round">
  <line x1="5" y1="15" x2="19" y2="7"/><line x1="8" y1="20" x2="22" y2="12"/>
  <line x1="29" y1="15" x2="43" y2="7"/><line x1="32" y1="20" x2="46" y2="12"/>
  <line x1="5" y1="33" x2="19" y2="41"/><line x1="8" y1="28" x2="22" y2="36"/>
  <line x1="29" y1="33" x2="43" y2="41"/><line x1="32" y1="28" x2="46" y2="36"/>
 </g>
</pattern>""",
    # 図面。方眼と寸法線（住宅・不動産）
    "zumen": """<pattern id="tx" width="72" height="72" patternUnits="userSpaceOnUse">
 <g stroke="rgba(%(c)s,.10)" stroke-width="1">
  <line x1="0" y1="0" x2="72" y2="0"/><line x1="0" y1="36" x2="72" y2="36"/>
  <line x1="0" y1="0" x2="0" y2="72"/><line x1="36" y1="0" x2="36" y2="72"/>
 </g>
 <g stroke="rgba(%(c)s,.22)" stroke-width="1.2">
  <line x1="8" y1="18" x2="28" y2="18"/>
  <line x1="8" y1="14" x2="8" y2="22"/><line x1="28" y1="14" x2="28" y2="22"/>
  <line x1="44" y1="54" x2="64" y2="54"/>
  <line x1="44" y1="50" x2="44" y2="58"/><line x1="64" y1="50" x2="64" y2="58"/>
 </g>
</pattern>""",
    # 刷毛の跡（塗装）
    "nuri": """<pattern id="tx" width="96" height="30" patternUnits="userSpaceOnUse">
 <g fill="none" stroke="rgba(%(c)s,.17)" stroke-width="2.2" stroke-linecap="round">
  <path d="M4 9 H60"/><path d="M8 15 H52"/><path d="M4 21 H64"/>
  <path d="M70 12 H92"/><path d="M74 24 H92"/>
 </g>
</pattern>""",
    # 足場の建地と布板（建築）
    "ashiba": """<pattern id="tx" width="64" height="64" patternUnits="userSpaceOnUse">
 <g stroke="rgba(%(c)s,.18)" stroke-width="1.6">
  <line x1="10" y1="0" x2="10" y2="64"/><line x1="42" y1="0" x2="42" y2="64"/>
  <line x1="0" y1="20" x2="64" y2="20"/><line x1="0" y1="52" x2="64" y2="52"/>
 </g>
 <g stroke="rgba(%(c)s,.09)" stroke-width="1.2">
  <line x1="10" y1="20" x2="42" y2="52"/><line x1="42" y1="20" x2="10" y2="52"/>
 </g>
</pattern>""",
    # 木。板目の年輪
    "mokume": """<pattern id="tx" width="120" height="54" patternUnits="userSpaceOnUse">
 <g fill="none" stroke="rgba(%(c)s,.16)" stroke-width="1.3">
  <path d="M0 12 C30 2 90 22 120 12"/><path d="M0 27 C34 18 86 36 120 27"/>
  <path d="M0 42 C28 33 92 51 120 42"/>
 </g>
 <path d="M0 53.4H120" stroke="rgba(%(c)s,.07)" stroke-width="1.2"/>
</pattern>""",
}


def texture_svg(kind, rgb, cls="tex", pid="tx"):
    """質感のSVG。kind が無ければ空文字。rgb は "r,g,b" の文字列。"""
    pat = TEXTURES.get(kind or "")
    if not pat:
        return ""
    # ★同じページに2つ置くので id を分ける。同じ id だと後の方が
    #   先に定義されたパターン（ヒーローの色）で塗られ、地の色に埋もれて見えない。
    body = (pat % {"c": rgb}).replace('id="tx"', f'id="{pid}"')
    return (f'<svg class="{cls}" aria-hidden="true"><defs>' + body
            + f'</defs><rect width="100%" height="100%" fill="url(#{pid})"/></svg>')


# ★縦書きの見出しは、入りきらないと途中で列が変わる。
#   中駒産業では「守る。」と「100年。」が次の列に落ちていた。
#   文字数から入る大きさを決め、それでも長い文は**読点・句点の位置で**列を分ける。
#   機械任せの折り返しと違って、切れ目が意味の切れ目に一致する。
VLIMIT = 12          # 1列に置く文字数の目安
VBUDGET = 460        # 1列に使える高さ（px）


def vsplit(text, limit=VLIMIT):
    """読点・句点で列に分ける。区切りが無ければ分けない（無理に切らない）。"""
    segs = [text]
    while True:
        i = max(range(len(segs)), key=lambda n: len(segs[n]))
        if len(segs[i]) <= limit:
            return segs
        cuts = [n + 1 for n, c in enumerate(segs[i][:-1]) if c in "、。"]
        if not cuts:
            return segs                          # 切れ目が無いなら諦める
        half = len(segs[i]) / 2
        cut = min(cuts, key=lambda c: abs(c - half))
        segs[i:i + 1] = [segs[i][:cut], segs[i][cut:]]


def headline(d, e):
    """見出しのHTMLと、縦書きのときの文字の大きさ。"""
    a, b = vsplit(d["catch"]), vsplit(d["catch_em"])
    px = max(26, min(40, int(VBUDGET / (max(len(x) for x in a + b) * 1.14))))
    html = "<br>".join(e(x) for x in a)
    html += "<br><em>" + "<br>".join(e(x) for x in b) + "</em>"
    return html, px


# リード文が「可児／東濃」「対／応します」のように語の途中で折り返していた。
# 読点・句点で区切った句を inline-block にして、切れ目をそこだけに限る。
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


def _bigrams(text):
    t = "".join(c for c in text if c not in "・／/ 　のとをごおはが")
    return {t[i:i + 2] for i in range(len(t) - 1)} or {t}


# ★メニューの項目は、対応するサービスカードまで飛ばす。
#   最初は全部 #works に飛ばしていたが、中駒だと7項目のうち5つが同じ場所に着地した。
#   2つ押せば「同じところに戻る＝中身が無い」と分かってしまう。
def nav_targets(d, ind):
    """メニューの項目名 → 飛び先。当てはまるカードが無い項目は None で返す。"""
    labels = list(d.get("nav") or [])
    pairs = {}
    has_gallery = bool(d.get("gallery"))
    svc = [t for t, _ in d.get("services", [])]

    # 見出しの重なり具合（2文字のかたまり）で一番近いカードに割り当てる。
    # 1項目1カードにしたいので、点の高い組から順に取っていく。
    # ★カードと強く重なる（2かたまり以上）項目は、語のヒントより先にカードへ。
    #   「設計事務所へのQ&A」が「事務所」のヒントで会社概要へ、
    #   「エディオン前並店」「店舗デザイン・設計」が「店」のヒントで会社概要へ飛んでいた。
    #   同名のカードを用意してあるのに着地しないのでは、カードを足した意味が無い。
    score = []
    for label in labels:
        lb = _bigrams(label)
        for i, title in enumerate(svc):
            n = len(lb & _bigrams(title))
            if n:
                score.append((-n, i, label))
    score.sort()
    used_l, used_i = set(), set()

    def take(min_n):
        for negn, i, label in score:
            if -negn < min_n or label in used_l or i in used_i:
                continue
            pairs[label] = f"#svc{i + 1}"
            used_l.add(label)
            used_i.add(i)

    # ★「〜の流れ」「〜ができるまで」は工程へ。カードと語が重なっても（「リフォームの流れ」と
    #   「リフォーム」のカード）工程が正しい着地（2026-09-19）
    for label in labels:
        if any(k in label for k in ("流れ", "できるまで", "工程", "ご相談から")):
            pairs[label] = "#flow"
            used_l.add(label)
        elif any(k in label for k in ("お知らせ", "ニュース", "新着", "NEWS", "News", "トピックス")):
            pairs[label] = "#news"
            used_l.add(label)
    take(2)                                      # 強い一致はカードへ
    for label in labels:
        if label in pairs:
            continue
        for key, target in NAV_HINTS:
            if key in label:
                if target == "#gallery" and not has_gallery:
                    continue                     # 実績ブロックが無いならカード照合に回す
                pairs[label] = target
                used_l.add(label)
                break
    take(1)                                      # 残りは弱い一致でもカードへ
    for label in labels:
        pairs.setdefault(label, None)            # 対応するカードが無い
    return [(x, pairs[x]) for x in labels]


def nav_html(d, ind, e):
    """メニューのHTML。nav が無ければ既定の4項目。"""
    items = d.get("nav")
    if not items:
        return (f'<a href="#works">{e(ind["svc"])}</a><a href="#flow">{e(ind["flow_h"])}</a>'
                f'<a href="#company">会社概要</a><a href="#contact">お問い合わせ</a>')
    out = []
    for label, href in nav_targets(d, ind)[:6]:  # 7つ以上は横に入らない
        out.append(f'<a href="{href or "#works"}">{e(label)}</a>')
    out.append('<a href="#contact">お問い合わせ</a>')   # 窓口は必ず出す
    return "".join(out)


def render(sid, d, ind):
    tel = d.get("tel", "")
    tl = tel.replace("-", "")
    name = d["name"]
    acc, acc_d, acc_rgb = accent_of(d, ind)
    h1_html, h1px = headline(d, e)
    sub_html = phrase(d["sub"], e)
    tex = texture_svg(d.get("texture"), acc_rgb)
    # 下のほうも文字だけが続いて単調になるので、同じ質感を白抜きで敷く
    ctex = texture_svg(d.get("texture"), "255,255,255", cls="tex ctex", pid="tx2")
    navbp = nav_breakpoint(d, ind)
    css = CSS % {"ground": ind["ground"], "ink2": ind["ink2"], "accent": acc,
                 "accent_d": acc_d, "acc_rgb": acc_rgb, "navbp": navbp,
                 "h1px": h1px}
    skin = ind.get("skin")
    if skin == "seizo":
        css += SKIN_SEIZO % {"sub": ind.get("sub", "#d4420a"), "acc_rgb": acc_rgb}
        tex = ""            # 製造は幾何形の地で持たせる。質感は問い合わせ帯だけ
    css += motion_css(navbp)      # 動きは皮の後ろ。皮の指定を上書きしないため
    roman = d.get("roman", "")
    since = bigen = tagline = badge = ""
    news_t = ind.get("news_hint", "お知らせが入ります（工事のご報告・休業日など）")
    if skin == "seizo":
        if d.get("founded"):
            since = f'<p class="since">SINCE {e(d["founded"])}</p>'
        if roman:
            bigen = f'  <p class="bigen" aria-hidden="true">{e(roman)}</p>\n'
    else:
        # TATSUSHO の型: 左端の縦書きの一言と、丸い CONTACT のバッジ（広い画面だけ出る）
        tagline = f'\n  <p class="tagline">{e(d.get("svc_lead") or ind["svc_lead"])}</p>'
        badge = ('\n<a class="badge" href="#contact" aria-label="お問い合わせ">'
                 '<svg viewBox="0 0 100 100" aria-hidden="true"><defs><path id="bc" d="M50,50 m-38,0 a38,38 0 1,1 76,0 a38,38 0 1,1 -76,0"/></defs>'
                 '<text><textPath href="#bc">CONTACT · CONTACT · CONTACT · </textPath></text></svg>'
                 '<span>ご相談<br>ください</span></a>')
    news = ('\n<div class="news" id="news"><div class="wrap"><div class="pill">'
            '<span class="dot"></span><span class="date">2026.09.01</span>'
            f'<span class="t">{e(news_t)}</span>'
            '<a class="more" href="#contact">NEWS →</a></div></div></div>')

    stats = "".join(f'<div><b>{e(a)}<small>{e(b)}</small></b><span>{e(c)}</span></div>'
                    for a, b, c in d["stats"])
    cards = "".join(
        f'<div class="card" id="svc{i}"><h3>{e(t)}</h3><p>{e(p)}</p></div>'
        for i, (t, p) in enumerate(d["services"], 1))
    steps = "".join(f'<div class="step"><h3>{e(t)}</h3><p>{e(p)}</p></div>'
                    for t, p in ind["flow"])

    # メニューに「実績」「事例」がある先には、その受け皿を作る。
    # 無いと項目を押しても「できること」に着地して、中身が無いのが分かる。
    gal = d.get("gallery")
    gallery = ""
    flow_cls, comp_cls = ' class="alt"', ""
    if gal:
        flow_cls, comp_cls = "", ' class="alt"'
        frames = "".join(f'<div class="gframe"><b>お写真が入ります</b>{e(c)}</div>' for c in gal[:3])
        gallery = f"""<section class="alt" id="gallery">
  <div class="wrap">
    <div class="sechead"><span class="en">WORKS</span>
      <h2>{e(d.get("gallery_h", "これまでの仕事"))}</h2>
      <p>お預かりしたお写真を、ここに並べます。</p></div>
    <div class="gal">{frames}</div>
  </div>
</section>"""

    info = [("商号", name)]
    if d.get("addr"):
        info.append(("所在地", (f'〒{d["zip"]} ' if d.get("zip") else "") + d["addr"]))
    if tel:
        info.append(("電話", f'<a href="tel:{e(tl)}">{e(tel)}</a>'))
    if d.get("founded"):
        info.append(("創業", f'{e(d["founded"])}年'))
    info.append(("事業内容", "／".join(t for t, _ in d["services"][:5])))
    rows = "".join(f'<tr><th>{e(k)}</th><td>{v if k=="電話" else e(v)}</td></tr>'
                   for k, v in info)

    nav = nav_html(d, ind, e)
    call = (f'<a class="call" href="tel:{e(tl)}">お電話 {e(tel)}</a>' if tel
            else '<a class="call" href="#contact">お問い合わせ</a>')
    if skin == "seizo":
        # 長峰の型: 右端に角ばったボタンを2つ（お問い合わせ／資料請求）
        call = f'<div class="calls">{call}<a class="call2" href="#contact">資料請求</a></div>'
    hero_btn = (f'<a class="btn p" href="tel:{e(tl)}">電話で相談する</a>' if tel else "")
    ctel = (f'<a class="big" href="tel:{e(tl)}">{e(tel)}</a>'
            f'<small>{e(ind["hours"])}</small>'
            f'<div><a class="btn w" href="tel:{e(tl)}">電話をかける</a></div>'
            if tel else f'<small>{e(ind["hours"])}</small>')

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- ★提案用の見本。検索に載せない。本物と誤認されないための最低条件 -->
<meta name="robots" content="noindex, nofollow, noarchive">
<title>【提案見本】{e(name)}さま トップページ案｜EasyWebCraft</title>
<style>{css}</style>
{HEAD_JS}
</head>
<body>

<div class="notice">
  <b>これは EasyWebCraft が作成した提案用の見本です。</b>
  <span><span class="ph">{e(name)}さまの公式サイトではありません。</span><span class="ph"><b>トップページだけを形にした見本</b>で、</span><span class="ph">メニューの各ページは実際の制作でお作りします。</span><span class="ph">写真・文章は当社が用意したものです。</span></span>
</div>

<div class="hdwrap">
  <header><div class="hd">
    <div class="logo">{e(name)}<small>{e(roman)}</small></div>
    <nav>{nav}</nav>
    {call}
  </div></header>
</div>

<div class="hero{" tx" if tex else ""}">
  {tex}{tagline}
  <div class="wrap inner">
    <div class="side">
      <div class="textcol">
        <div class="meta">
          <p class="sub">{sub_html}</p>
          <p class="en">{e(roman)}</p>
          <div class="acts">{hero_btn}<a class="btn g" href="#works">{e(ind["svc"])}を見る</a></div>
        </div>
        {since}<h1 class="vt">{h1_html}</h1>
      </div>
    </div>
    <div class="shot">
      <div class="lb"><b>お写真が入ります</b>{e(ind.get("shot", "現場のようす・完成した建物など"))}</div>
    </div>
    <span class="scroll">scroll</span>
  </div>
{bigen}  <div class="wrap"><div class="stats">{stats}</div></div>
</div>
{news}
<section id="works">
  <div class="wrap">
    <div class="sechead"><span class="en">SERVICE</span>
      <h2>{e(ind["svc"])}</h2><p>{e(ind["svc_lead"])}</p></div>
    <div class="cards">{cards}</div>
  </div>
</section>

{gallery}

<section{flow_cls} id="flow">
  <div class="wrap">
    <div class="sechead"><span class="en">FLOW</span>
      <h2>{e(ind["flow_h"])}</h2><p>はじめての方にも、順番が分かるように。</p></div>
    <div class="flow">{steps}</div>
  </div>
</section>

<section{comp_cls} id="company">
  <div class="wrap" style="max-width:720px">
    <div class="sechead"><span class="en">COMPANY</span><h2>会社概要</h2></div>
    <table class="info">{rows}</table>
    <div class="mapbox"><b>地図が入ります</b>最寄り駅・駐車場のご案内もここに</div>
  </div>
</section>

<div class="contact{" tx" if ctex else ""}" id="contact">
  {ctex}
  <h2>{e(ind["cta"])}</h2>
  <p>{e(ind["cta_sub"])}</p>
  {ctel}
</div>

{badge}
<footer>
  <span class="ph">この見本は EasyWebCraft が作成した提案資料です。</span><span class="ph">{e(name)}さまの公式サイトではありません。</span><br>
  <span class="ph">実際の制作では、</span><span class="ph">御社の写真・実績・文章に差し替えて仕上げます。</span>
  <p class="by"><span class="ph">EasyWebCraft（担当：田代）</span><span class="ph"><a href="mailto:info@easywebcraft.jp">info@easywebcraft.jp</a></span></p>
</footer>

{body_js()}
</body>
</html>
"""
