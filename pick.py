#!/usr/bin/env python3
"""本番のCRMから「見本（トップ案）を作る候補」を選び、作業用のTSVを書き出す。読むだけで、CRMは変えない。

    python3 pick.py                          # 20点以上の候補を全部（一覧を表示）
    python3 pick.py --min 40 --cat 住宅・建材  # 40点以上・業種で絞る
    python3 pick.py --min 40 --cat 住宅・建材 --out nav_todo.tsv   # 作業用TSVに書き出す

候補の条件（CRMの「まとめて予約」に載る条件の裏返し＝見本だけが足りない先）:
  未着手・メール可・アドレスあり・見本なし・まだ1通も送っていない（テスト送信は数えない）
  ＋同じアドレスに送った先・送付済／送らない／見本ありの先が別の行に無い

書き出す nav_todo.tsv は「キー / サイトURL / 社名」の3列で、navfind.py・colorfind.py・factfind.py の入力になる。
同じ内容に CRM の番号・点数・業種・地域・メモを足したものを pick.tsv に書く（register.py が使う）。

★キー（公開URLの末尾）は相手のドメインから作る。sites.json に同じキーがあれば -2 を付ける。
★メモに「要確認」がある先（フリーメール・サイトと別ドメインのアドレス）は印を付けて出す。
  送る前に人がアドレスを確かめる先なので、見本を作る順番は後ろにする。
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
REMOTE = "xserver-crm"

QUERY = r'''
import json, sqlite3
c = sqlite3.connect("file:/opt/ewc-crm/crm.db?mode=ro", uri=True)
c.row_factory = sqlite3.Row
rows = c.execute("""
  SELECT p.id, p.name, p.url, p.category, p.area, p.score, p.email, IFNULL(p.memo,'') memo,
         IFNULL(p.list_kind,'営業') list_kind
  FROM prospects p
  WHERE p.status='未着手' AND p.reach='メール可' AND IFNULL(p.email,'')<>''
    AND IFNULL(p.proposal_url,'')='' AND IFNULL(p.url,'')<>''
    AND NOT EXISTS (SELECT 1 FROM prospect_mails m WHERE m.prospect_id=p.id AND m.is_test=0)
    AND NOT EXISTS (SELECT 1 FROM prospect_mails m WHERE m.is_test=0
                    AND lower(trim(m.to_email))=lower(trim(p.email)))
    AND NOT EXISTS (SELECT 1 FROM prospects q WHERE q.id<>p.id
                    AND lower(trim(q.email))=lower(trim(p.email))
                    AND (q.status<>'未着手' OR q.reach='送らない' OR IFNULL(q.proposal_url,'')<>''))
  ORDER BY (p.score IS NULL), p.score DESC, p.id""").fetchall()
print(json.dumps([dict(r) for r in rows], ensure_ascii=False))
'''


def fetch():
    r = subprocess.run(["ssh", REMOTE, "python3", "-"], input=QUERY, capture_output=True, text=True, timeout=60)
    if r.returncode:
        sys.exit("本番のCRMを読めない（ssh xserver-crm）:\n" + r.stderr)
    return json.loads(r.stdout)


def key_of(url, used):
    host = urllib.parse.urlparse(url).netloc.lower().split(":")[0]
    host = re.sub(r"^www\d?\.", "", host)
    parts = host.split(".")
    # 無料ブログ・共用ドメインは、ドメインではなくパスの先頭を使う
    if len(parts) > 2 and parts[-2] in ("livedoor", "fc2", "jimdo", "wixsite", "jp-net", "hi-ho", "ocn", "goo"):
        path = urllib.parse.urlparse(url).path.strip("/").split("/")
        base = (path[0] if path and path[0] else parts[0])
    else:
        base = parts[0]
    base = re.sub(r"[^a-z0-9-]", "-", base).strip("-") or "site"
    k, n = base, 2
    while k in used:
        k, n = "%s-%d" % (base, n), n + 1
    used.add(k)
    return k


def norm_name(n):
    return re.sub(r"(株式会社|有限会社|合資会社|合同会社|㈱|㈲|\s)", "", n or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=20, help="点数の下限（既定20）")
    ap.add_argument("--cat", default="", help="業種（CRMの業種名と完全一致。例：住宅・建材）")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="", help="作業用TSV（キー/URL/社名）の書き出し先")
    a = ap.parse_args()

    sites = json.load(open(os.path.join(HERE, "sites.json"), encoding="utf-8"))
    used = set(sites)
    rows = [r for r in fetch() if (r["score"] or 0) >= a.min and (not a.cat or r["category"] == a.cat)]
    # ★同じ会社が住所違いで2行あることがある（2026-11-05）。同じアドレスは1行だけ、
    #   見本のある社名と同じ先は外す（アドレスが違っても同じ会社のことが多い）
    made = {norm_name(v.get("name", "")) for v in sites.values()} - {""}
    seen, kept, dup = set(), [], []
    for r in rows:
        e = r["email"].strip().lower()
        if e in seen or norm_name(r["name"]) in made:
            dup.append(r)
            continue
        seen.add(e)
        kept.append(r)
    rows = kept
    if a.limit:
        rows = rows[:a.limit]
    for r in rows:
        r["key"] = key_of(r["url"], used)
        r["check"] = "要確認" if "要確認" in r["memo"] else ""

    for r in rows:
        print("%3s点  %-6s %-22s %s  %s  %s" % (r["score"], r["check"] or "", r["key"], r["name"],
                                              r["category"] or "(業種なし)", r["area"] or ""))
    print("— %d件" % len(rows))
    if dup:
        print("（同じアドレス・見本のある社名と同じで外した %d件：%s）" % (len(dup), "、".join(r["name"] for r in dup)))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            for r in rows:
                f.write("%s\t%s\t%s\n" % (r["key"], r["url"], r["name"]))
        with open(os.path.join(HERE, "pick.tsv"), "w", encoding="utf-8") as f:
            f.write("key\tprospect_id\tname\turl\tscore\tcategory\tarea\tcheck\n")
            for r in rows:
                f.write("\t".join(str(r[k] or "") for k in
                                  ("key", "id", "name", "url", "score", "category", "area", "check")) + "\n")
        print("→ %s と pick.tsv に書き出した" % a.out)


if __name__ == "__main__":
    main()
