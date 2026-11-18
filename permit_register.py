#!/usr/bin/env python3
"""見本で照合した所見（建設業許可の表記・証明書の警告）を、本番のCRMの所見（prospects.findings）の末尾に足す。

    python3 permit_register.py               # 足す予定を表示するだけ（何も変えない）
    python3 permit_register.py --apply       # 本番に書き込む（★松本さんの了解を取ってから）

足す文字は sites.json の所見（intro.findings）にある次のもの（TOKENS）。
  - 「許可表記が古い(般-19→般-4・令和4年更新)」：国土交通省の建設業者検索で照合した先（2026-11-19）
  - 「証明書エラー(別の名前)」など：実際の Chrome で開いて「プライバシー エラー」になった先（2026-11-19）
営業メールは所見のこれらの言葉を見て、挙げる2つの上のほうに出す（ewc-crm/salesmail.py）。

本番の先は、見本のURL（prospects.proposal_url）で見分ける。次の先は飛ばす:
  - 本番に見本のURLが入った先が無い（未登録）
  - 状態が「見送り」（営業しないと決めた先）
  - 足す言葉がもう全部ある（二重に足さない）
  - 表示したときと書き込むときで所見が変わっている（その間に人が画面で直した）

★本番のDBは CRM の利用者（ewc）として書く（register.py と同じ。root で書くと CRM がDBに書けなくなる）。
★書く前に本番で /opt/backup/backup-ewc.sh を流してDBの控えを取る。控えが取れなければ書かない。
★書くのは findings だけ。状態・送り方・メモなど人が使う欄には触らない。
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REMOTE = "xserver-crm"
BASE = "https://easywebcraft.github.io/ewc-proposals/%s/"
TOKENS = [re.compile(r"証明書エラー\([^)]*\)"), re.compile(r"許可表記が古い\([^)]*\)")]

# 本番で、見本のURLから先の id・社名・状態・今の所見を読む（読むだけ。DBは読み取り専用で開く）
READ = r'''
import json, sqlite3, sys
urls = json.loads(sys.stdin.read())
c = sqlite3.connect("file:/opt/ewc-crm/crm.db?mode=ro", uri=True)
out = {}
for u in urls:
    r = c.execute("SELECT id, name, status, IFNULL(findings,'') FROM prospects WHERE proposal_url=?", (u,)).fetchall()
    out[u] = r
print(json.dumps(out, ensure_ascii=False))
'''

# 本番に書く。表示したときの所見のままの先だけ書き換える
APPLY = r'''
import json, sqlite3, sys
plan = json.loads(sys.stdin.read())
c = sqlite3.connect("/opt/ewc-crm/crm.db")
done = []
for pid, before, after in plan:
    cur = c.execute("UPDATE prospects SET findings=? WHERE id=? AND IFNULL(findings,'')=?", (after, pid, before))
    if cur.rowcount:
        done.append(pid)
c.commit()
print(json.dumps(done))
'''


def remote_py(script, payload, write=False):
    # ssh の標準入力にスクリプトとデータの両方は渡せないので、データはスクリプトに埋め込む
    body = script.replace("json.loads(sys.stdin.read())", "json.loads(%r)" % json.dumps(payload, ensure_ascii=False))
    cmd = "cd /opt/ewc-crm && sudo -u ewc .venv/bin/python -" if write else "cd /opt/ewc-crm && .venv/bin/python -"
    r = subprocess.run(["ssh", REMOTE, cmd], input=body, capture_output=True, text=True, timeout=60)
    if r.returncode:
        sys.exit("本番での処理に失敗:\n" + r.stderr)
    return json.loads(r.stdout)


def main():
    apply = "--apply" in sys.argv
    sites = json.load(open(os.path.join(HERE, "sites.json"), encoding="utf-8"))
    want = {}
    for key, d in sites.items():
        f = (d.get("intro") or {}).get("findings", "")
        toks = [m.group(0) for t in TOKENS for m in [t.search(f)] if m]
        if toks:
            want[BASE % key] = (key, d["name"], toks)
    if not want:
        sys.exit("sites.json に足す所見の入った先が無い")
    found = remote_py(READ, list(want))
    plan = []
    for url, (key, name, toks) in want.items():
        rows = found.get(url) or []
        if not rows:
            print("  未登録（飛ばす）      %-18s %s" % (key, name))
            continue
        if len(rows) > 1:
            print("  同じ見本の先が%d件（飛ばす）%-12s %s" % (len(rows), key, name))
            continue
        pid, pname, status, before = rows[0]
        if status == "見送り":   # 営業しないと決めた先には足さない（2026-11-19 松本さん）
            print("  見送り（飛ばす）      %-18s %s" % (key, pname))
            continue
        add = [t for t in toks if t.split("(")[0] not in before]
        if not add:
            print("  もう入っている        %-18s %s" % (key, pname))
            continue
        after = " / ".join([before.rstrip()] + add) if before.strip() else " / ".join(add)
        print("  足す                  %-18s %s（%s）\n      足す文字：%s" % (key, pname, status, " / ".join(add)))
        plan.append((pid, before, after))
    print("— 足す予定 %d件" % len(plan))
    if not plan or not apply:
        if plan:
            print("（--apply を付けると本番に書き込む）")
        return
    subprocess.run(["ssh", REMOTE, "/opt/backup/backup-ewc.sh before-permit"], check=True)
    done = remote_py(APPLY, plan, write=True)
    print("本番に足した: %d件（予定 %d件。差は、その間に人が画面で所見を直した先）" % (len(done), len(plan)))


if __name__ == "__main__":
    main()
