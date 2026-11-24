"""今のサイトをスマホとして開き、横幅と警告の画面かを測る。python3 measure.py <キー>  → キー\t横幅\tURL\t題名"""
import json, os, random, subprocess, sys, tempfile, time, urllib.request, shutil
sys.path.insert(0, os.path.expanduser("~/ewc-proposals")); sys.path.insert(0, os.path.expanduser("~/.claude/skills/hp-sample/scripts"))
import nowshot as N, shoot as sh

def run(keys):
    for k in keys:
        q = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--one", k], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True, start_new_session=True)
        try:
            o = q.communicate(timeout=45)[0].strip()
        except subprocess.TimeoutExpired:
            os.killpg(q.pid, 9); q.wait(); o = ""
        print(o or f"{k}	?", flush=True)


if sys.argv[1:2] != ["--one"]:
    run(sys.argv[1:]); sys.exit()
sys.argv.pop(1)
k = sys.argv[1]; url = N.load_teian()[k]
port = random.randint(20000, 40000); prof = tempfile.mkdtemp(prefix="chrome-")
p = subprocess.Popen([sh.CHROME, "--headless=new", "--hide-scrollbars", f"--remote-debugging-port={port}",
    "--disable-features=HttpsUpgrades,HttpsFirstBalancedModeAutoEnable,HttpsFirstModeV2ForTypicallySecureUsers",
    f"--user-data-dir={prof}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(100):
        try:
            page = next(t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json")) if t.get("type") == "page"); break
        except Exception: time.sleep(0.1)
    ws = sh.WS(page["webSocketDebuggerUrl"]); ws.call("Page.enable"); ws.call("Network.enable")
    ws.call("Network.setUserAgentOverride", userAgent=N.UA)
    ws.call("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    ws.call("Page.navigate", url=url); ws.wait_event("Page.loadEventFired", 30); time.sleep(3)
    r = ws.call("Runtime.evaluate", returnByValue=True, expression="JSON.stringify([Math.max(document.documentElement.scrollWidth, document.body?document.body.scrollWidth:0), window.innerWidth, location.href, document.title])")
    w, iw, href, title = json.loads(r["result"]["value"])
    print(f"{k}\t{w}\t{iw}\t{href}\t{title}")
finally:
    p.kill(); shutil.rmtree(prof, ignore_errors=True)
