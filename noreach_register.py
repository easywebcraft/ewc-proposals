#!/usr/bin/env python3
"""サイトに「営業お断り」の書き込みがあった先を、本番のCRMで「送らない」にする（2026-11-19）。

    python3 noreach_register.py <CRMの番号> [...]            # 変える予定を表示するだけ（何も変えない）
    python3 noreach_register.py <CRMの番号> [...] --apply    # 本番に書き込む（★松本さんの了解を取ってから）

見本作りでサイトを読んだときに「勧誘などのメールは受け付けておりません」などのお断りを見つけた先に使う。
番号は pick.tsv の prospect_id。

★本番のDBは CRM の利用者（ewc）として書く（register.py と同じ。root で書くと CRM がDBに書けなくなる）。
★書く前に本番で /opt/backup/backup-ewc.sh を流してDBの控えを取る。控えが取れなければ書かない。
★変えるのは reach（送り方）だけ。表示したときと送り方が変わっていた先（その間に人が画面で直した）は飛ばす。
"""
import json
import subprocess
import sys

REMOTE = "xserver-crm"

READ = r'''
import json, sqlite3, sys
ids = json.loads(sys.stdin.read())
c = sqlite3.connect("file:/opt/ewc-crm/crm.db?mode=ro", uri=True)
out = {}
for i in ids:
    r = c.execute("SELECT id, name, status, IFNULL(reach,'') FROM prospects WHERE id=?", (i,)).fetchone()
    out[str(i)] = r
print(json.dumps(out, ensure_ascii=False))
'''

APPLY = r'''
import json, sqlite3, sys
plan = json.loads(sys.stdin.read())
c = sqlite3.connect("/opt/ewc-crm/crm.db")
done = []
for pid, before in plan:
    cur = c.execute("UPDATE prospects SET reach='送らない' WHERE id=? AND IFNULL(reach,'')=?", (pid, before))
    if cur.rowcount:
        done.append(pid)
c.commit()
print(json.dumps(done))
'''


def remote_py(script, payload, write=False):
    # ssh の標準入力にスクリプトとデータの両方は渡せないので、データはスクリプトに埋め込む（permit_register.py と同じ）
    body = script.replace("json.loads(sys.stdin.read())", "json.loads(%r)" % json.dumps(payload, ensure_ascii=False))
    cmd = "cd /opt/ewc-crm && sudo -u ewc .venv/bin/python -" if write else "cd /opt/ewc-crm && .venv/bin/python -"
    r = subprocess.run(["ssh", REMOTE, cmd], input=body, capture_output=True, text=True, timeout=60)
    if r.returncode:
        sys.exit("本番での処理に失敗:\n" + r.stderr)
    return json.loads(r.stdout)


def main():
    apply = "--apply" in sys.argv
    ids = [int(a) for a in sys.argv[1:] if a.isdigit()]
    if not ids:
        sys.exit(__doc__)
    found = remote_py(READ, ids)
    plan = []
    for i in ids:
        r = found.get(str(i))
        if not r:
            print("  番号が無い（飛ばす）   %d" % i)
            continue
        pid, name, status, reach = r
        if reach == "送らない":
            print("  もう送らない          %d %s" % (pid, name))
            continue
        print("  送らないにする        %d %s（%s・今は %s）" % (pid, name, status, reach or "空"))
        plan.append((pid, reach))
    print("— 変える予定 %d件" % len(plan))
    if not plan or not apply:
        if plan:
            print("（--apply を付けると本番に書き込む）")
        return
    subprocess.run(["ssh", REMOTE, "/opt/backup/backup-ewc.sh before-noreach"], check=True)
    done = remote_py(APPLY, plan, write=True)
    print("本番を送らないにした: %d件（予定 %d件。差は、その間に人が画面で送り方を直した先）" % (len(done), len(plan)))


if __name__ == "__main__":
    main()
