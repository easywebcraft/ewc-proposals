#!/usr/bin/env python3
"""公開した見本のURLを、本番のCRMの営業リスト（prospects.proposal_url）に入れる。

    python3 register.py               # 入れる予定を表示するだけ（何も変えない）
    python3 register.py --apply       # 本番に書き込む（★松本さんの了解を取ってから）

pick.py が書いた pick.tsv の先のうち、次をすべて満たすものだけを入れる:
  - sites.json にキーがあり、<キー>/index.html ができている
  - 公開URL（https://easywebcraft.github.io/ewc-proposals/<キー>/）が開ける（GitHub Pages に反映済み）
  - 本番で今も「未着手・見本なし」のまま（その間に人が触っていたら飛ばす）

★本番のDBは CRM の利用者（ewc）として書く。root で書くと、SQLite の作業ファイルが root の持ち物になり、
  CRM がDBに書けなくなる。
★書く前に本番で /opt/backup/backup.sh を流してDBの控えを取る。
★入れるのは proposal_url だけ。状態・送り方・メモなど人が使う欄には触らない
  （営業リストの作り方.md「項目ごとに持ち主が分かれている」）。
"""
import json
import os
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REMOTE = "xserver-crm"
BASE = "https://easywebcraft.github.io/ewc-proposals/%s/"

APPLY = r'''
import json, sqlite3, sys
plan = json.loads(sys.stdin.read())
c = sqlite3.connect("/opt/ewc-crm/crm.db")
done = []
for pid, url in plan:
    cur = c.execute("UPDATE prospects SET proposal_url=? WHERE id=? AND status='未着手' "
                    "AND IFNULL(proposal_url,'')=''", (url, pid))
    if cur.rowcount:
        done.append(pid)
c.commit()
print(json.dumps(done))
'''


def live(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=15) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    apply = "--apply" in sys.argv
    sites = json.load(open(os.path.join(HERE, "sites.json"), encoding="utf-8"))
    path = os.path.join(HERE, "pick.tsv")
    if not os.path.exists(path):
        sys.exit("pick.tsv が無い。先に python3 pick.py ... --out nav_todo.tsv を流す")
    rows = [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8")][1:]
    plan = []
    for key, pid, name, *_ in rows:
        url = BASE % key
        if key not in sites or not os.path.exists(os.path.join(HERE, key, "index.html")):
            print("  まだ作っていない  %-20s %s" % (key, name))
            continue
        if not live(url):
            print("  公開待ち          %-20s %s" % (key, name))
            continue
        print("  入れる            %-20s %s → %s" % (key, name, url))
        plan.append((int(pid), url))
    print("— 入れる予定 %d件" % len(plan))
    if not plan or not apply:
        if plan:
            print("（--apply を付けると本番に書き込む）")
        return
    subprocess.run(["ssh", REMOTE, "/opt/backup/backup.sh"], check=False)
    # ssh の標準入力にスクリプトと計画の両方は渡せないので、計画はスクリプトに埋め込む
    script = APPLY.replace("json.loads(sys.stdin.read())", "json.loads(%r)" % json.dumps(plan))
    r = subprocess.run(["ssh", REMOTE, "cd /opt/ewc-crm && sudo -u ewc .venv/bin/python -"],
                       input=script, capture_output=True, text=True, timeout=60)
    if r.returncode:
        sys.exit("書き込みに失敗:\n" + r.stderr)
    done = json.loads(r.stdout)
    print("本番に入れた: %d件（予定 %d件。差は、その間に人が触って条件から外れた先）" % (len(done), len(plan)))


if __name__ == "__main__":
    main()
