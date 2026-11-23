#!/usr/bin/env python3
"""相手の今のサイトと見本を、スマホの最初の画面で撮って並べるための画像を作る（2026-11-23 試作）。

    python3 nowshot.py <出力先フォルダ> <キー> <今のサイトのURL>

<出力先フォルダ>/now-sp.jpg … 今のサイト（スマホ 390×844 で開いた最初の画面）
<出力先フォルダ>/fv-sp.jpg  … 見本（同じ大きさ。<出力先フォルダ>/index.html を撮る）

★今のサイトはスマホとして開く（mobile=True）。スマホ用の設定が無いサイトは、実際のスマホと同じく縮んで写る。
★撮れなかったら画像を作らない。見本の側は画像が無ければ並べる枠を出さない（build.py の compare_html）。
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

sys.path.insert(0, os.path.expanduser("~/.claude/skills/hp-sample/scripts"))
import shoot as sh   # noqa: E402 ― Chrome の場所と開発者用の接続（WS）を借りる

W, H, OUT_W = 390, 844, 520
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")


def snap(ws, url, out, wait):
    ws.call("Page.navigate", url=url)
    ws.wait_event("Page.loadEventFired", 30)
    time.sleep(wait)
    ws.call("Runtime.evaluate", expression="document.querySelectorAll('.ewcbar').forEach(e=>e.style.display='none')")
    time.sleep(0.3)
    png = out + ".png"
    with open(png, "wb") as fh:
        fh.write(base64.b64decode(ws.call("Page.captureScreenshot", format="png")["data"]))
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", "-Z", str(OUT_W * H // W), png,
                    "--out", out], check=True, capture_output=True)
    os.remove(png)


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    dest, key, now_url = sys.argv[1:]
    port = random.randint(20000, 40000)
    prof = tempfile.mkdtemp(prefix="chrome-")
    p = subprocess.Popen([sh.CHROME, "--headless=new", "--hide-scrollbars", f"--remote-debugging-port={port}",
                          f"--user-data-dir={prof}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        ws.call("Network.setUserAgentOverride", userAgent=UA)
        ws.call("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=2, mobile=True)
        try:
            snap(ws, now_url, os.path.join(dest, "now-sp.jpg"), 4)
            print(f"{key} 今のサイト：撮った")
        except Exception as e:  # noqa: BLE001
            print(f"{key} 今のサイト：撮れなかった（{type(e).__name__}）")
        snap(ws, "file://" + os.path.abspath(os.path.join(dest, "index.html")), os.path.join(dest, "fv-sp.jpg"), 3.5)
        print(f"{key} 見本：撮った")
    finally:
        p.kill()
        shutil.rmtree(prof, ignore_errors=True)


if __name__ == "__main__":
    main()
