#!/usr/bin/env python3
"""見本のトップの最初の画面を撮り、<キー>/fv.jpg に置く（営業メールの画像に使う。2026-11-19）。

    python3 fvshot.py <キー> [<キー> ...]   # 指定した見本だけ（見本作りの4のあと）
    python3 fvshot.py --all                 # fv.jpg が無い見本を全部
    python3 fvshot.py --all --force         # 全部撮り直す（見本の見た目を変えたあと）

CRM（ewc-crm app.py の sample_shot）は、画像のある段（A2 など）を送る直前に
https://easywebcraft.github.io/ewc-proposals/<キー>/fv.jpg を取りに来て、段の画像の代わりにメールに入れる。
無ければ段の画像で送るので、撮り忘れても送れなくはならない。

★PC の幅（1280×800）で撮り、下に次の段の白い枠がのぞかないよう上から 625px で切って、幅 1120 の JPEG にする（150KB 前後）。
★画面下の EasyWebCraft の相談の帯（.ewcbar）は隠して撮る。上の「提案用の見本」の帯は残す（相手が本物と取り違えないため）。
★撮る前に、最初の動き（文字が出てくる演出など）が終わるまで待つ。
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

W, H, CUT, OUT_W = 1280, 800, 625, 1120


def keys_to_shoot(args):
    sites = json.load(open(os.path.join(HERE, "sites.json"), encoding="utf-8"))
    force = "--force" in args
    if "--all" in args:
        # 丸信（marushin-kaitai）はお客さまの案件なので営業メールに使わない。いつも外す
        keys = [k for k in sites if k != "marushin-kaitai" and os.path.isfile(os.path.join(HERE, k, "index.html"))]
    else:
        keys = [a for a in args if not a.startswith("--")]
    return [k for k in keys if force or not os.path.isfile(os.path.join(HERE, k, "fv.jpg"))]


def main():
    keys = keys_to_shoot(sys.argv[1:])
    if not keys:
        sys.exit(__doc__ if len(sys.argv) < 2 else "撮る見本がない（fv.jpg はもうある。撮り直すなら --force）")
    port = random.randint(20000, 40000)
    prof = tempfile.mkdtemp(prefix="chrome-")
    tmp = tempfile.mkdtemp(prefix="fvshot-")
    p = subprocess.Popen([sh.CHROME, "--headless=new", "--hide-scrollbars", f"--remote-debugging-port={port}",
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
        ws.call("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=1, mobile=False)
        for i, k in enumerate(keys, 1):
            try:
                ws.call("Page.navigate", url="file://" + os.path.join(HERE, k, "index.html"))
                ws.wait_event("Page.loadEventFired", 30)
                time.sleep(3.5)
                ws.call("Runtime.evaluate", expression="document.querySelectorAll('.ewcbar').forEach(e=>e.style.display='none')")
                time.sleep(0.3)
                png = os.path.join(tmp, k + ".png")
                with open(png, "wb") as fh:
                    fh.write(base64.b64decode(ws.call("Page.captureScreenshot", format="png",
                                                      clip={"x": 0, "y": 0, "width": W, "height": CUT, "scale": 1})["data"]))
                out = os.path.join(HERE, k, "fv.jpg")
                subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", "-Z", str(OUT_W), png,
                                "--out", out], check=True, capture_output=True)
                print("%d/%d %s" % (i, len(keys), k), flush=True)
            except Exception as e:  # noqa: BLE001 ― 1件の失敗で全体を止めない
                ng.append(k)
                print("%d/%d %s 撮れなかった（%s）" % (i, len(keys), k, type(e).__name__), flush=True)
    finally:
        p.kill()
        shutil.rmtree(prof, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)
    if ng:
        print("撮れなかった:", " ".join(ng))


if __name__ == "__main__":
    main()
