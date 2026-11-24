#!/usr/bin/env python3
"""相手の今のサイトと見本を、スマホの最初の画面で撮って並べる画像を作る（2026-11-23）。

    python3 nowshot.py <キー> [<キー> ...]   # teian.tsv に載った見本だけ（URL は teian.tsv の3列目）
    python3 nowshot.py --all                 # teian.tsv の全部で、now-sp.jpg が無いもの
    python3 nowshot.py --all --force         # 全部撮り直す

<キー>/now-sp.jpg … 今のサイト（スマホ 390×844 で開いた最初の画面）
<キー>/fv-sp.jpg  … 見本（同じ大きさ。<キー>/index.html を撮る）
<キー>/cmp.jpg    … 2つを左右に並べ、「今のサイト」「この案」の見出しを付けた1枚（幅1000。営業メールに貼る用）

★見本のページ（build.py の compare_html）は now-sp.jpg と fv-sp.jpg を別々に並べる。cmp.jpg はメール用。
★今のサイトはスマホとして開く（mobile=True）。スマホ用の設定が無いサイトは、実際のスマホと同じく縮んで写る。
★撮れなかったら3つとも作らない（前に撮ったものは消す）。見本の側は画像が無ければ比較の枠を出さない。
★撮ったあとは build.py <キー> で作り直す（比較の枠は画像があるときだけ入るため）。
★撮るのは所見に「スマホ非対応」か「証明書エラー」がある見本だけ（2026-11-23）。それ以外の先は今のサイトもスマホで
  読めることが多く、並べても違いが伝わらない（かえって今のままでよいと思われる）。
★撮った今のサイトは目で見る：アクセスを断る先（Forbidden）・所見に無い警告の画面は、3つの画像を消す。
"""
import base64
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser("~/.claude/skills/hp-sample/scripts"))
import shoot as sh   # noqa: E402 ― Chrome の場所と開発者用の接続（WS）を借りる

W, H, OUT_W, CMP_W = 390, 844, 520, 1000
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")
CMP_HTML = """<!doctype html><meta charset="utf-8"><style>
body{margin:0;background:#fff;font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN",sans-serif;color:#10294f}
.w{width:600px;padding:18px 20px 16px;box-sizing:border-box}
p{margin:0 0 12px;text-align:center;font-size:13px;color:#4a5b75;letter-spacing:.04em}
.g{display:grid;grid-template-columns:1fr 1fr;gap:16px}
figure{margin:0;text-align:center}
img{display:block;width:100%%;border:1px solid #c9d4e3;border-radius:10px}
figcaption{margin-top:8px;font-size:15px;font-weight:700;color:#6b7a90}
.n figcaption{color:#10294f}
</style><div class="w" id="w"><p>%(name)s様　スマートフォンで開いた最初の画面</p><div class="g">
<figure><img src="file://%(now)s"><figcaption>今のサイト</figcaption></figure>
<figure class="n"><img src="file://%(new)s"><figcaption>この案</figcaption></figure></div></div>"""


def load_teian():
    rows = [x.split("\t") for x in open(os.path.join(HERE, "teian.tsv"), encoding="utf-8").read().splitlines()[1:] if x.strip()]
    return {r[0]: r[2] for r in rows}


def to_jpeg(png, out, width):
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", "--resampleWidth", str(width), png,
                    "--out", out], check=True, capture_output=True)
    os.remove(png)


def snap(ws, url, out, wait):
    ws.call("Page.navigate", url=url)
    ws.wait_event("Page.loadEventFired", 30)
    time.sleep(wait)
    ws.call("Runtime.evaluate", expression="document.querySelectorAll('.ewcbar').forEach(e=>e.style.display='none')")
    time.sleep(0.3)
    with open(out + ".png", "wb") as fh:
        fh.write(base64.b64decode(ws.call("Page.captureScreenshot", format="png")["data"]))
    to_jpeg(out + ".png", out, OUT_W)


def compose(ws, key, name, tmp):
    d = os.path.join(HERE, key)
    page = os.path.join(tmp, key + ".html")
    with open(page, "w", encoding="utf-8") as fh:
        fh.write(CMP_HTML % {"name": name, "now": os.path.join(d, "now-sp.jpg"), "new": os.path.join(d, "fv-sp.jpg")})
    ws.call("Emulation.setDeviceMetricsOverride", width=600, height=900, deviceScaleFactor=2, mobile=False)
    ws.call("Page.navigate", url="file://" + page)
    ws.wait_event("Page.loadEventFired", 30)
    time.sleep(0.5)
    r = ws.call("Runtime.evaluate", returnByValue=True,
                expression="var b=document.getElementById('w').getBoundingClientRect();JSON.stringify([b.width,b.height])")
    w, h = json.loads(r["result"]["value"])
    png = os.path.join(d, "cmp.jpg.png")
    with open(png, "wb") as fh:
        fh.write(base64.b64decode(ws.call("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                                          clip={"x": 0, "y": 0, "width": w, "height": h, "scale": 1})["data"]))
    to_jpeg(png, os.path.join(d, "cmp.jpg"), CMP_W)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    urls = load_teian()
    sites = json.load(open(os.path.join(HERE, "sites.json"), encoding="utf-8"))
    def worth(k):
        f = sites[k].get("intro", {}).get("findings", "")
        return "スマホ非対応" in f or "証明書エラー" in f
    if "--all" in args:
        keys = [k for k in urls if worth(k) and ("--force" in args or not os.path.isfile(os.path.join(HERE, k, "now-sp.jpg")))]
    else:
        keys = [a for a in args if not a.startswith("--")]
        missing = [k for k in keys if k not in urls]
        if missing:
            sys.exit("teian.tsv に無いキー：" + " ".join(missing))
        skip = [k for k in keys if not worth(k)]
        if skip:
            print("所見にスマホ非対応・証明書エラーが無いので撮らない：" + " ".join(skip))
        keys = [k for k in keys if worth(k)]
    if "--all" in args:
        # ★応答の無いサイトで Chrome との接続ごと止まった（2026-11-23 夜、117件目のあとで朝まで）。
        #   1件ずつ別に動かし、120秒で Chrome ごと打ち切る
        ng = []
        for i, k in enumerate(keys, 1):
            q = subprocess.Popen([sys.executable, os.path.abspath(__file__), k], stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, start_new_session=True)
            try:
                out = q.communicate(timeout=120)[0]
            except subprocess.TimeoutExpired:
                os.killpg(q.pid, 9)
                q.wait()
                out = "撮れなかった（時間切れ）"
                for f in ("now-sp.jpg", "fv-sp.jpg", "cmp.jpg"):
                    if os.path.isfile(os.path.join(HERE, k, f)):
                        os.remove(os.path.join(HERE, k, f))
            ok = os.path.isfile(os.path.join(HERE, k, "cmp.jpg"))
            ng += [] if ok else [k]
            print(f"{i}/{len(keys)} {k}" + ("" if ok else " " + out.strip().splitlines()[-1]), flush=True)
        if ng:
            print("撮れなかった:", " ".join(ng))
        return
    port = random.randint(20000, 40000)
    prof = tempfile.mkdtemp(prefix="chrome-")
    tmp = tempfile.mkdtemp(prefix="nowshot-")
    # ★http だけのサイトは、Chrome が https に切り替えようとして白い画面のまま止まる（2026-11-23 に45件）。切り替えを止める
    p = subprocess.Popen([sh.CHROME, "--headless=new", "--hide-scrollbars", f"--remote-debugging-port={port}",
                          "--disable-features=HttpsUpgrades,HttpsFirstBalancedModeAutoEnable,HttpsFirstModeV2ForTypicallySecureUsers",
                          f"--user-data-dir={prof}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ng = []
    try:
        for _ in range(100):
            try:
                page = next(t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
                            if t.get("type") == "page")
                break
            except Exception:  # noqa: BLE001
                time.sleep(0.1)
        else:
            sys.exit("Chrome に接続できない")
        ws = sh.WS(page["webSocketDebuggerUrl"])
        ws.call("Page.enable")
        ws.call("Network.enable")
        for i, k in enumerate(keys, 1):
            d = os.path.join(HERE, k)
            try:
                ws.call("Network.setUserAgentOverride", userAgent=UA)
                ws.call("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=2, mobile=True)
                snap(ws, urls[k], os.path.join(d, "now-sp.jpg"), 4)
                snap(ws, "file://" + os.path.join(d, "index.html"), os.path.join(d, "fv-sp.jpg"), 3.5)
                compose(ws, k, sites[k]["name"], tmp)
                print(f"{i}/{len(keys)} {k}", flush=True)
            except Exception as e:  # noqa: BLE001 ― 1件の失敗で全体を止めない
                ng.append(k)
                for f in ("now-sp.jpg", "fv-sp.jpg", "cmp.jpg"):
                    if os.path.isfile(os.path.join(d, f)):
                        os.remove(os.path.join(d, f))
                print(f"{i}/{len(keys)} {k} 撮れなかった（{type(e).__name__}）", flush=True)
    finally:
        p.kill()
        shutil.rmtree(prof, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)
    if ng:
        print("撮れなかった:", " ".join(ng))


if __name__ == "__main__":
    main()
