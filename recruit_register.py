#!/usr/bin/env python3
"""見本の先の採用ページを調べて（~/kmtools/recruitcheck.py）、本番のCRMに入れる。

    python3 recruit_register.py               # まだ調べていない先を調べ、入れる予定を表示（本番は変えない）
    python3 recruit_register.py --apply       # 調べて本番に書き込む
    python3 recruit_register.py キー キー…     # その見本の先だけ（調べ直しにも使う）

営業メールの A7（採用の段）は、この結果で段落と件名を切り替える（ewc-crm/salesmail.py の recruit_values）。
調べていない先には一般の言い方が届くので、見本を CRM に登録したら（register.py のあと）必ず流す（2026-11-24）。

対象は teian.tsv（キー / 日付 / 今のサイトのURL）にあって、本番に見本のURLが入っていて、
採用の調べ（prospects.recruit）がまだ空の先。キーを渡したときは、調べ済みでも調べ直す。
次の先は飛ばす: 未登録・同じ見本の先が2件以上・状態が「見送り」。

★相手のサイトを読みに行く（1社に数ページ・スマホの画面での測定込みで10〜20秒）。
★本番のDBは CRM の利用者（ewc）として書く（register.py と同じ）。書く前に backup-ewc.sh で控えを取る。
★書くのは recruit・recruit_url・recruit_issues・recruit_checked_on だけ。状態・所見・メモには触らない。
"""
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser("~/kmtools"))
import recruitcheck  # noqa: E402

REMOTE = "xserver-crm"
BASE = "https://easywebcraft.github.io/ewc-proposals/%s/"

READ = r'''
import json, sqlite3, sys
urls = json.loads(sys.stdin.read())
c = sqlite3.connect("file:/opt/ewc-crm/crm.db?mode=ro", uri=True)
out = {}
for u in urls:
    out[u] = c.execute("SELECT id, name, status, IFNULL(recruit,'') FROM prospects WHERE proposal_url=?", (u,)).fetchall()
print(json.dumps(out, ensure_ascii=False))
'''

APPLY = r'''
import json, sqlite3, sys
plan = json.loads(sys.stdin.read())
c = sqlite3.connect("/opt/ewc-crm/crm.db")
done = []
for pid, before, recruit, url, issues, day in plan:
    cur = c.execute("UPDATE prospects SET recruit=?, recruit_url=?, recruit_issues=?, recruit_checked_on=? "
                    "WHERE id=? AND IFNULL(recruit,'')=?", (recruit, url, issues, day, pid, before))
    if cur.rowcount:
        done.append(pid)
c.commit()
print(json.dumps(done))
'''


def remote_py(script, payload, write=False):
    # ssh の標準入力にスクリプトとデータの両方は渡せないので、データはスクリプトに埋め込む（permit_register.py と同じ）
    body = script.replace("json.loads(sys.stdin.read())", "json.loads(%r)" % json.dumps(payload, ensure_ascii=False))
    cmd = "cd /opt/ewc-crm && sudo -u ewc .venv/bin/python -" if write else "cd /opt/ewc-crm && .venv/bin/python -"
    r = subprocess.run(["ssh", REMOTE, cmd], input=body, capture_output=True, text=True, timeout=120)
    if r.returncode:
        sys.exit("本番での処理に失敗:\n" + r.stderr)
    return json.loads(r.stdout)


def teian():
    out = {}
    for line in open(os.path.join(HERE, "teian.tsv"), encoding="utf-8"):
        c = line.rstrip("\n").split("\t") + ["", "", ""]
        if c[0] and c[0] != "キー" and c[2].strip():
            out[c[0]] = c[2].strip()
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    sites = teian()
    keys = args or list(sites)
    miss = [k for k in keys if k not in sites]
    if miss:
        sys.exit("teian.tsv に無いキー: " + " ".join(miss))
    found = remote_py(READ, [BASE % k for k in keys])
    targets = []
    for k in keys:
        rows = found.get(BASE % k) or []
        if not rows:
            if args:
                print("  未登録（飛ばす）      %s" % k)
            continue
        if len(rows) > 1:
            print("  同じ見本の先が%d件（飛ばす）%s" % (len(rows), k))
            continue
        pid, name, status, before = rows[0]
        if status == "見送り":
            print("  見送り（飛ばす）      %-18s %s" % (k, name))
            continue
        if before and not args:
            continue
        targets.append((k, pid, name, before))
    if not targets:
        print("— 調べる先はありません（見本の先はすべて調べ済み）")
        return
    print("— %d件を調べます" % len(targets))
    day = datetime.date.today().isoformat()
    plan = []
    for k, pid, name, before in targets:
        try:
            r = recruitcheck.check(sites[k])
        except Exception as e:  # noqa: BLE001 ― 1件の失敗で全体を止めない
            r = ("分からない", "", "", "", "取得できない(%s)" % type(e).__name__)
        status, url, _y, issues, memo = r
        print("  %-6s %-18s %s%s" % (status, k, name, ("\n      気になる点：" + issues) if issues else ""))
        plan.append((pid, before, status, url, issues, day))
    print("— 入れる予定 %d件" % len(plan))
    if not apply:
        print("（--apply を付けると本番に書き込む）")
        return
    subprocess.run(["ssh", REMOTE, "sudo /opt/backup/backup-ewc.sh before-recruit"], check=True)
    done = remote_py(APPLY, plan, write=True)
    print("本番に入れた: %d件（予定 %d件。差は、その間にほかで書き換わった先）" % (len(done), len(plan)))


if __name__ == "__main__":
    main()
