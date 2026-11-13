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
import re


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
     line-height:1.9;-webkit-text-size-adjust:100%%;overflow-x:hidden;overflow-x:clip}
/* ★横のはみ出しは clip で切る（hidden だけだと、冒頭の演出で html を overflow:hidden にした間に
   body がスクロールの枠になり、初回アクセスだけメニューの固定が効かないことがあった 2026-11-02）。
   clip は枠を作らない。古いブラウザは前の行の hidden が効く */
a{color:inherit}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}

/* 見本であることの明示。閉じられない。 */
.notice{position:relative;z-index:60;background:var(--accent);color:#fff;
        font-size:13px;line-height:1.6;padding:9px 16px;text-align:center}
.notice b{font-weight:700}
.notice span{display:block;opacity:.92;font-size:12px}
/* ★2026-11-02 松本さん「見本の帯が強調されすぎて邪魔」。会社の色の2段から、濃い灰色の細い1行に。
   公式サイトではないことは常に見せる（閉じられない）。詳しい断り書きはページ下（footer）に残す */
.notice.slim{background:#2a2c2b;color:rgba(255,255,255,.8);font-size:11.5px;line-height:1.5;
  padding:6px 16px;letter-spacing:.04em}
.notice.slim span{display:inline-block;opacity:1;font-size:inherit}
.notice.slim i{display:inline-block;width:6px;height:6px;border-radius:50%%;background:var(--accent);
  margin-right:7px;vertical-align:1px;box-shadow:0 0 0 2px rgba(255,255,255,.25)}
.notice.slim .ph{margin-right:0}
/* スマホは1行に収めるため「EasyWebCraft の」を省く（会社名はページ下の断り書きにある） */
@media(max-width:600px){.notice.slim{font-size:11px;padding:6px 10px;letter-spacing:.02em}.notice.slim .ewc{display:none}}

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
.hero .inner{position:relative;display:grid;gap:22px;padding:18px 20px 0}   /* 左右は .wrap と同じ余白（0だとスマホで文字が端に付く） */
.hero .textcol{display:flex;flex-direction:column}
.hero .textcol h1{order:-1}   /* 狭い画面では見出しを先頭に */
.vt{writing-mode:horizontal-tb}
.hero h1{font-family:var(--serif);font-weight:500;margin:0;
         font-size:clamp(27px,7.4vw,40px);line-height:1.65;letter-spacing:.06em}
.hero h1 em{font-style:normal;color:var(--accent)}
.hero .sub{margin:16px 0 0;color:var(--muted);font-size:14.5px;max-width:30em}
.ph{display:inline-block}
.cp{display:inline-block}.cp+.cp{margin-inline-start:.55em}
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
/* ★当社が用意したイメージ写真を入れた枠（2026-09-19）。相手の写真は使わない原則はそのまま。
   写真は data URI で内蔵するので1ファイル・外部読み込みなしは崩れない。
   「イメージ写真」の札を必ず出す（本物の実績と誤認させないため） */
.ph{background-size:cover;background-position:center}
.ph::after{display:none}
.shot.ph,.gframe.ph{display:block;padding:0;background-size:cover;background-position:center}
/* ★.gframe の background 一括指定が後ろにあり、.ph の cover/center を打ち消していた
   （写真が原寸のまま左上だけ写っていた）。ここで写真の枠に限って掛け直す */
/* 札は大きく・はっきり（2026-09-19 指示: イメージ写真であることを強調）。
   1行目に「イメージ写真」を太く、2行目に差し替えの断り */
.shot.ph .lb,.gframe.ph .cap{position:absolute;left:12px;bottom:12px;z-index:1;text-align:left;
  background:rgba(20,18,14,.78);color:#fff;border-radius:8px;padding:9px 14px 10px;
  font-size:12px;letter-spacing:.04em;line-height:1.5;backdrop-filter:blur(4px);
  box-shadow:0 2px 12px rgba(0,0,0,.25)}
.shot.ph .lb b,.gframe.ph .cap b{display:block;font-family:var(--sans);font-size:15px;
  margin:0 0 1px;font-weight:700;color:#fff;letter-spacing:.12em}
.shot.ph .lb b::before,.gframe.ph .cap b::before{content:"";display:inline-block;width:8px;height:8px;
  border-radius:50%%;background:var(--sub,#f0b429);margin:0 8px 2px 0;vertical-align:middle}
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
  border:1px solid var(--line);border-radius:22px;padding:6px 16px 6px 14px;font-size:12.5px;
  max-width:560px;margin-left:auto}
.news .pill .rows{min-width:0;flex:1 1 auto}
.news .pill .lbl{flex:none;font-size:10px;line-height:1.35;font-weight:700;color:var(--muted);border-right:1px solid var(--line);padding-right:10px;text-align:center}
.news .pill .row{display:flex;align-items:center;gap:12px;padding:5px 0}
.news .pill .row+.row{border-top:1px dashed var(--line)}
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

/* 問い合わせ帯の注記: 電話が苦手な客層に「窓口は増える」と伝える */
.contact .note{font-size:11.5px;opacity:.8;margin:14px auto 0;max-width:40em;position:relative}
/* ★サイトの構成（2026-09-19）。スマホでメニューを畳んだので、
   「この構成で作ります」を一覧で見せる場所を別に持つ。営業メールの主旨と一致させる */
.sitemap{background:var(--paper);border-top:1px solid var(--line);padding:34px 20px 36px;text-align:center}
.sitemap h2{font-size:15px;margin:0 0 4px;letter-spacing:.08em}
.sitemap p{margin:0 0 16px;font-size:12.5px;color:var(--muted)}
.sitemap ul{list-style:none;margin:0 auto;padding:0;display:flex;flex-wrap:wrap;justify-content:center;
  gap:8px;max-width:820px}
.sitemap li a{display:inline-block;padding:8px 14px;border:1px solid var(--line);border-radius:999px;
  background:var(--ground);text-decoration:none;font-size:12.5px;color:var(--ink);white-space:nowrap}
.sitemap li a:hover{border-color:var(--accent);color:var(--accent)}
.sitemap li a::before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%%;
  background:var(--accent);margin:0 8px 2px 0;vertical-align:middle}
footer{background:#242c27;color:rgba(255,255,255,.6);font-size:11.5px;
       padding:26px 20px;text-align:center;line-height:1.9}
/* ★この見本を本物にするには（2026-09-19）。見本を見たあとの行き先。
   金額は 2026-11-13 から LP と同じ表示（EWC_PRICE）を書く（画面下の EWC への相談の帯と同じ） */
footer .next{max-width:560px;margin:18px auto 0;padding:16px 18px;border:1px solid rgba(255,255,255,.18);
  border-radius:10px;text-align:left;color:rgba(255,255,255,.78)}
footer .next b{display:block;color:#fff;font-size:12.5px;margin-bottom:6px;letter-spacing:.06em;text-align:center}
footer .next ol{margin:0;padding-left:1.4em}
footer .next li{margin:2px 0}

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
               align-items:center;gap:46px;padding:34px 20px 46px}
  /* 縦書きの明朝（TATSUSHO の型）。広い画面のときだけ。 */
  .vt{writing-mode:vertical-rl;text-orientation:upright;
      max-height:470px;margin-left:auto;white-space:nowrap}
  .hero h1{line-height:2.0;letter-spacing:.14em;font-size:calc(%(h1px)spx * var(--h1k,1))}
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
  footer .next{border-color:#999;color:#333}footer .next b{color:#000}
  .sitemap li a{border-color:#999}
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
REVEAL_SEL = ".stats > *,.sechead,.cards > *,.gal > *,.flow > *,.info,.mapbox,.news .pill,.abph,.abtx"

MOTION_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
@keyframes heroUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes popIn{from{opacity:0;transform:scale(.97)}to{opacity:1;transform:none}}
.hero .meta > *,.hero h1,.hero .since{animation:heroUp .8s cubic-bezier(.2,.7,.3,1) both}
/* トップの文字は 見出し → 説明 → ボタン の順に少しずつ */
.hero .since,.hero h1{animation-delay:.15s}
.hero .meta > :nth-child(1){animation-delay:.4s}
.hero .meta > :nth-child(2){animation-delay:.5s}
.hero .meta > :nth-child(3){animation-delay:.65s}

.hero .shot{animation:popIn 1s cubic-bezier(.2,.7,.3,1) .45s both}
.anim :is(SEL){opacity:0}
.anim .on{animation:rise .7s cubic-bezier(.2,.7,.3,1) both}
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
  /* ★2026-11-09 松本さん「スマホでメニューを押すと表示がズレる」。ページの上でメニューを開くと、ヘッダーが
     伸びて写真と本文が丸ごと下へ押し出されていた（写真が 85px → 430px）。メニューはヘッダーの真下に
     重ねて出し、下のページは動かさない。項目が多くても画面に収まるよう、はみ出す分はメニューの中で流す */
  .js .hd{position:relative}
  .js .hd.open nav{position:absolute;top:calc(100% + 1px);left:0;right:0;margin:0;width:auto;box-sizing:border-box;z-index:5;
    background:#fff;padding:4px 16px 10px;border-bottom:1px solid var(--line);
    box-shadow:0 12px 24px rgba(30,40,50,.12);max-height:calc(100vh - 110px);max-height:calc(100dvh - 110px);
    overflow-y:auto;overscroll-behavior:contain}
}
/* ---- メニュー（2026-11-02 松本さん「各メニューにも動き・カーソルを合わせたら選んでいると分かる動き」） ----
   PC：トップと一緒に左から順に上から降りてくる。合わせると文字が色付き、下に線が中央から伸びる
   スマホ：メニューを開くと項目が上から順に横から出てくる。押すと少し右へ寄って色付く */
@keyframes navIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
@keyframes menuIn{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:none}}
nav a{position:relative;transition:color .25s;cursor:pointer}
nav a:hover,nav a:focus-visible{color:var(--accent)}
@media(min-width:NAVMINpx){
  .anim nav a{animation:navIn .6s cubic-bezier(.2,.7,.3,1) both}
  .anim nav a:nth-child(2){animation-delay:.06s}.anim nav a:nth-child(3){animation-delay:.12s}
  .anim nav a:nth-child(4){animation-delay:.18s}.anim nav a:nth-child(5){animation-delay:.24s}
  .anim nav a:nth-child(6){animation-delay:.3s}.anim nav a:nth-child(n+7){animation-delay:.36s}
  nav a::after{content:"";position:absolute;left:0;right:0;bottom:-6px;height:2px;border-radius:2px;
    background:var(--accent);transform:scaleX(0);transition:transform .3s cubic-bezier(.2,.7,.3,1)}
  nav a:hover::after,nav a:focus-visible::after{transform:scaleX(1)}
}
@media(max-width:NAVMAXpx){
  .js nav a{transition:color .2s,padding-left .25s,background-color .25s}
  .js nav a:hover,.js nav a:active,.js nav a:focus-visible{padding-left:14px;color:var(--accent)}
  .js .hd.open nav a{animation:menuIn .35s cubic-bezier(.2,.7,.3,1) both}
  .js .hd.open nav a:nth-child(2){animation-delay:.04s}.js .hd.open nav a:nth-child(3){animation-delay:.08s}
  .js .hd.open nav a:nth-child(4){animation-delay:.12s}.js .hd.open nav a:nth-child(5){animation-delay:.16s}
  .js .hd.open nav a:nth-child(n+6){animation-delay:.2s}
}
@media(prefers-reduced-motion:reduce){
  nav a{animation:none!important}
  nav a::after{transition:none}
}
@media(prefers-reduced-motion:reduce){
  .anim :is(SEL){opacity:1}
  .anim .on,.hero .meta > *,.hero h1,.hero .since,.hero .shot{animation:none}
  .mbtn i::before,.mbtn i::after,.mbtn i span{transition:none}
}
@media print{
  .anim :is(SEL){opacity:1!important}
  .anim .on,.hero .meta > *,.hero h1,.hero .since,.hero .shot,nav a{animation:none!important}
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
// スクロールで出てくる動き。隠す指定は <head> の CSS 側（.anim）。ここでは出す時と順番だけを決める
//   ・IntersectionObserver で、画面の下1割より上に入ったら出す。一度出したら見張らない（戻っても隠さない）
//   ・同じ並び（カード・流れ・数字の帯）で同時に入ったものは 100ms ずつずらす
//   ・冒頭の演出の幕が透け始めるまでは見張らない（演出の裏で出しきって、動きが見えなかった）
(function(){
  var r=document.documentElement,units=[].slice.call(document.querySelectorAll('SEL'));
  function show(el){el.classList.add('on');}
  if(!('IntersectionObserver' in window)){units.forEach(show);return;}
  var io=new IntersectionObserver(function(es){
    var hit=es.filter(function(x){return x.isIntersecting;}).map(function(x){return x.target;});
    hit.sort(function(a,b){var p=a.getBoundingClientRect(),q=b.getBoundingClientRect();return (p.top-q.top)||(p.left-q.left);});
    var rows=[],n=[];
    hit.forEach(function(el){
      var k=rows.indexOf(el.parentNode);if(k<0){k=rows.push(el.parentNode)-1;n[k]=0;}
      el.style.animationDelay=(Math.min(n[k]++,5)*0.1)+'s';
      show(el);io.unobserve(el);
    });
  },{rootMargin:'0px 0px -10% 0px',threshold:0});
  function start(){units.forEach(function(el){io.observe(el);});}
  var veiled=function(){return r.classList.contains('ewl-on')&&!r.classList.contains('ewl-go');};
  if(veiled()){
    var mo=new MutationObserver(function(){if(!veiled()){mo.disconnect();start();}});
    mo.observe(r,{attributes:true,attributeFilter:['class']});
  }else start();
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


# ★冒頭の演出（2026-11-01・LFグループのトップと同じ流れ。中身は社名だけ）
#   輪が埋まる → 社名が中央に出る → ヘッダーの社名の位置へ吸い込まれ、白い幕が透けてページが出る。
#   ・1回の訪問で1度だけ（sessionStorage）。押せばすぐ終わる。動きを減らす設定の人には出さない
#   ・演出の社名はヘッダーと同じ .logo の指定で組むので、着いたところで本物と入れ替えても境目が出ない
#   ・幕の下でトップの出る動きが先に終わらないよう、演出中は止めておき、幕が透けるときに動かす
#   ・JS が動かなくても 6秒で幕を外す（見本の断り書きを隠したままにしない）
LOADER_CSS = """
.ewl{display:none}
html.ewl-on{overflow:hidden}
html.ewl-on .ewl{display:grid;place-items:center;position:fixed;inset:0;z-index:1000;background:#fff;
  transition:background-color .9s ease .25s,opacity .5s ease;cursor:pointer}
html.ewl-on .ewl.is-absorb{background-color:rgba(255,255,255,0)}
html.ewl-on .ewl.is-out{opacity:0}
/* ★2026-11-02 輪の中は頭文字ではなく会社名。輪は会社名が収まる大きさ（--ewd、JS で決める） */
.ewl-p1{position:absolute;left:50%;top:50%;width:var(--ewd,112px);height:var(--ewd,112px);
  transform:translate(-50%,-50%);transition:opacity .45s,transform .45s}
.ewl.is-p2 .ewl-p1{opacity:0;transform:translate(-50%,-50%) scale(1.04)}
.ewl-ring{position:absolute;inset:0;width:100%;height:100%;transform:rotate(-90deg)}
/* ★2026-11-11 vector-effect:non-scaling-stroke はやめた。輪を拡大すると線の長さの計算がずれ、100%でも輪が一周しなかった。
   線の太さは画面上で2pxになるよう JS が --ews に入れる（輪の図は120の枠で描いている） */
.ewl-ring circle{fill:none;stroke-width:var(--ews,2.14)}
.ewl-ring .t{stroke:#e6e3dc}
.ewl-ring .f{stroke:var(--accent);stroke-linecap:round}
.ewl-pct{position:absolute;top:calc(100% + 16px);left:0;right:0;text-align:center;font-size:12px;
  font-weight:700;letter-spacing:.14em;color:var(--accent)}
.ewl-p2{position:absolute;inset:0;display:grid;place-content:center;opacity:0;pointer-events:none;transition:opacity .6s ease .1s}
.ewl.is-in .ewl-p2{opacity:1}
.ewl .logo{transform:scale(var(--ewk,1.9));transform-origin:50% 50%;white-space:nowrap;
  transition:transform 1s cubic-bezier(.65,0,.35,1),opacity .45s ease .95s}
/* 着いてから本物と入れ替える（途中で消すと、吸い込まれる動きが見えない） */
.ewl.is-absorb .logo{opacity:0}
.ewl-skip{position:absolute;bottom:26px;left:0;right:0;text-align:center;font-size:11px;letter-spacing:.1em;
  color:#888;transition:opacity .3s}
.ewl.is-absorb .ewl-skip{opacity:0}
@media(hover:hover){.ewl-skip{display:none}}
html.ewl-on .hd .logo{opacity:0}
.hd .logo .lw{display:inline-block}
.hd .logo.ewl-in{transition:opacity .8s ease}
html.ewl-on:not(.ewl-go) .hero .shot{animation-play-state:paused}
html.ewl-on:not(.ewl-txt) :is(.hero .meta > *,.hero h1,.hero .since,nav a){animation-play-state:paused}
/* ★写真は幕が透け始めたら（ewl-go）、文字は幕がほぼ消えてから（ewl-txt）動かす。
   文字も幕と一緒に動かすと、演出が終わった時にはもう出終わっていた（2026-11-02） */
/* ★止めるのは animation:none ではなく一時停止。none にすると、動き出す瞬間に写真が 1.04 倍へ跳ねてかたつき、
   幕が消えきるまで（社名が着いてから約2.3秒）コピーが出なかった（2026-11-02） */
/* 幕を外したときにスクロールバーが出て、ページが横にずれないように（Windows など） */
html{scrollbar-gutter:stable}
"""

# ★2026-11-02 松本さん「LFのFVのように、メニューを分かりやすい大きさにして、白い帯なしで背景の写真の上に。
#   スクロールしたら帯を出す」。PC（メニューが横に並ぶ幅）で、トップに写真がある見本だけ。
#   ・帯はそのまま sticky にして、下に負の余白を付けて写真の上に重ねる（見本の断り書きは上に残る）
#   ・写真の上では白い文字＋薄い影、少し下がったら（.solid）白い帯と濃い文字に戻す
#   ・冒頭の演出の社名は、写真の上に着地するので白に変えながら吸い込む
OVL_CSS = """
/* 大きなメニューは並びきる広い画面だけ（ノートパソコンでは今までの大きさで横に並べる） */
@media(min-width:%(navbig)spx){
  .logo{font-size:21px}
  .logo small{font-size:10.5px}
  nav{font-size:16.5px;column-gap:30px;letter-spacing:.08em}
  .hd .call{padding:13px 24px;font-size:14.5px}
}
@media(min-width:%(navbp)spx){
  .hd{min-height:76px;max-width:%(hdmax)spx;padding:0 28px}
  .hdwrap.ovl{margin-bottom:-77px}
  .hdwrap.ovl header{background:transparent;border-bottom-color:transparent;box-shadow:none;
    backdrop-filter:none;-webkit-backdrop-filter:none;transition:background-color .35s,box-shadow .35s,border-color .35s}
  /* 明るい写真（白い天井・白い壁）でも白い文字が読めるよう、帯の所だけ上から薄く暗くする */
  /*   （下の透明な枠線の所に、暗い上端がくり返して細い線に見えないよう、枠線まで1枚で敷く） */
  .hdwrap.ovl:not(.solid) header{background-image:linear-gradient(rgba(20,24,22,.42),rgba(20,24,22,.16) 70%%,rgba(20,24,22,0));
    background-origin:border-box;background-repeat:no-repeat}
  .hdwrap.ovl:not(.solid) .logo,.hdwrap.ovl:not(.solid) nav a{color:#fff;text-shadow:0 1px 12px rgba(0,0,0,.4)}
  .hdwrap.ovl:not(.solid) .logo small{color:rgba(255,255,255,.85)}
  .hdwrap.ovl:not(.solid) nav a::after{background:#fff}
  .hdwrap.ovl .logo,.hdwrap.ovl nav a{transition:color .35s,text-shadow .35s}
  .hdwrap.ovl.solid header{background:rgba(255,255,255,.96);border-bottom-color:var(--line);
    box-shadow:0 2px 12px rgba(40,50,45,.08);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
  /* 帯の分だけ、写真の上の文字の塊を下げる */
  .hdwrap.ovl ~ .hero.full .inner .side{padding-top:125px}
  /* 「イメージ写真です」の札がメニューの電話ボタンに隠れないよう、帯の下へ */
  .hdwrap.ovl ~ .hero.full .shot .lb{top:96px}
  html:has(.hdwrap.ovl) .ewl.is-absorb .logo{color:#fff;transition:transform 1s cubic-bezier(.65,0,.35,1),opacity .45s ease .95s,color .8s ease}
  html:has(.hdwrap.ovl) .ewl.is-absorb .logo small{color:rgba(255,255,255,.85);transition:color .8s ease}
}
"""

# ★2026-11-03 松本さん「テーマカラーをネイビーで統一し、スタイリッシュに」。
#   面積の大きい所（見出し・数字・流れ・お問い合わせの帯・足元・写真の幕・冒頭の演出）はネイビーにそろえ、
#   会社の色は電話のボタン・主なボタン・見出しの強調・小さな点や線だけに残す（「うちの色だ」と感じてもらうため）。
#   地の色も、温かい生成りから少し青みのある白へ。新しい作り（v3）だけに効く
NAVY_CSS = """
:root{--navy:#1b2c47;--navy-d:#121f34;--ground:#f4f5f7;--ink:#1e2a3a;--muted:#5f6b7a;--line:#dce1e7;--panel:#e9edf2}
h2,.card h3,.card.pc h3{color:var(--navy)}
.logo,nav a{color:var(--navy)}
.stats b{color:var(--navy)}
.btn.g:hover{border-color:var(--navy);color:var(--navy)}
.step .si{border-color:var(--navy);color:var(--navy)}
.step .sn{color:var(--navy)}
@media(min-width:760px){.flow .step:not(:last-child)::after{background:var(--navy)}}
.pts .pi{color:var(--navy)}
.card.pc .cph.ci{background:rgba(27,44,71,.07);color:var(--navy)}
.card.pc .cb::after{border-color:var(--navy)}
.contact{background:var(--navy)}
.contact .btn.w{color:var(--navy)}
footer{background:var(--navy-d)}
.mapbox,.gframe{background:linear-gradient(135deg,#e7ebf0 0%,#dfe4ea 55%,#ebeef2 100%);color:#5f6b7a}
.mapbox b,.gframe b{color:var(--navy)}
.ewl-ring .f{stroke:var(--navy)}
.ewl-pct,.ewl .logo{color:var(--navy)}
/* ★2026-11-03 松本さん「スマホの冒頭をコンパクトに。写真・地域名・キャッチ・相談ボタンをひとまとまりで」
   ヘッダーは社名・電話・メニューを1行に（電話は番号を省いて短く）。写真を低くし、
   地域とサービスの一言→見出し→相談ボタン→説明文の順に並べて、最初の画面に収める */
.hero .htag{display:none}
@media(max-width:899px){
  .hd{padding:0 8px 0 14px;min-height:56px}
  .logo{flex:1 1 0;min-width:0;white-space:normal;font-size:clamp(13.5px,3.9vw,15.5px)}
  .logo small{white-space:nowrap;overflow:hidden;text-overflow:clip}
  .hero.full .shot{height:auto;aspect-ratio:16/10;min-height:0;max-height:340px}
  .hero.full .shot .lb{right:10px;bottom:10px;padding:6px 10px;font-size:10.5px;line-height:1.5}
  .hero.full .shot .lb b{font-size:12px}
  .hero.full .shot .lb b::before{width:6px;height:6px}
  .hero.full .side{padding:18px 20px 0}
  .hero .meta{display:contents}
  .hero .htag{display:block;order:-3;margin:0 0 10px;font-size:12.5px;font-weight:700;letter-spacing:.08em;
    color:var(--navy);line-height:1.5}
  .hero .htag::before{content:"";display:inline-block;width:18px;height:2px;background:var(--accent);
    vertical-align:4px;margin-right:8px}
  .hero .since{order:-2}
  .hero .textcol h1{order:-1}
  .hero h1{font-size:min(28px,calc((100vw - 44px) / (var(--hn,12) * 1.1)));line-height:1.6;letter-spacing:.05em;color:var(--navy)}
  .hero h1 .cp+.cp{margin-inline-start:.3em}
  .hero .acts{order:0;margin-top:16px}
  .hero .sub{order:1;margin-top:16px;font-size:13.5px;line-height:1.75}
  .hero .en{order:2}
}
@media(max-width:599px){
  .hd .call .cn{display:none}
  .hd .call{padding:10px 14px}
  .hero .acts{display:block}
  .hero .acts .btn.p{display:block;text-align:center;padding:15px 20px;font-size:15px}
  .hero .acts .btn.g{display:none}
}
@media(min-width:900px){
  .hero.full.fv .shot::before{background:linear-gradient(90deg,rgba(14,24,42,.62) 0%,rgba(14,24,42,.42) 36%,rgba(14,24,42,0) 68%)}
}
"""

# ★メニューが帯に収まらない時の保険（文字幅の見積もりは目安なので、実際に測る）。
#   はみ出していたら、すきま→文字の大きさの順に2段階まで詰める。幅が変わるたびに測り直す
# ★2026-11-02 松本さん「FVの写真はカメラワークを。静止画だと退屈」。写真（と切り替えの写真）を
#   1枚の層（.cam）に入れ、ゆっくり寄りながら左右に流す。札（イメージ写真です）と暗い幕は動かさない。
#   寄り（最大1.08倍）の分の余白より横の移動（1.5%）を小さくして、写真の端が見えないようにする
CAM_CSS = """
.shot.cam-on{overflow:hidden}
.shot .cam{position:absolute;inset:0;display:block;background-size:cover;background-position:center;
  animation:camDrift 26s ease-in-out 1.8s infinite alternate;will-change:transform}
@keyframes camDrift{0%{transform:scale(1) translate3d(0,0,0)}
  50%{transform:scale(1.08) translate3d(-1.5%,-1%,0)}100%{transform:scale(1.05) translate3d(1.5%,.8%,0)}}
html.ewl-on:not(.ewl-go) .shot .cam{animation-play-state:paused}
@media(prefers-reduced-motion:reduce){.shot .cam{animation:none}}
@media print{.shot .cam{animation:none}}
"""

NAVFIT_CSS = """
.hd.fit1 nav{column-gap:18px;font-size:14px;letter-spacing:.04em}
.hd.fit1 .logo{font-size:18px}
.hd.fit1 .call{padding:11px 18px;font-size:13.5px}
.hd.fit2 nav{column-gap:12px;font-size:12.5px;letter-spacing:0}
.hd.fit2 .logo{font-size:16px}
.hd.fit2 .call{padding:10px 14px;font-size:12.5px}
.hd.fit1,.hd.fit2{gap:14px}
"""

NAVFIT_JS = """<script>
(function(){
  var hd=document.querySelector('.hd'),nav=hd&&hd.querySelector('nav');if(!hd||!nav)return;
  var over=function(){return hd.scrollWidth>hd.clientWidth+1||nav.scrollWidth>nav.clientWidth+1;};
  var fit=function(){
    hd.classList.remove('fit1','fit2');
    if(getComputedStyle(nav).display==='none'||getComputedStyle(nav).flexDirection==='column')return;
    if(over())hd.classList.add('fit1');
    if(over()){hd.classList.remove('fit1');hd.classList.add('fit2');}
  };
  fit();addEventListener('resize',fit);addEventListener('load',fit);
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fit);
})();
</script>"""

OVL_JS = """<script>
(function(){
  var w=document.querySelector('.hdwrap.ovl');if(!w)return;
  var n=document.querySelector('.notice'),f=function(){
    var y=(n?n.offsetHeight:0)+24;w.classList.toggle('solid',(window.scrollY||pageYOffset)>y);};
  addEventListener('scroll',f,{passive:true});addEventListener('resize',f);f();
})();
</script>"""

LOADER_HEAD = """<script>
(function(){
  var r=document.documentElement,played=false;
  try{played=sessionStorage.getItem('ewl')==='1';}catch(e){}
  if(played||(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches))return;
  r.classList.add('ewl-on');
  if('scrollRestoration' in history)history.scrollRestoration='manual';
  setTimeout(function(){r.classList.remove('ewl-on');},6000);
})();
</script>"""

LOADER_HTML = """<div class="ewl" id="ewl" aria-hidden="true">
  <div class="ewl-p1">
    <svg class="ewl-ring" viewBox="0 0 120 120"><circle class="t" cx="60" cy="60" r="54"/><circle class="f" cx="60" cy="60" r="54"/></svg>
    <span class="ewl-pct">0%%</span>
  </div>
  <div class="ewl-p2"><div class="logo">%(name)s<small>%(roman)s</small></div></div>
  <span class="ewl-skip">タップでスキップ</span>
</div>"""

LOADER_JS = """<script>
(function(){
  var r=document.documentElement,L=document.getElementById('ewl');
  if(!r.classList.contains('ewl-on')||!L){if(L)L.remove();return;}
  try{sessionStorage.setItem('ewl','1');}catch(e){}
  scrollTo(0,0);
  var real=document.querySelector('.hd .logo'),copy=L.querySelector('.logo'),ended=false;
  // 社名の文字（英字の小見出しより前）の範囲
  var rng=function(el){var g=document.createRange(),sm=el.querySelector('small');g.setStart(el,0);
    if(sm)g.setEndBefore(sm);else g.setEnd(el,el.childNodes.length);return g;};
  var txt=function(el){return rng(el).getBoundingClientRect();};
  // ★2026-11-09 スマホで長い社名はヘッダーで2行に折り返す。演出の社名を1行のままにすると2行目が合わないので、
  //   同じ幅で同じ所で折り返す（2行かどうかは、ヘッダーの社名の各部分の上端の差で見る）
  //   （「株式会社」と「丸信」は別々の箱なので、上端が数px違うだけのものは同じ行とみなす）
  if(real&&copy){var tops=[].map.call(rng(real).getClientRects(),function(x){return x.top;});
    if(tops.length&&Math.max.apply(null,tops)-Math.min.apply(null,tops)>parseFloat(getComputedStyle(real).fontSize)*.8){copy.style.whiteSpace='normal';copy.style.width=Math.ceil(real.getBoundingClientRect().width)+'px';}}
  var show=function(){if(real){real.classList.add('ewl-in');}};
  var end=function(){
    if(ended)return;ended=true;
    r.classList.add('ewl-go','ewl-txt');L.classList.add('is-out');
    setTimeout(function(){r.classList.remove('ewl-on','ewl-go','ewl-txt');L.remove();},500);
  };
  L.addEventListener('click',end);
  var absorb=function(){
    if(ended)return;
    if(real&&copy){
      // 中央に拡大して置いた社名を、ヘッダーの社名にぴったり重なる位置・大きさ（1倍）へ動かす。
      // ★2026-11-09 スマホではヘッダーの社名の枠が横幅いっぱいに広がる（文字は左寄せ）。枠の真ん中どうしを
      //   合わせると、文字が右へずれた所に着いてから本物に入れ替わり、跳んで見えた（丸信で約70px）。
      //   枠ではなく社名の文字（英字の小見出しより前）の左上どうしを合わせる
      var a=copy.getBoundingClientRect(),cx=a.left+a.width/2,cy=a.top+a.height/2;
      var k0=parseFloat(copy.style.getPropertyValue('--ewk'))||1.9,t=txt(copy),u=txt(real);
      var dx=u.left-(cx+(t.left-cx)/k0),dy=u.top-(cy+(t.top-cy)/k0);
      copy.style.transform='translate('+dx+'px,'+dy+'px) scale(1)';
    }
    r.classList.add('ewl-go');          // 幕の下で止めていたトップの動きを、ここから流す
    L.classList.add('is-absorb');
    setTimeout(function(){if(real)real.style.opacity='1';},950);
    setTimeout(function(){r.classList.add('ewl-txt');},850);   // 幕がほぼ透けたところで文字を出し始める
    setTimeout(end,1200);                                       // 幕の白が消えたらすぐ外す（前は 1.8秒待っていた）
  };
  // ★2026-11-02「ローディングの演出はそのままで、表示は会社名のみ。会社名は大きく、長めに」。
  //   輪の中に会社名を大きく置く。輪は会社名が収まる大きさにし、画面の短い辺の8割に収める
  var m=Math.min(innerWidth,innerHeight)*0.82,k=1.9;
  //   円の中で文字の端が線に触れないよう、輪の直径は会社名の幅の1.25倍＋余白
  if(copy){var w=copy.offsetWidth||1;k=Math.max(.8,Math.min(2.2,(m-56)/(w*1.25)));
    // 大きさを決める瞬間は動かさない（既定の 1.9倍 から縮んで見えていた）
    copy.style.transition='none';copy.style.setProperty('--ewk',k.toFixed(3));void copy.offsetWidth;copy.style.transition='';
    var d=Math.round(Math.min(m,w*k*1.25+56));L.style.setProperty('--ewd',d+'px');L.style.setProperty('--ews',(240/d).toFixed(3));}
  requestAnimationFrame(function(){L.classList.add('is-in');});
  var fill=L.querySelector('.ewl-ring .f'),pct=L.querySelector('.ewl-pct');
  var C=2*Math.PI*54,D=1600,t0=null;
  fill.style.strokeDasharray=C;fill.style.strokeDashoffset=C;
  var tick=function(ts){
    if(ended)return;
    if(t0===null)t0=ts;
    var p=Math.min((ts-t0)/D,1),q=1-Math.pow(1-p,3);
    pct.textContent=Math.round(q*100)+'%';
    fill.style.strokeDashoffset=C*(1-q);
    if(p<1){requestAnimationFrame(tick);return;}
    // 輪が満ちたら輪と数字だけ消し、会社名はもう少し見せてからヘッダーへ
    setTimeout(function(){if(ended)return;L.classList.add('is-p2');setTimeout(absorb,900);},250);
  };
  requestAnimationFrame(tick);
})();
</script>"""


def loader_mark(name):
    """輪の中の1文字。会社の種類（株式会社など）を除いた最初の字。"""
    n = re.sub(r"^(株式会社|有限会社|合同会社|合資会社|合名会社|（株）|\(株\)|（有）|\(有\))\s*", "", name)
    n = re.sub(r"\s*(株式会社|有限会社|合同会社)$", "", n)
    return (n or name)[:1]


# ★立体版（2026-11-12 松本さん「見本を立体的にしたい」→ 同日「全てに立体案反映して」で全見本に付ける）。
#   角の形は型ごとのまま（製造は角張っている）。影を深く重ね、写真の後ろに色の板をずらして置き（影で描く。現れる動きで写真が重なりの単位になり、::before では前に出るため）、触れると浮く。浮く動きは translate を使う
#   （現れる動きの animation が transform を持ち続けるので、transform では上書きされて浮かない）
DEPTH_CSS = """
.stats.pts{box-shadow:0 2px 4px rgba(20,30,45,.06),0 24px 56px rgba(20,30,45,.20)!important}
.pts .pi{border-radius:50%;background:linear-gradient(180deg,#fff,#eef1f5);box-shadow:0 6px 14px rgba(20,30,45,.14),inset 0 -2px 0 rgba(ACC,.28)}
.pts .pi svg{width:30px;height:30px}
.cards>.card{border-color:transparent;box-shadow:0 1px 2px rgba(20,30,45,.06),0 12px 30px rgba(20,30,45,.12);
  transition:translate .3s cubic-bezier(.2,.7,.3,1),box-shadow .3s}
.cards>.card:hover{translate:0 -8px;box-shadow:0 2px 4px rgba(20,30,45,.08),0 24px 48px rgba(20,30,45,.20)}
.abph{box-shadow:22px 22px 0 rgba(ACC,.16),0 2px 6px rgba(20,30,45,.10),0 26px 56px rgba(20,30,45,.24)}
.si{background:linear-gradient(180deg,#fff,#eef1f5)!important;border-color:transparent!important;
  box-shadow:0 8px 18px rgba(20,30,45,.16),inset 0 -3px 0 rgba(ACC,.30);transition:translate .3s cubic-bezier(.2,.7,.3,1),box-shadow .3s}
.step:hover .si{translate:0 -5px;box-shadow:0 14px 26px rgba(20,30,45,.22),inset 0 -3px 0 rgba(ACC,.40)}
.info{box-shadow:0 2px 4px rgba(20,30,45,.06),0 18px 42px rgba(20,30,45,.13)}
.mapbox{box-shadow:inset 0 2px 12px rgba(20,30,45,.10)}
@media(min-width:900px){.hero.full h1{text-shadow:0 2px 2px rgba(0,0,0,.22),0 12px 32px rgba(0,0,0,.38)}}
.hero .btn.p{box-shadow:0 10px 26px rgba(ACC,.50)}
.btn{transition:translate .25s,box-shadow .25s,background-color .2s,color .2s}
.btn:hover{translate:0 -2px}
.contact .big{text-shadow:0 2px 0 rgba(0,0,0,.22),0 14px 34px rgba(0,0,0,.40)}
.contact .btn{box-shadow:0 12px 28px rgba(0,0,0,.30)}
.badge{box-shadow:0 14px 30px rgba(ACC,.45),inset 0 -4px 0 rgba(0,0,0,.18)}
@media(max-width:599px){
  .abph{box-shadow:12px 12px 0 rgba(ACC,.16),0 2px 6px rgba(20,30,45,.10),0 18px 40px rgba(20,30,45,.22)}
  .step{box-shadow:0 1px 2px rgba(20,30,45,.05),0 8px 20px rgba(20,30,45,.09)}
}
@media(prefers-reduced-motion:reduce){.cards>.card:hover,.step:hover .si,.btn:hover{translate:none}}
"""


def motion_css(navbp):
    return (MOTION_CSS.replace("SEL", REVEAL_SEL).replace("NAVMAX", str(navbp - 1))
            .replace("NAVMIN", str(navbp)))


def body_js():
    return BODY_JS.replace("SEL", REVEAL_SEL)


# ★EWC への相談の帯（2026-11-13 松本さん）。見本を開いても問い合わせに繋がらない一番の理由は、
#   見本のボタンが相手自身の電話番号にかかり、EWC への連絡先がページ最下部の小さな文字しか無いこと。
#   画面の下に固定して出す。料金は公開中のLP（service.easywebcraft.jp）と同じ表示に合わせる
#   （2026-09-19 の「見本に金額は書かない」は、この日に松本さんの判断で改めた）。
#   電話は載せない（LPの番号が仮のため）。×で説明の文を畳む（料金とボタンは残す。そのタブでは畳んだまま）。印刷では出さない。
#   build.py の型（士業・医院など）も同じ帯を使う。
EWC_PRICE = "初期費用0円・月額5,980円〜（税別）"
EWC_MAIL = "info@easywebcraft.jp"
EWC_LINE = "https://line.me/R/ti/p/@508ijijg"
EWCBAR = """<style>
.ewcbar{position:fixed;left:0;right:0;bottom:0;z-index:80;background:#10294f;color:#fff;
  padding:10px 44px calc(10px + env(safe-area-inset-bottom)) 14px;box-shadow:0 -8px 24px rgba(0,0,0,.2);
  font-family:"Noto Sans JP",system-ui,sans-serif;letter-spacing:.02em}
.ewcbar .in{max-width:1100px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;
  justify-content:center;gap:8px 18px}
.ewcbar p{margin:0;font-size:12.5px;line-height:1.55;text-align:center}
.ewcbar p b{display:inline-block;font-size:12.5px;line-height:1.6}
.ewcbar p b .w{display:inline-block}
/* 前半（社名〜変更可能です）と後半（少しでも〜）のまとまり。PCで入りきらないときは「少しでも」の前で改行される */
.ewcbar p b .g{display:inline-block}
.ewcbar p i{font-style:normal;display:inline-block;color:#ffc93c;font-weight:700}
.ewcbar p > span{display:inline-block;margin-left:.6em;font-size:11px;color:rgba(255,255,255,.7)}
.ewcbar .bt{display:flex;gap:8px;width:100%;max-width:340px;margin:0 auto}
.ewcbar .bt a{flex:1}
@media(min-width:900px){.ewcbar .bt{width:auto;margin:0}.ewcbar .bt a{flex:none}}
.ewcbar a{display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:0 18px;
  border-radius:999px;font-size:13px;font-weight:700;text-decoration:none;white-space:nowrap}
.ewcbar .m{background:#fff;color:#10294f}
.ewcbar .l{background:#06c755;color:#fff}
.ewcbar.min p b,.ewcbar.min p br{display:none}
.ewcbar .x{position:absolute;right:6px;top:6px;width:32px;height:32px;border:0;border-radius:50%;
  background:transparent;color:rgba(255,255,255,.7);font-size:18px;line-height:1;cursor:pointer}
body{padding-bottom:190px}
.badge{bottom:104px!important}
@media(min-width:900px){body{padding-bottom:84px}.ewcbar .in{flex-wrap:nowrap}.ewcbar p{text-align:left;flex:1 1 auto}.ewcbar p b{font-size:13.5px}}
@media print{.ewcbar{display:none}body{padding-bottom:0}}
</style>
<div class="ewcbar" role="region" aria-label="EasyWebCraft へのご相談">
  <div class="in">
    <p><b><span class="g"><span class="w">@@NAME@@様向けに制作した<span class="w">デザイン案です。</span></span><span class="w">文章やデザインは</span><span class="w">ご要望に応じて変更可能です。</span></span><span class="g"><span class="w">少しでもご興味があれば、</span><span class="w">お気軽にお問い合わせください。</span></span></b><br><i>@@PRICE@@</i> <span>EasyWebCraft</span></p>
    <div class="bt"><a class="m" href="@@MAILTO@@">メールで相談</a><a class="l" href="@@LINE@@" target="_blank" rel="noopener">LINEで相談</a></div>
  </div>
  <button class="x" type="button" aria-label="閉じる">×</button>
</div>
<script>
(function(){var b=document.querySelector('.ewcbar');if(!b)return;var x=b.querySelector('.x');
/* 帯の高さは社名の長さと画面の幅で変わるので、ページ下の余白を帯の実際の高さに合わせる（最下部の文字が隠れないように） */
function fit(){document.body.style.paddingBottom=(b.offsetHeight+8)+'px';}
/* ×は帯ごと消さず、説明の文だけ畳む（料金とボタンは残す。2026-11-13 松本さん）。もう一度押すと説明が出る */
function set(min){b.classList.toggle('min',min);x.textContent=min?'＋':'×';
  x.setAttribute('aria-label',min?'説明を表示':'説明をたたむ');fit();
  try{sessionStorage.setItem('ewcbar',min?'min':'');}catch(e){}}
var st='';try{st=sessionStorage.getItem('ewcbar')||'';}catch(e){}
set(st==='min'||st==='0');window.addEventListener('resize',fit);
x.addEventListener('click',function(){set(!b.classList.contains('min'));});
})();
</script>"""


def ewc_bar(name):
    """画面の下に固定する EWC への相談の帯。メールは件名に会社名を入れて開く。"""
    from urllib.parse import quote
    mailto = "mailto:%s?subject=%s" % (EWC_MAIL, quote(f"{name}様の見本について"))
    # ★目印は @@…@@ にする。「LINE」のままだとボタンの「LINEで相談」まで置き換わった（2026-11-13）
    return (EWCBAR.replace("@@NAME@@", H.escape(name)).replace("@@PRICE@@", H.escape(EWC_PRICE)).replace("@@MAILTO@@", H.escape(mailto))
            .replace("@@LINE@@", H.escape(EWC_LINE)))


# ★写真があるときのヒーロー（2026-09-19）。参考サイト（達匠・大洋画地）と同じ、
#   画面いっぱいの写真に文字を重ねる型。枠時代の設計（右半分の小さな枠）は写真が無い前提
#   だったので、写真がある先だけ .hero.full に切り替える。
#   スマホは写真の上に文字を重ねず、写真の直下に置く（重ねると読めなくなる。かみのてで経験済み）。
HERO_FULL_CSS = """
@keyframes zoomOut{from{transform:scale(1.04)}to{transform:none}}
.hero.full{padding:0 0 12px}
.hero.full::before,.hero.full::after,.hero.full .inner::before,.hero.full .tex,.hero.full .tagline{display:none}
.hero.full .inner{display:flex;flex-direction:column;max-width:none;padding:0;gap:0}
.hero.full .shot{order:-1;width:100vw;margin-left:calc(50% - 50vw);aspect-ratio:auto;height:58vh;
  min-height:300px;max-height:520px;border:0;border-radius:0;outline:0;
  animation:zoomOut 1.8s cubic-bezier(.2,.7,.3,1) both}
.hero.full .shot .lb{left:auto;right:14px;bottom:14px}
.hero.full .side{max-width:1120px;margin:0 auto;padding:22px 20px 0;width:100%}
.hero.full .scroll{display:none}
@media(min-width:900px){
  .hero.full{padding:0 0 20px}
  .hero.full .inner{display:block;position:relative;min-height:min(74vh,700px)}
  .hero.full .shot{position:absolute;inset:0;width:auto;margin:0;height:auto;max-height:none;order:0}
  /* 文字が読めるように、左を濃く右を薄く */
  .hero.full .shot::before{content:"";position:absolute;inset:0;
    z-index:1;background:linear-gradient(90deg,rgba(20,18,14,.62) 0%,rgba(20,18,14,.32) 55%,rgba(20,18,14,.12) 100%)}
  .hero.full .shot .lb{z-index:2}
  /* ★2026-11-01「FVのインパクトを出したい、全体的に暗い」。写真を切り替える先（.fv＝住宅）だけ、
     高さを画面いっぱいに、黒い幕は文字の後ろ（左4割）だけにして写真の明るさを見せる。見出しも2割大きく。
     ほかの業種は写真が暗め・込み入っているものがあり、幕を薄くすると文字が読めなくなるので前のまま */
  .hero.full.fv{--h1k:1.22}
  .hero.full.fv .inner{min-height:max(600px,min(calc(100vh - 96px),900px))}
  .hero.full.fv .vt{max-height:600px}
  .hero.full.fv .shot::before{background:linear-gradient(90deg,rgba(20,18,14,.58) 0%,rgba(20,18,14,.40) 36%,rgba(20,18,14,0) 68%)}
  .hero.full.fv .side{padding-bottom:110px}
  .hero.full .side{position:relative;z-index:1;align-items:flex-start;padding:64px 20px 96px}
  .hero.full .textcol{justify-content:flex-start;gap:34px}
  .hero.full .textcol h1{order:-1}
  .hero.full h1,.hero.full .sub,.hero.full .en{color:#fff;text-shadow:0 1px 14px rgba(0,0,0,.35)}
  .hero.full h1 em{color:#fff;text-shadow:0 0 0 #fff,0 1px 14px rgba(0,0,0,.35)}
  .hero.full .meta{padding-top:8px}
  .hero.full .btn.g{background:rgba(255,255,255,.14);color:#fff;border-color:rgba(255,255,255,.7)}
  .hero.full .btn.g:hover{background:#fff;color:var(--ink)}
  /* 下端は数字の帯が重なるので、札は右上・scroll はその上に置く */
  .hero.full .shot .lb{bottom:auto;top:18px;right:18px;left:auto}
  .hero.full .scroll{display:block;color:#fff;bottom:66px}
  .hero.full .scroll::after{background:#fff}
  /* 数字の帯を写真の下端に少し重ねる */
  .hero.full .stats{margin-top:-44px;position:relative;z-index:2}
  .hero.full .stats div{box-shadow:0 10px 30px rgba(20,18,14,.10)}
}
/* 2枚目以降の写真。各ページで切り替えの間合い（@keyframes heroSl）を書き足す */
.hero.full .shot .sl{position:absolute;inset:0;background-size:cover;background-position:center;opacity:0}
@media(prefers-reduced-motion:reduce){.hero.full .shot{animation:none}.hero.full .shot .sl{animation:none!important}}
@media print{
  .hero.full .inner{min-height:0;display:block}
  .hero.full .shot{position:relative;inset:auto;width:auto;margin:0;height:auto;aspect-ratio:16/7;
    border:1px solid var(--line);animation:none!important}
  .hero.full .shot::before{display:none}
  .hero.full .side{padding:12px 0 0}
  .hero.full h1,.hero.full .sub,.hero.full .en,.hero.full h1 em{color:var(--ink);text-shadow:none}
  .hero.full .btn.g{background:#fff;color:var(--ink);border-color:var(--ink)}
  .hero.full .stats{margin-top:12px}
}
"""


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
  border-radius:16px;padding:6px 18px 6px 16px;font-size:13px;box-shadow:0 2px 10px rgba(20,30,50,.05);
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
def nav_breakpoint(d, ind, big=False):
    """メニューを横に並べられる最小の幅。big は v3 の大きなメニュー（OVL_CSS）で並べられる幅。"""
    labels = (nav_labels(d) + ["お問い合わせ"]) if d.get("nav") else [ind["svc"], ind["flow_h"], "会社概要", "お問い合わせ"]
    nav = sum(_tw(x, 17.7 if big else 14.3) for x in labels) + (len(labels) - 1) * (30 if big else 22)
    logo = _tw(d["name"], 22 if big else 18.4)
    call = _tw("お電話 " + d.get("tel", ""), 15.5 if big else 14.5) + (52 if big else 40)
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


# ★2026-11-03 松本さん「スマホの冒頭で、どこの会社で何を頼めるかを伝える」。見出しの上に添える一言。
#   sites.json の "hero_tag" があればそれ。無ければ住所の市町村と、できることの先頭（長ければ1つ）から作る
def hero_tag(d):
    if d.get("hero_tag"):
        return d["hero_tag"]
    m = re.search(r"(?:都|道|府|県)(?:.+?郡)?(.+?[市町村])", d.get("addr", ""))
    svc = [t for t, _ in d.get("services", [])][:2]
    svc = "／".join(svc) if sum(map(len, svc)) <= 15 else (svc[0] if svc and len(svc[0]) <= 15 else "")
    return "｜".join(x for x in ((m.group(1) if m else ""), svc) if x)


def headline(d, e):
    """見出しのHTMLと、縦書きのときの文字の大きさ。"""
    a, b = vsplit(d["catch"]), vsplit(d["catch_em"])
    px = max(26, min(40, int(VBUDGET / (max(len(x) for x in a + b) * 1.14))))
    html = "<br>".join(copy_html(x, e) for x in a)
    html += "<br><em>" + "<br>".join(copy_html(x, e) for x in b) + "</em>"
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


# コピー（キャッチ・見出しの一言）は読点・句点を付けない（松本さんの指示 2026-11-02）。
# 読点のあった所は少しあけて、その切れ目でだけ折り返す
def copy_html(text, e):
    parts = [x for x in re.split(r"[、。]", text) if x]
    return "".join(f'<span class="cp">{e(x)}</span>' for x in parts)


def _bigrams(text):
    t = "".join(c for c in text if c not in "・／/ 　のとをごおはが")
    return {t[i:i + 2] for i in range(len(t) - 1)} or {t}


# ★メニューの項目は、対応するサービスカードまで飛ばす。
#   最初は全部 #works に飛ばしていたが、中駒だと7項目のうち5つが同じ場所に着地した。
#   2つ押せば「同じところに戻る＝中身が無い」と分かってしまう。
# ★2026-11-09 sites.json のメニューに「お問い合わせ」を書くと、末尾に必ず足す窓口と2つ並んでいた
#   （尾張の見本で発覚。表記ゆれ「お問合せ」「お問合わせ」も同じ）。書いてあっても1つにまとめる
CONTACT_LABEL = re.compile(r"^お問い?合わ?せ")


def nav_labels(d):
    """sites.json のメニューから、末尾に必ず足す「お問い合わせ」と重なる項目を除いたもの。"""
    return [x for x in (d.get("nav") or []) if not CONTACT_LABEL.match(x)]


def nav_targets(d, ind):
    """メニューの項目名 → 飛び先。当てはまるカードが無い項目は None で返す。"""
    labels = nav_labels(d)
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
        # ★総称（業務内容・事業案内・◯◯サービス）は「できること」全体で受ける。
        #   「リフォームサービス」が「水廻りリフォーム」のカードに強く一致して、
        #   1枚に着地していた（2026-09-19）
        elif (any(k in label for k in ("業務内容", "事業内容", "事業案内", "業務案内", "サービス一覧",
                                        "取扱商品", "商品のご案内")) or label.endswith("サービス")) \
                and not any(t == label or (len(t) >= 4 and (t in label or label in t)) for t in svc):
            # 同名のカードがある（松岡設計の「プラン提案サービス」）ときはカードを優先
            pairs[label] = "#works"
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


import hashlib
import os

PHOTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")


SLIDE_SEC = 6       # 1枚を見せる秒数


def hero_slides(pids):
    """トップの2枚目以降の写真を重ねる層と、その切り替えの間合い。
    n枚を SLIDE_SEC 秒ずつ、1秒かけて重ねて替える（1枚目は .shot の背景のまま下に敷く）。"""
    if not pids:
        return ""
    n = len(pids) + 1
    cyc = n * SLIDE_SEC
    a = 100 / cyc                     # 1秒が周期の何％か
    on = SLIDE_SEC * a
    kf = (f"@keyframes heroSl{{0%{{opacity:0;transform:scale(1.08)}}{a:.2f}%{{opacity:1}}"
          f"{on + a:.2f}%{{opacity:1}}{on + 2 * a:.2f}%{{opacity:0;transform:none}}100%{{opacity:0}}}}")
    layers = "".join(
        f'<i class="sl"{photo_style(p)[:-1]};animation:heroSl {cyc}s linear {i * SLIDE_SEC - 1}s infinite"></i>'
        for i, p in enumerate(pids, 1))
    return f"<style>{kf}</style>{layers}"


def photo_style(pid):
    """photos/<id>.jpg を参照する style 属性にする。無ければ空（枠のまま）。"""
    if not pid:
        return ""
    # "id@50% 85%" のように @ の後ろで切り出す位置を指定できる（既定は中央）
    pid, _, pos = pid.partition("@")
    path = os.path.join(PHOTO_DIR, pid + ".jpg")
    if not os.path.exists(path):
        raise SystemExit(f"写真が無い: {path}（PHOTOS.md の手順で取得する）")
    # ★内蔵（data URI）にしない。1ページ 500KB になり、再生成のたびに git に積まれる。
    #   同じリポジトリ内の相対参照なので「外部リソースを読み込まない」方針は崩れない
    extra = f";background-position:{pos}" if pos else ""
    # ★写真を取り直しても名前が同じだと、ブラウザと GitHub Pages のキャッシュに古い版が残る
    #   （低解像度のまま見えていた原因）。中身のハッシュを ?v= に付けて、変わったら別URLにする
    with open(path, "rb") as f:
        ver = hashlib.md5(f.read()).hexdigest()[:8]
    return f' style="background-image:url(../photos/{pid}.jpg?v={ver}){extra}"'


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
    css += LOADER_CSS
    if (d.get("photos") or {}).get("hero"):
        css += HERO_FULL_CSS
    # ★2026-11-02 から全見本を v3 の形にする（松本さん「この形に全体的に切り替えて」）。
    #   写真の無い所は空の枠を出さず、絵のカード・トップの写真で埋める
    v3 = not d.get("_classic")
    v2 = bool(d.get("_v2")) or v3      # v3 は v2 の「仮の表示を出さない」を引き継ぐ
    if v2:
        css += V2_CSS % {"acc_rgb": acc_rgb}
    if v3:
        css += V3_CSS % {"acc_rgb": acc_rgb}
        navbig = nav_breakpoint(d, ind, big=True)
        # メニューの多い会社は、帯の中身の幅（既定 1240px）に収まらず右端が切れた。広い画面では中身の幅も広げる
        css += OVL_CSS % {"navbp": max(navbp, 900), "navbig": navbig, "hdmax": max(1240, min(1680, navbig + 100))}
        css += NAVFIT_CSS + CAM_CSS
        css += NAVY_CSS
    css += DEPTH_CSS.replace("ACC", acc_rgb)   # ★2026-11-12 から全見本を立体版に（松本さん「全てに立体案反映して」）
    roman = d.get("roman", "")
    since = bigen = tagline = badge = ""
    htag = f'<p class="htag">{e(hero_tag(d))}</p>' if v3 and hero_tag(d) else ""
    hn = max(len(re.sub(r"[、。]", "", x)) for x in vsplit(d["catch"]) + vsplit(d["catch_em"]))
    news_t = ind.get("news_hint", "お知らせが入ります（工事のご報告・休業日など）")
    if skin == "seizo":
        if d.get("founded"):
            since = f'<p class="since">SINCE {e(d["founded"])}</p>'
        if roman:
            bigen = f'  <p class="bigen" aria-hidden="true">{e(roman)}</p>\n'
    else:
        # TATSUSHO の型: 左端の縦書きの一言と、丸い CONTACT のバッジ（広い画面だけ出る）
        tagline = f'\n  <p class="tagline">{copy_html(d.get("svc_lead") or ind["svc_lead"], e)}</p>'
        badge = ('\n<a class="badge" href="#contact" aria-label="お問い合わせ">'
                 '<svg viewBox="0 0 100 100" aria-hidden="true"><defs><path id="bc" d="M50,50 m-38,0 a38,38 0 1,1 76,0 a38,38 0 1,1 -76,0"/></defs>'
                 '<text><textPath href="#bc">CONTACT · CONTACT · CONTACT · </textPath></text></svg>'
                 '<span>ご相談<br>ください</span></a>')
    # ★お知らせは3件（2026-09-21）。1件だと「置いてあるだけ」に見える。種類の違う3件で
    #   「更新できるサイト」だと伝える。文言は業種ごと（build.py の news_items）
    items = ind.get("news_items") or ["お知らせのタイトルが入ります"] * 3
    dates = ("2026.09.01", "2026.08.20", "2026.08.05")
    rows_html = "".join(
        f'<div class="row"><span class="dot"></span><span class="date">{dt}</span>'
        f'<span class="t">{e(t)}</span></div>' for dt, t in zip(dates, items))
    news = (f'\n<div class="news" id="news"><div class="wrap"><div class="pill">'
            '<span class="lbl">お知らせの<br>表示例</span>'
            f'<div class="rows">{rows_html}</div>'
            '<a class="more" href="#contact">NEWS →</a></div></div></div>')

    if v2:
        news = ""        # 試作：表示例のお知らせは出さない（仮の表示に見えるため）
    stats = "".join(f'<div><b>{e(a)}<small>{e(b)}</small></b><span>{e(c)}</span></div>'
                    for a, b, c in d["stats"])
    stats_cls = "stats"
    if v3:
        # v3：数字の帯の代わりに、線の絵＋見出し＋一言（sites.json の points = [絵, 見出し, 一言]）。
        #   書いていない先は数字の帯（stats）から作る：「1981」「年」「創業」→ 1981年 ／ 創業
        #   見出しは大きい字と小さい字を並べたまま（「瑞穂」「東京」を「瑞穂東京」とつなげないため）
        if d.get("points"):
            pts = [(ic, e(t), c) for ic, t, c in d["points"]]
        else:
            pts = [(point_icon(a, b, c), f'{e(a)}<i>{e(b)}</i>', c) for a, b, c in d["stats"]]
        stats_cls = "stats pts"
        stats = "".join(f'<div><span class="pi">{icon_svg("", ic)}</span><span class="pt"><b>{t}</b>'
                        f'<small>{e(c)}</small></span></div>' for ic, t, c in pts)
    sph = ((d.get("photos") or {}).get("svc") or auto_svc_photos(d)) if v3 else None
    if sph:
        # v3：写真付きのカード（sites.json の photos.svc、無ければ項目名から選ぶ）。
        #   写真の無い枠は、項目名の絵を写真の大きさで出す（空の枠を見せないため）
        def cph(i, t):
            st = photo_style(sph[i] if i < len(sph) else None)
            return (f'<div class="cph ph"{st}></div>' if st else
                    f'<div class="cph ci">{icon_svg(t)}</div>')
        cards = "".join(
            f'<div class="card pc" id="svc{i}">{cph(i - 1, t)}<div class="cb"><h3>{e(t)}</h3>'
            f'<p>{e(p)}</p></div></div>'
            for i, (t, p) in enumerate(d["services"], 1))
    elif v2:
        cards = "".join(
            f'<div class="card" id="svc{i}"><span class="ic">{icon_svg(t)}</span><span class="no" aria-hidden="true">{i:02d}</span>'
            f'<h3>{e(t)}</h3><p>{e(p)}</p></div>'
            for i, (t, p) in enumerate(d["services"], 1))
    else:
        cards = "".join(
            f'<div class="card" id="svc{i}"><h3>{e(t)}</h3><p>{e(p)}</p></div>'
            for i, (t, p) in enumerate(d["services"], 1))
    steps = "".join(f'<div class="step"><h3>{e(t)}</h3><p>{e(p)}</p></div>'
                    for t, p in ind["flow"])
    if v3:
        steps = "".join(f'<div class="step"><span class="si">{icon_svg(t, FLOW_ICONS[min(i, 3)])}</span>'
                        f'<span class="sn">{i + 1:02d}</span><h3>{e(t)}</h3><p>{e(p)}</p></div>'
                        for i, (t, p) in enumerate(ind["flow"]))

    # メニューに「実績」「事例」がある先には、その受け皿を作る。
    # 無いと項目を押しても「できること」に着地して、中身が無いのが分かる。
    photos = d.get("photos") or {}
    hero_ph = photo_style(photos.get("hero"))
    slides = hero_slides(photos.get("slides") if hero_ph else None)
    hero_lb = ("<b>イメージ写真です</b>実際の制作では御社のお写真に差し替えます" if hero_ph else
               f'<b>お写真が入ります</b>{e(ind.get("shot", "現場のようす・完成した建物など"))}')
    gal = d.get("gallery")
    gallery = ""
    flow_cls, comp_cls = ' class="alt"', ""
    if gal:
        flow_cls, comp_cls = "", ' class="alt"'
        gph = photos.get("gallery") or []
        frames = ""
        for i, c in enumerate(gal[:3]):
            st = photo_style(gph[i] if i < len(gph) else None)
            if st:
                frames += f'<div class="gframe ph"{st}><span class="cap"><b>イメージ写真です</b>{e(c)}（御社のお写真に差し替え）</span></div>'
            else:
                frames += f'<div class="gframe"><b>お写真が入ります</b>{e(c)}</div>'
        gallery = f"""<section class="alt" id="gallery">
  <div class="wrap">
    <div class="sechead"><span class="en">WORKS</span>
      <h2>{e(d.get("gallery_h", "これまでの仕事"))}</h2>
      <p>お預かりしたお写真を、ここに並べます。</p></div>
    <div class="gal">{frames}</div>
  </div>
</section>"""

    ab = (d.get("about") or auto_about(d, photos)) if v3 else None
    if ab:
        # v3：写真と紹介文を左右に（画像の「暮らしのそばに」の段）。写真は外観のイメージ
        st = photo_style(ab.get("photo"))
        abph = (f'<div class="abph ph"{st}><span class="cap">{e(ab.get("cap", "外観写真イメージ"))}</span></div>' if st
                else '<div class="abph"><b>お写真が入ります</b>お店・会社の外観</div>')
        gallery = f"""<section class="alt about" id="about">
  <div class="wrap abrow">{abph}
    <div class="abtx"><span class="en">ABOUT US</span><h2>{copy_html(ab["h"], e)}</h2>
      {"".join(f"<p>{phrase(x, e)}</p>" for x in ab["p"])}
      <a class="btn p" href="#company">{e(ab.get("btn", "会社概要"))}</a></div>
  </div>
</section>"""
        flow_cls, comp_cls = "", ' class="alt"'

    feat = ""
    if v2 and d.get("features"):
        rows_f = ""
        for i, f in enumerate(d["features"], 1):
            st = photo_style(f.get("photo"))
            ph = (f'<div class="fph"{st}><span class="cap">イメージ写真</span></div>' if st else "")
            rows_f += (f'<div class="frow">{ph}<div class="ftx"><span class="no">{i:02d}</span>'
                       f'<h3>{phrase(f["h"], e)}</h3><p>{e(f["p"])}</p></div></div>')
        feat = f"""\n<section class="feat" id="feature">
  <div class="wrap">
    <div class="sechead"><span class="en">OUR WORK</span><h2>{e(d.get("features_h", "大切にしていること"))}</h2></div>
    <div class="frows">{rows_f}</div>
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
    # ★信用の材料（2026-09-21）。建設業許可番号・ISO は相手のサイトに公開されている事実。
    #   ~/kmtools/permitfind.py で拾う。1行あるだけで「ちゃんとした会社」に見える
    if d.get("permits"):
        info.append(("許可・登録", "／".join(d["permits"])))
    rows = "".join(f'<tr><th>{e(k)}</th><td>{v if k=="電話" else e(v)}</td></tr>'
                   for k, v in info)

    nav = nav_html(d, ind, e)
    # ★2026-11-02 松本さん「メニューは押しても反応しないように。基本は専用ページを用意するので、
    #   ページ内へ飛ぶ動きは逆に出したくない」。リンク先を外し、合わせた時の色と下線だけ残す
    nav = re.sub(r' href="[^"]*"', '', nav)
    # サイトの構成: メニューは6件までしか横に入らないが、ここは全項目を出す
    if d.get("nav"):
        pairs = nav_targets(d, ind) + [("お問い合わせ", "#contact")]
    else:
        pairs = [(ind["svc"], "#works"), (ind["flow_h"], "#flow"), ("会社概要", "#company"), ("お問い合わせ", "#contact")]
    sitemap = "".join(f'<li><a href="{href or "#works"}">{e(label)}</a></li>' for label, href in pairs)
    call = (f'<a class="call" href="tel:{e(tl)}">お電話<span class="cn"> {e(tel)}</span></a>' if tel
            else '<a class="call" href="#contact">お問い合わせ</a>')
    if skin == "seizo":
        # 長峰の型: 右端に角ばったボタンを2つ（お問い合わせ／資料請求）
        call = f'<div class="calls">{call}<a class="call2" href="#contact">資料請求</a></div>'
    hero_btn = (f'<a class="btn p" href="tel:{e(tl)}">{"お見積り・ご相談" if v3 else "電話で相談する"}</a>' if tel else "")
    hours_html = ("" if v2 and "が入ります" in ind["hours"] else f'<small>{e(ind["hours"])}</small>')
    ctel = (f'<a class="big" href="tel:{e(tl)}">{e(tel)}</a>'
            f'{hours_html or "<small></small>"}'
            f'<div><a class="btn w" href="tel:{e(tl)}">電話をかける</a></div>'
            if tel else f'<small>{e(ind["hours"])}</small>')

    loader = LOADER_HTML % {"mark": e(loader_mark(name)), "name": e(name), "roman": e(roman)}
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
{LOADER_HEAD}
</head>
<body>
{loader}

<div class="notice slim"><span class="ph"><i></i><span class="ewc">EasyWebCraft の</span>提案用の見本｜</span><span class="ph">{e(short_name(name))}さまの公式サイトではありません</span></div>

<div class="hdwrap{" ovl" if v3 and hero_ph else ""}">
  <header><div class="hd">
    <div class="logo">{logo_name(name)}<small>{e(roman)}</small></div>
    <nav>{nav}</nav>
    {call}
  </div></header>
</div>

<div class="hero{" tx" if tex else ""}{" full" if hero_ph else ""}{" fv" if slides else ""}">
  {tex}{tagline}
  <div class="wrap inner">
    <div class="side">
      <div class="textcol">
        <div class="meta">
          <p class="sub">{sub_html}</p>
          <p class="en">{e(roman)}</p>
          <div class="acts">{hero_btn}<a class="btn g" href="#works">{e(ind["svc"])}を見る</a></div>
        </div>
        {htag}{since}<h1 class="vt" style="--hn:{hn}">{h1_html}</h1>
      </div>
    </div>
    {f'<div class="shot ph cam-on"><i class="cam"{hero_ph}>{slides}</i>' if v3 and hero_ph else f'<div class="shot{" ph" if hero_ph else ""}"{hero_ph}>{slides}'}
      <div class="lb">{hero_lb}</div>
    </div>
    <span class="scroll">scroll</span>
  </div>
{bigen}  <div class="wrap"><div class="{stats_cls}">{stats}</div></div>
</div>
{news}{feat}
<section id="works">
  <div class="wrap">
    <div class="sechead"><span class="en">SERVICE</span>
      <h2>{e(ind["svc"])}</h2><p>{copy_html(ind["svc_lead"], e)}</p></div>
    <div class="cards">{cards}</div>
  </div>
</section>

{gallery}

<section{flow_cls} id="flow">
  <div class="wrap">
    <div class="sechead"><span class="en">FLOW</span>
      <h2>{e(ind["flow_h"])}</h2>{"" if v2 else "<p>" + phrase("流れの一例です。実際の制作では、御社の進め方に合わせて書き換えます。", e) + "</p>"}</div>
    <div class="flow">{steps}</div>
  </div>
</section>

<section{comp_cls} id="company">
  <div class="wrap"{"" if v3 else ' style="max-width:720px"'}>
    <div class="sechead"><span class="en">COMPANY</span><h2>{e(d.get("company_h", "会社概要")) if v3 else "会社概要"}</h2></div>
    {'<div class="cgrid">' if v3 else ""}<table class="info">{rows}</table>
    {'<div class="mapbox"><b>地図が入ります</b>実際の制作で、お店の場所の地図を入れます</div></div>' if v3 else "" if v2 else '<div class="mapbox"><b>地図が入ります</b>最寄り駅・駐車場のご案内もここに</div>'}
  </div>
</section>

<div class="contact{" tx" if ctex else ""}" id="contact">
  {ctex}
  <h2>{copy_html(ind["cta"], e)}</h2>
  <p>{e(ind["cta_sub"])}</p>
  {ctel}
  <p class="note">{phrase("見本の電話のボタンは、御社の電話番号につながります。", e)}{phrase("メールフォーム・LINEでのお問い合わせ窓口は、実際の制作でお付けします。", e)}</p>
</div>

<section class="sitemap" id="sitemap">
  <h2>サイトの構成</h2>
  <p>この見本はトップページだけです。実際の制作では、次のページをお作りします。</p>
  <ul>{sitemap}</ul>
</section>

{badge}
<footer>
  <span class="ph">この見本は EasyWebCraft が作成した提案資料です。</span><span class="ph">{e(name)}さまの公式サイトではありません。</span><br>
  <span class="ph">トップページだけを形にした見本で、</span><span class="ph">メニューの各ページは実際の制作でお作りします。</span><br>
  <span class="ph">実際の制作では、</span><span class="ph">御社の写真・実績・文章に差し替えて仕上げます。</span>
  <div class="next"><b>この見本を本物のサイトにするには</b>
    <ol>
      <li>{phrase("御社の写真と文章をお預かりします（見本の写真・文章は当社が用意したものです）", e)}</li>
      <li>{phrase("お預かりしたものを入れて、公開まで当社で仕上げます", e)}</li>
      <li>{phrase(EWC_PRICE + "。", e)}{phrase("制作と公開、スマートフォン対応、公開後の修正、安全性の対応、検索対策、運用サポートは月額に含まれます", e)}</li>
    </ol>
  </div>
  <p class="by"><span class="ph">EasyWebCraft（担当：田代）</span><span class="ph"><a href="mailto:info@easywebcraft.jp">info@easywebcraft.jp</a></span></p>
</footer>

{ewc_bar(name)}
{body_js()}
{OVL_JS if v3 and hero_ph else ""}
{NAVFIT_JS if v3 else ""}
{LOADER_JS}
</body>
</html>
"""


# =====================================================================
# 試作（v2・2026-10-31）：松本さん「開いてもこの程度かと思われたくない」から。
#   build.py --trial <キー> のときだけ使う（今の見本は変えない）。出力は <キー>-v2/
#   ・ヒーローの下が「白い箱に文字」だけで続いて設計図のように見えたので、
#     写真と文字を左右に並べる「大切にしていること」（sites.json の features）を足す
#   ・「できること」に線の絵と番号を付けて、6つ同じ箱の単調さをなくす
#   ・仮の表示（お知らせの表示例・地図の灰色の枠・「流れの一例です」・受付時間の仮の文）を出さない
# =====================================================================
ICONS = {  # 24×24 の線の絵。stroke は文字色
    "house": '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 9.8V20h13V9.8"/><path d="M10 20v-5.5h4V20"/>',
    "build": '<path d="M4 20V7l6-3v16"/><path d="M10 9h10v11"/><path d="M3 20h18"/><path d="M13 12.5h1.5M16.5 12.5H18M13 16h1.5M16.5 16H18M6.5 9.5h1M6.5 13h1M6.5 16.5h1"/>',
    "pin": '<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="m11 12 8.5-8.5M16 7l2.5 2.5M14 9l2 2"/>',
    "tool": '<path d="M14.5 6.5a4 4 0 0 0 5 5L11 20a2.1 2.1 0 0 1-3-3l8.5-8.5"/><path d="M14.5 6.5 17 4l3 3-2.5 2.5"/>',
    "shield": '<path d="M12 3.5 19 6v5.5c0 4.4-3 7.6-7 9-4-1.4-7-4.6-7-9V6z"/><path d="m8.8 12 2.2 2.2 4.3-4.4"/>',
    "plan": '<rect x="4" y="4" width="16" height="16" rx="1.5"/><path d="M4 11h7v9M11 11V4M15 4v7h5"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21M5.6 5.6l1.8 1.8M16.6 16.6l1.8 1.8M5.6 18.4l1.8-1.8M16.6 7.4l1.8-1.8"/>',
    "roller": '<rect x="4" y="4" width="13" height="5" rx="1"/><path d="M17 6.5h2.5V12H11v3"/><rect x="9.5" y="15" width="3" height="5.5" rx="1"/>',
    "drop": '<path d="M12 3.5s6 6.4 6 10.5a6 6 0 0 1-12 0c0-4.1 6-10.5 6-10.5z"/>',
    "bolt": '<path d="M13 3 5.5 13.5H12L11 21l7.5-10.5H12z"/>',
    "car": '<path d="M5 16.5V12l2-5h10l2 5v4.5"/><path d="M3.5 16.5h17"/><circle cx="7.5" cy="16.5" r="1.8"/><circle cx="16.5" cy="16.5" r="1.8"/><path d="M5.5 12h13"/>',
    "leaf": '<path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z"/><path d="M5 19 13 11"/>',
    "doc": '<path d="M7 3.5h7l4 4V20.5H7z"/><path d="M14 3.5v4h4M9.5 12h6M9.5 15.5h6"/>',
    "cal": '<rect x="4" y="5.5" width="16" height="14.5" rx="1.5"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>',
    "check": '<circle cx="12" cy="12" r="8.5"/><path d="m8.3 12.2 2.6 2.6 4.9-5"/>',
    "phone": '<path d="M6.5 3.5h3l1.5 4-2 1.3a11 11 0 0 0 6.2 6.2l1.3-2 4 1.5v3a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 4.5 5.7a2 2 0 0 1 2-2.2z"/>',
    "hand": '<path d="M2.5 11.5 6 8l3 1 3-2.5 3.5 1L21.5 12"/><path d="M6 8l-3.5 3.5L8 17l1.5-1.2 1.5 1.2 1.5-1.2 1.5 1.2 1.5-1.2L19 12"/><path d="M12 6.5 9 9.5a1.4 1.4 0 0 0 2 2l2.5-2"/>',
    "chat": '<path d="M4.5 5.5h15v10h-8l-4 3.5v-3.5h-3z"/><path d="M8.5 9.5h7M8.5 12h4.5"/>',
}
ICON_HINTS = (  # 項目名に含まれる語 → 絵。上から順に見る
    (("引渡", "点検", "保証", "アフター", "メンテ", "保全", "保険"), "shield"),
    (("土地", "不動産", "物件", "立地"), "pin"),
    (("中古", "賃貸", "売買", "仲介"), "key"),
    (("リフォーム", "修理", "修繕", "改修", "補修", "直し"), "tool"),
    (("設計", "プラン", "図面", "間取り", "監理"), "plan"),
    (("分譲", "マンション", "ビル", "施設", "店舗", "公共"), "build"),
    (("塗装", "塗り", "外壁"), "roller"),
    (("水", "配管", "給排水", "浴"), "drop"),
    (("電気", "電設", "計装", "太陽光"), "bolt"),
    (("車", "板金", "車検"), "car"),
    (("造園", "庭", "緑"), "leaf"),
    (("機械", "製作", "加工", "製造", "装置", "治具"), "gear"),
    (("相談", "ご案内", "Q&A", "質問"), "chat"),
    (("住宅", "家", "新築", "住まい"), "house"),
)


FLOW_ICONS = ("phone", "house", "doc", "tool")   # v3 の流れ：相談→確認→提案→施工


def point_icon(a, b, c):
    """数字の帯の1つ分に合う絵。年（創業・設立）→暦、地名・拠点→ピン、それ以外は項目名から。"""
    if b == "年" or "創業" in c or "設立" in c or "創立" in c:
        return "cal"
    if any(w in a + b + c for w in ("拠点", "エリア", "県", "市", "町", "地域")):
        return "pin"
    return next((ic for words, ic in ICON_HINTS if any(w in a + b + c for w in words)), "check")


# できることの写真：項目名に含まれる語 → 写真（photos/ のファイル名、並べた順に使う）。上から順に見る。
#   写真が [] の行は「まだ写真が無い業種」。下の住宅の行に誤って当たらないよう、ここで止める
#   （業種別の写真 t-* がそろったら、ここに足す）。最後の値は当てない業種（実績→住宅の模型は製造に合わない）
ROOF = ["ai-roof-2", "ai-roof-1", "ai-roof-4", "ai-roof-3"]   # 2026-11-02 素材写真から作った写真に
SVC_PHOTOS = (
    (("見積", "相談", "質問", "Q&A", "問い合わせ", "お問合せ"), ["ai-c-estimate"], ()),
    (("採用", "求人", "リクルート", "人材", "職人紹介", "教育"), ["ai-c-recruit"], ()),
    (("耐震", "補強", "構造"), ["ai-c-seismic"], ()),
    (("外構", "エクステリア", "カーポート", "ブロック", "門まわり", "門扉"), ["ai-c-exterior"], ()),
    (("パソコン", "ネットワーク", "インターネット", "通信", "Wi-Fi", "LAN"), ["ai-c-pc"], ()),
    (("剪定", "伐採", "手入れ"), ["ai-zoen-3", "ai-zoen-2"], ()),
    (("造園", "庭", "植栽", "ガーデ", "緑化"), ["ai-zoen-1", "ai-zoen-2", "ai-zoen-3"], ()),
    (("蓄電", "オール電化", "エコキュート"), ["ai-solar-3"], ()),
    (("テレビ", "家電", "アンテナ", "エアコン"), ["ai-denkiten-1", "ai-denkiten-3"], ()),
    (("水まわり", "水回り", "キッチン", "浴室", "風呂", "トイレ", "洗面", "給湯"), ["ai-house-g4", "ai-house-g3"], ()),
    (("屋根の点検", "屋根点検", "屋根診断", "雨漏り調査", "雨漏り診断"), ["ai-roof-5"], ()),
    (("金属屋根", "ガルバ", "屋根板金", "板金屋根"), ["ai-roof-3", "ai-roof-4"], ()),
    (("屋根", "瓦", "雨漏", "雨もれ", "雨とい", "雨樋", "葺"), ROOF, ()),
    (("太陽光", "発電", "ソーラー"), ["ai-solar-2", "ai-solar-1"], ()),
    (("車検", "鈑金", "自動車", "中古車", "福祉車両", "カーコーティング", "エアロ", "全塗装", "特装車", "お車"), ["ai-car-1", "ai-car-2", "ai-car-3"], ()),
    (("メンテ", "点検", "保守", "保全", "アフター", "定期"), ["ai-c-mainte"], ()),
    (("修理", "修繕", "補修", "お困り", "故障", "水漏れ", "詰まり"), ["ai-c-repair"], ()),
    (("設計", "図面", "プラン", "監理", "調査", "診断", "測量", "デザイン"), ["ai-c-design"], ()),
    (("お客様の声", "実績", "事例", "引渡", "引き渡し"), ["ai-c-handover"], ("seizo",)),
    (("外壁", "塗り壁", "左官"), ["ai-house-g7"], ()),
    (("家具", "木工", "造作", "建具", "什器", "インテリア"), ["ai-mokko-2", "ai-mokko-1", "ai-mokko-3"], ()),
    (("製材", "木材", "木型", "無垢", "県産材"), ["ai-mokko-3", "ai-mokko-1"], ()),
    (("制御盤", "計装", "盤"), ["ai-denki-1", "ai-denki-2"], ()),
    (("照明", "LED"), ["ai-denki-2", "ai-denki-1"], ()),
    (("電気", "電設", "弱電", "配線", "受変電", "電柱", "架線"), ["ai-denki-3", "ai-denki-1", "ai-denki-2"], ()),
    (("空調", "冷凍", "冷蔵", "ダクト", "換気", "冷暖房"), ["ai-setsubi-3", "ai-setsubi-1"], ()),
    (("給排水", "配管", "衛生", "ガス", "上下水道", "消防", "設備", "井戸"), ["ai-setsubi-2", "ai-setsubi-3"], ()),
    (("舗装", "道路", "区画線", "防護柵"), ["ai-doboku-1", "ai-doboku-2"], ()),
    (("造成", "解体", "重機", "土工", "整地", "土砂"), ["ai-doboku-2", "ai-doboku-1"], ()),
    (("土木", "地盤", "コンクリ", "生コン", "杭", "橋", "カルバート", "のり面"), ["ai-doboku-3", "ai-doboku-1", "ai-doboku-2"], ()),
    (("防水", "シーリング"), ["ai-tosou-3", "ai-tosou-2"], ()),
    (("塗装", "塗り替え", "塗替"), ["ai-tosou-1", "ai-tosou-2", "ai-tosou-3"], ()),
    (("板金", "車"), [], ()),
    (("加工", "溶接", "組立", "試作", "部品", "機械", "製作", "製造", "製缶", "金型", "切削", "旋盤"), ["ai-seizo-2", "ai-seizo-1", "ai-seizo-3"], ()),
    (("リフォーム", "リノベ", "改修", "内装", "改装", "増改築"), ["ai-house-g6", "ai-house-g2", "ai-house-g5"], ()),
    (("不動産", "土地", "売買", "賃貸", "物件", "仲介", "買取", "空き家", "空家"), ["ai-fudosan-1", "ai-fudosan-2", "ai-house-h2", "ai-house-h1"], ()),
    (("大工", "木の家", "伝統"), ["ai-house-h5"], ()),
    (("新築", "注文住宅", "住宅", "家", "分譲", "建築", "木造"), ["ai-house-h1", "ai-house-h3", "ai-house-h4", "ai-house-g2"], ()),
)


def auto_svc_photos(d):
    """できることの写真を項目名から選ぶ（photos.svc を書いていない先）。
    同じページで同じ写真を2回使わない。合う写真が無い項目は、その会社の写真
    （切り替え→実績→トップ）を1回ずつ使い回す。写真が付くのが半分未満なら None（絵のカードのまま）。"""
    photos = d.get("photos") or {}
    hero = photos.get("hero")
    # v3 では「これまでの仕事」の段を出さないので、その写真も使ってよい
    spare = [p for p in (photos.get("slides") or []) + (photos.get("gallery") or []) + [hero] if p]
    used = {(hero or "").partition("@")[0]}   # トップと同じ写真をカードに重ねない
    out = []
    # 先に項目名に合う写真を当て、残った項目にだけ会社の写真を回す
    #   （順に当てると、会社の写真が先に取られて「不動産」に鉋の写真が当たった）
    for t, _ in d["services"]:
        pool = next((ps for ws, ps, skip in SVC_PHOTOS
                     if any(w in t for w in ws) and d.get("industry") not in skip), [])
        pid = next((p for p in pool if p not in used), None)
        if pid:
            used.add(pid)
        out.append(pid)
    for i, pid in enumerate(out):
        if pid is None:   # 合う写真が無い項目：切り替え・実績の写真、最後にトップの写真を1回ずつ
            pid = next((p for p in spare if p not in out and (p == hero or p.partition("@")[0] not in used)), None)
            if pid:
                used.add(pid.partition("@")[0])
                out[i] = pid
    return out if sum(1 for p in out if p) * 2 >= len(out) else None


def about_photo(d):
    """会社紹介の外観写真を業種で選ぶ。町の電器店は自前の店先の写真があるので、それを使う。"""
    words = d["name"] + "".join(t for t, _ in d["services"])
    if any(w in words for w in ("電器", "電機商会", "家電")):
        return None
    if d.get("industry") == "seizo":
        return "ai-o-factory"
    if any(w in words for w in ("土木", "舗装", "造成", "解体", "造園", "庭", "石材", "生コン", "砕石", "資材")):
        return "ai-o-yard"
    return "ai-o-office"


def logo_name(name):
    """ヘッダーの社名。会社の種類と呼び名をそれぞれひとかたまりにして、折り返すなら境目で折る。
    「株式会社岐阜ソイルコンサルタ／ント」と1文字だけ落ちたため（2026-11-05）。"""
    m = re.match(r"^(株式会社|有限会社|合同会社|合資会社)(.+)$", name) or re.match(r"^(.+?)(株式会社|有限会社|合同会社|合資会社)$", name)
    if not m:
        return e(name)
    return "".join(f'<span class="lw">{e(x)}</span>' for x in m.groups())


def short_name(name):
    """会社の種類（株式会社など）を除いた呼び名。見本の帯の「〇〇さま」に使う。"""
    return re.sub(r"(株式会社|有限会社|合同会社|合資会社|協同組合|医療法人|一般社団法人|社会福祉法人)", "", name).strip() or name


def auto_about(d, photos):
    """会社紹介の段を事実だけで組む（about を書いていない先）。写真は業種に合う外観のイメージ。
    町の電器店などはトップの2枚目→1枚目の順で使い回し、写真が1枚も無ければ出さない。"""
    pid = (photos.get("about") or about_photo(d)
           or (photos.get("slides") or [None])[0] or photos.get("hero"))
    if not pid:
        return None
    short = re.sub(r"(株式会社|有限会社|合同会社|合資会社|協同組合|医療法人|一般社団法人|社会福祉法人)", "", d["name"]).strip()
    m = re.search(r"(?:都|道|府|県)?([^都道府県]{1,6}?(?:市|郡[^町村]{1,4}?[町村]|区))", d.get("addr", ""))
    city = m.group(1) if m else ""
    p1 = (f'{d["founded"]}年の創業。' if d.get("founded") else "") + (f'{d["addr"]}にあります。' if d.get("addr") else "")
    names = [t for t, _ in d["services"][:3]]
    p2 = "「" + "」「".join(names) + "」などを承っています。"
    return {"photo": pid, "cap": "イメージ写真", "h": (f"{city}の、{short}。" if city else f"{short}について"),
            "p": [x for x in (p1, p2) if x], "btn": "会社概要"}


def icon_svg(title, key=None):
    key = key or next((ic for words, ic in ICON_HINTS if any(w in title for w in words)), "doc")
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[key]}</svg>')


V2_CSS = """
/* ---- 試作 v2 ---- */
body{font-size:15.5px}
.sechead .en{font-size:11.5px;letter-spacing:.32em;font-weight:700}
.sechead h2{font-size:clamp(24px,5.8vw,34px);letter-spacing:.08em}
.sechead h2::after{content:"";display:block;width:36px;height:2px;background:var(--accent);margin:16px auto 0}
/* できること：線の絵と番号。白い箱の繰り返しに見えないよう、絵の丸と大きな番号で強弱を付ける */
.card{padding:30px 26px 28px;border-radius:14px;transition:transform .25s,box-shadow .25s,border-color .25s}
.card .ic{display:grid;place-items:center;width:54px;height:54px;border-radius:50%%;
  background:rgba(%(acc_rgb)s,.1);color:var(--accent);margin-bottom:16px}
.card .ic svg{width:28px;height:28px}
.card .no{position:absolute;right:20px;top:14px;font-family:var(--serif);font-size:44px;line-height:1;
  color:rgba(%(acc_rgb)s,.12);letter-spacing:.02em}
.card h3{font-size:17.5px}
.card p{font-size:14px;line-height:1.85}
@media(hover:hover){.card:hover{transform:translateY(-3px);border-color:rgba(%(acc_rgb)s,.45);
  box-shadow:0 14px 30px rgba(30,40,35,.08)}}
/* 大切にしていること：写真と文字を左右に。互い違いに並べる */
.feat{background:var(--paper)}
.frows{display:grid;gap:56px}
.frow{display:grid;gap:22px;align-items:center}
.fph{position:relative;aspect-ratio:4/3;border-radius:14px;background-size:cover;background-position:center;
  box-shadow:0 18px 40px rgba(30,40,35,.14)}
.fph::before{content:"";position:absolute;inset:auto -12px -12px auto;width:46%%;height:46%%;
  border-radius:14px;background:rgba(%(acc_rgb)s,.14);z-index:-1}
.fph .cap{position:absolute;left:12px;bottom:12px;background:rgba(20,18,14,.72);color:#fff;
  border-radius:6px;padding:5px 10px;font-size:11px;letter-spacing:.06em}
.ftx .no{display:flex;align-items:center;gap:12px;font-family:var(--serif);font-size:15px;
  color:var(--accent);letter-spacing:.12em;margin-bottom:10px}
.ftx .no::after{content:"";width:44px;height:1px;background:var(--accent)}
.ftx h3{font-family:var(--serif);font-weight:500;font-size:clamp(22px,5.6vw,30px);line-height:1.55;
  letter-spacing:.06em;margin:0 0 14px}
.ftx p{margin:0;color:var(--muted);font-size:15px;line-height:2}
/* 流れ：番号を大きく、つなぎの線を引く */
.step{border-radius:14px;padding:24px 22px 22px 70px}
.step::before{font-size:24px;top:20px;left:20px}
/* 会社概要：地図の灰色の枠の代わりに、表だけを白い面に */
#company table.info{background:var(--paper);border-radius:14px;overflow:hidden;
  box-shadow:0 10px 30px rgba(30,40,35,.06)}
section.alt #company table.info,section.alt table.info{background:var(--ground)}
#company table.info th,#company table.info td{padding:18px 22px}
@media(min-width:900px){
  .frows{gap:96px}
  .frow{grid-template-columns:1.12fr 1fr;gap:64px}
  .frow:nth-child(even) .fph{order:2}
  .frow:nth-child(even) .fph::before{inset:auto auto -12px -12px}
  .ftx{max-width:30em}
  .step:not(:last-child)::after{content:"";position:absolute;top:50%%;right:-12px;width:12px;height:1px;background:var(--accent)}
}
"""


# =====================================================================
# 試作（v3・2026-11-02）：松本さんが持ってきた改善後の画像（山中電器）に寄せる。
#   build.py --v3 <キー> のときだけ使う（今の見本は変えない）。出力は <キー>-v3/
#   ・トップの下：数字の帯 → 線の絵＋見出し＋一言（points）
#   ・できること：写真付きのカード（photos.svc）
#   ・会社紹介：外観の写真と紹介文を左右に（about）
#   ・流れ：丸い絵を線でつなぐ／会社概要：表と地図の枠を左右に
# =====================================================================
V3_CSS = """
/* ---- 試作 v3 ---- */
.hero .stats.pts{grid-template-columns:1fr;gap:0;background:var(--paper);border:1px solid var(--line);
  border-radius:12px;padding:6px 18px;box-shadow:0 10px 30px rgba(30,40,35,.06)}
.hero .stats.pts div{display:flex;align-items:center;gap:16px;text-align:left;background:none;border:0;
  border-radius:0;padding:14px 0;box-shadow:none}
.hero .stats.pts div+div{border-top:1px solid var(--line)}
.pts .pi{flex:none;display:grid;place-items:center;width:52px;height:52px;color:var(--accent)}
.pts .pi svg{width:40px;height:40px}
.pts .pt b{display:block;font-family:var(--serif);font-size:18px;color:var(--ink);letter-spacing:.06em;margin:0}
.pts .pt b i{font-style:normal;font-size:12.5px;margin-left:3px;letter-spacing:.04em}
.pts .pt small{display:block;margin-top:4px;font-size:12.5px;color:var(--muted);line-height:1.7;letter-spacing:.02em}
/* 写真付きのカード */
.cards{display:grid;grid-template-columns:1fr;gap:18px}
.card.pc{padding:0;border-radius:10px;overflow:hidden;background:var(--paper);display:flex;flex-direction:column;
  box-shadow:0 6px 20px rgba(30,40,35,.06)}
.card.pc .cph{aspect-ratio:16/9;background:repeating-linear-gradient(135deg,#eef0ec 0 10px,#e6e9e3 10px 20px);
  display:grid;place-items:center;background-size:cover;background-position:center}
.card.pc .cph span{font-size:12px;color:#7a7f78;letter-spacing:.08em}
.card.pc .cph.ci{background:rgba(%(acc_rgb)s,.08);color:var(--accent)}
.card.pc .cph.ci svg{width:52px;height:52px;opacity:.85}
.card.pc .cb{position:relative;padding:18px 40px 20px 20px}
.card.pc .cb::after{content:"";position:absolute;right:20px;top:50%%;width:8px;height:8px;
  border-top:2px solid var(--accent);border-right:2px solid var(--accent);transform:translateY(-50%%) rotate(45deg)}
.card.pc h3{font-size:17px;margin:0 0 6px}
.card.pc p{font-size:13px;line-height:1.75}
/* 会社紹介 */
.abrow{display:grid;gap:26px;align-items:center}
.abph{position:relative;aspect-ratio:16/10;border-radius:6px;background:repeating-linear-gradient(135deg,#eef0ec 0 10px,#e6e9e3 10px 20px);
  background-size:cover;background-position:center;display:grid;place-items:center;text-align:center;
  font-size:12px;color:#7a7f78;box-shadow:0 14px 34px rgba(30,40,35,.12)}
.abph b{display:block;font-family:var(--serif);font-size:14px;color:#575a51}
.abph .cap{position:absolute;right:10px;bottom:10px;background:rgba(255,255,255,.92);color:#333;
  border-radius:4px;padding:4px 10px;font-size:11px;letter-spacing:.06em}
.abtx .en{display:block;font-size:11.5px;letter-spacing:.3em;color:var(--muted);font-weight:700;margin-bottom:10px}
.abtx h2{font-size:clamp(23px,5.6vw,30px);line-height:1.5;margin:0 0 16px}
.abtx p{margin:0 0 12px;color:var(--muted);font-size:14.5px;line-height:2}
.abtx .btn{margin-top:10px}
/* 流れ：丸い絵を線でつなぐ */
.flow{grid-template-columns:repeat(2,1fr);gap:26px 12px;counter-reset:none}
.flow .step{background:none!important;border:0;padding:0;text-align:center;position:relative;box-shadow:none}
.flow .step::before{display:none}
.step .si{display:grid;place-items:center;width:64px;height:64px;margin:0 auto 10px;border-radius:50%%;
  border:1.5px solid var(--accent);color:var(--accent);background:var(--paper)}
.step .si svg{width:28px;height:28px}
.step .sn{position:absolute;top:0;left:calc(50%% + 36px);font-family:var(--serif);font-size:14px;color:var(--accent);font-weight:700}
.step h3{font-size:16px;margin:0 0 4px}
.step p{font-size:12.5px}
/* 会社概要と地図 */
.cgrid{display:grid;gap:22px;grid-template-columns:minmax(0,1fr)}
.cgrid table.info{table-layout:fixed}
.cgrid table.info th{width:7.5em}
.cgrid table.info td{overflow-wrap:anywhere}
.cgrid table.info{background:var(--paper);border-radius:8px}
.cgrid .mapbox{margin:0;min-height:220px;aspect-ratio:auto;padding:0 16px}
.contact .big{font-family:var(--sans);font-weight:800;font-size:clamp(34px,10vw,52px);letter-spacing:.02em}
@media(min-width:900px){
  .hero .stats.pts{grid-template-columns:repeat(3,1fr);padding:8px 10px}
  .hero .stats.pts div{padding:14px 22px;justify-content:center}
  .hero .stats.pts div+div{border-top:0;border-left:1px solid var(--line)}
  .cards{grid-template-columns:repeat(3,1fr);gap:22px}
  .abrow{grid-template-columns:1.15fr 1fr;gap:56px}
  .flow{grid-template-columns:repeat(4,1fr);gap:0}
  .flow .step:not(:last-child)::after{content:"";position:absolute;top:32px;left:calc(50%% + 48px);
    right:calc(-50%% + 48px);width:auto;height:1.5px;background:var(--accent);opacity:.7}
  .cgrid{grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);align-items:stretch}
}
/* PCのトップの見出しも横書き（松本さんの指示 2026-11-02。縦書きは読みにくい） */
@media(min-width:900px){
  .hero .vt,.hero.full.fv .vt{writing-mode:horizontal-tb;max-height:none;margin-left:0;white-space:normal}
  .hero h1.vt{line-height:1.45;letter-spacing:.06em;font-size:calc(clamp(34px,3.5vw,50px) * var(--h1k,1) / 1.1)}
  .hero h1.vt em{white-space:nowrap}
  .hero .textcol,.hero.full .textcol{flex-direction:column;gap:18px;justify-content:flex-start}
  .hero h1.vt{line-height:1.38}
  /* 文字の塊は写真の高さの真ん中より少し上に置く（上から 64px 固定だと、縦に大きい画面で
     下に 300px 近く空いて文字が浮いて見えた 2026-11-02）。下端に重なる数字の帯の分も下を多めにあける */
  .hero.full .wrap.inner{display:flex;flex-direction:column;justify-content:center;align-items:stretch}
  .hero.full .inner .side,.hero.full.fv .inner .side{padding:48px 20px 136px}
  .hero .textcol h1,.hero.full .textcol h1{order:-1}
  .hero .side{align-items:flex-start}
  .hero .meta{max-width:34em}
}
/* ---- 動き（v3）：出てくる動きは MOTION_CSS（.anim/.on）。ここでは見出しの線と流れの線を伸ばすだけ ---- */
.anim .sechead h2::after{transform:scaleX(0);transition:transform .7s cubic-bezier(.6,0,.2,1) .3s}
.anim .sechead.on h2::after{transform:none}
@media(min-width:900px){
  .anim .flow .step:not(:last-child)::after{transform:scaleX(0);transform-origin:left;transition:transform .6s ease .45s}
  .anim .flow .step.on:not(:last-child)::after{transform:none}
}
.card.pc .cph{transition:transform .8s cubic-bezier(.2,.7,.2,1)}
/* 指を乗せたとき：カードが浮いて、写真が少し寄る */
.card.pc{transition:transform .3s,box-shadow .3s}
@media(hover:hover){
  .card.pc:hover{transform:translateY(-4px);box-shadow:0 16px 34px rgba(30,40,35,.12)}
  .card.pc:hover .cph{transform:scale(1.06)}
}
@media(prefers-reduced-motion:reduce){
  .anim .sechead h2::after,.anim .flow .step::after{transform:none!important;transition:none}
}
"""
