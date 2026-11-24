#!/usr/bin/env python3
"""見本の相手の今のサイトをスマホとして開き、横幅と警告の画面かを測る（2026-11-24）。

    python3 fitcheck.py <キー>...      → キー<TAB>横幅<TAB>開いたURL<TAB>題名（URL は teian.tsv の3列目）

★比較画像を撮ったあとに流す。次の先は nowshot.py の3つの画像を消す：
  ・横幅が420以下（スマホ用のページが出て、普通に読める。所見の「スマホ非対応」も誤りなので外す）
  ・開いたURLが chrome-error://（警告の画面）で、所見に「証明書エラー」が無い
  ・題名が 404・500 など
★測る中身は ~/kmtools/mobilefit.py（採点の道具と同じ物差し）。
"""
import os
import sys

sys.path.insert(0, os.path.expanduser("~/kmtools"))
import mobilefit   # noqa: E402
import nowshot as N   # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    urls = N.load_teian()
    for k in sys.argv[1:]:
        w, final, t = mobilefit.measure(urls[k])
        print(f"{k}\t{'?' if w is None else w}\t{final}\t{t}", flush=True)
