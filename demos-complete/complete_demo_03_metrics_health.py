#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
PAXECT Core — Complete · Demo 03 (Safety/Throttle, full stack)
Stack: Core + SelfTune + Link + AEAD + Polyglot

What this demo stresses:
- Burst traffic to trigger SelfTune safety windows (5m/30m) and throttling.
- Full pipeline exercised; determinism verified on the last item.
- Summarizes throttle activity (throttle_percent < 100 and fail_safe).
"""

import os, sys, time, json, base64, subprocess, secrets, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "inbox"
OUTBOX = ROOT / "outbox"
LINK_LOG = ROOT / "paxect_link_log.jsonl"

# Expected script names in repo root (adjust if yours differ)
CORE = ROOT / "paxect_core.py"
LINK = ROOT / "paxect_link_plugin.py"
AEAD = ROOT / "paxect_aead_enterprise.py"
POLY = ROOT / "paxect_polyglot_plugin.py"

AUTOTUNE_LOG = Path(os.environ.get("AUTOTUNE_LOG_PATH", str(ROOT / "paxect_log.jsonl")))

def need(path: Path, hint: str):
    if not path.exists():
        print(f"[ERROR] Missing: {path}  → {hint}", file=sys.stderr)
        sys.exit(2)

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def ensure_link_running():
    try:
        subprocess.check_call(["pgrep","-f","paxect_link_plugin.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        subprocess.Popen([sys.executable, str(LINK)], cwd=ROOT,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)

def main():
    os.chdir(ROOT)
    # Preflight
    for p,h in [(CORE,"paxect_core.py"),(LINK,"paxect_link_plugin.py"),(AEAD,"paxect_aead_enterprise.py"),(POLY,"paxect_polyglot_plugin.py")]:
        need(p, f"Place {h} in repo root")

    # SelfTune "safe" mode + logs
    os.environ["AUTOTUNE_MODE"] = os.environ.get("AUTOTUNE_MODE", "safe")
    os.environ.setdefault("AUTOTUNE_LOG_LEVEL", "info")
    os.environ.setdefault("AUTOTUNE_STATE_PATH", str((ROOT / "paxect_state.json").resolve()))
    os.environ.setdefault("AUTOTUNE_LOG_PATH", str((ROOT / "paxect_log.jsonl").resolve()))
    os.environ["PAXECT_CORE"] = os.environ.get("PAXECT_CORE", f"python3 {CORE}")

    INBOX.mkdir(exist_ok=True); OUTBOX.mkdir(exist_ok=True)
    ensure_link_running()

    # Clean leftovers (optional)
    for pat in ("burst_*.txt", "burst_*_poly.txt", "burst_*.aead", "recovered_burst_last.txt"):
        for f in ROOT.glob(pat):
            try: f.unlink()
            except Exception: pass
    for f in list(INBOX.glob("burst_*")) + list(OUTBOX.glob("burst_*")):
        try: f.unlink()
        except Exception: pass

    # Burst parameters
    N = 200               # number of items
    MIN_KB, MAX_KB = 16, 64   # payload size range
    SLEEP_BETWEEN = 0.03      # tiny delay to keep pressure but not overwhelm stdout

    print(f"[INFO] Burst start: N={N}, size={MIN_KB}–{MAX_KB} KiB, mode={os.environ['AUTOTUNE_MODE']}")

    # Fire the burst (no per-iteration wait on outbox; Link will keep up)
    for i in range(1, N+1):
        plain = ROOT / f"burst_{i}.txt"
        poly  = ROOT / f"burst_{i}_poly.txt"
        aead  = ROOT / f"burst_{i}.aead"

        kib = secrets.randbelow(MAX_KB - MIN_KB + 1) + MIN_KB
        raw = secrets.token_bytes(kib * 1024)
        plain.write_text(base64.b64encode(raw).decode("ascii"), encoding="utf-8")

        subprocess.check_call([sys.executable, str(POLY), "--mode", "lower", "-i", str(plain), "-o", str(poly)])

        with poly.open("rb") as fin, aead.open("wb") as fout:
            enc = subprocess.Popen([sys.executable, str(AEAD), "--mode","encrypt","--cipher","auto","--pass","demo-pass"],
                                   stdin=fin, stdout=fout)
            enc.communicate()
            if enc.returncode != 0:
                print(f"[ERROR] AEAD encrypt failed at item {i}", file=sys.stderr)
                sys.exit(1)

        # hand to Link; tiny delay to modulate pressure
        (ROOT / aead.name).rename(INBOX / aead.name)
        time.sleep(SLEEP_BETWEEN)

    # Wait until the last outbox artifact is present
    last_out = OUTBOX / f"burst_{N}"
    t0 = time.time()
    while not last_out.exists():
        if time.time() - t0 > 30.0:
            print("[ERROR] Timeout waiting for last outbox artifact; check paxect_link_log.jsonl", file=sys.stderr)
            if LINK_LOG.exists():
                print("\n— Link log (tail) —\n" + LINK_LOG.read_text()[-1500:])
            sys.exit(1)
        time.sleep(0.1)

    # Determinism check on the last item
    last_poly   = ROOT / f"burst_{N}_poly.txt"
    last_recov  = ROOT / "recovered_burst_last.txt"
    with last_out.open("rb") as fin, last_recov.open("wb") as fout:
        dec = subprocess.Popen([sys.executable, str(AEAD), "--mode","decrypt","--pass","demo-pass"], stdin=fin, stdout=fout)
        dec.communicate()
        if dec.returncode != 0:
            print("[ERROR] AEAD decrypt failed on last item", file=sys.stderr)
            sys.exit(1)

    h1 = sha256_file(last_poly)
    h2 = sha256_file(last_recov)
    print(f"SHA-256 last-plain : {h1}")
    print(f"SHA-256 recovered  : {h2}")
    if h1 == h2:
        print("✅ Deterministic under burst")
    else:
        print("❌ Last item mismatch (investigate timing or policy)")

    # Summarize throttling/fail_safe from SelfTune log
    if AUTOTUNE_LOG.exists():
        try:
            lines = AUTOTUNE_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
            recent = lines[-400:]  # last window
            th_cnt = fs_cnt = 0
            last_entries = []
            for ln in recent:
                try:
                    obj = json.loads(ln)
                    if isinstance(obj, dict):
                        if obj.get("throttle_percent", 100) < 100:
                            th_cnt += 1
                        if obj.get("fail_safe") is True:
                            fs_cnt += 1
                        last_entries.append(obj)
                except Exception:
                    continue
            print(f"\n[SUMMARY] Throttle events: {th_cnt}  ·  Fail-safe trips: {fs_cnt}")
            print("— SelfTune (last 5) —")
            for obj in last_entries[-5:]:
                lab = (obj.get("decision") or {}).get("label", "?")
                thr = obj.get("throttle_percent")
                fs  = obj.get("fail_safe")
                print(f"{lab:>9}  fail_safe={fs}  throttle={thr}")
        except Exception as e:
            print(f"[WARN] Could not parse AUTOTUNE_LOG: {e}")
    else:
        print("[INFO] AUTOTUNE_LOG not found; set AUTOTUNE_LOG_PATH to capture entries.")

    print("\nDemo 03 — DONE ✅")

if __name__ == "__main__":
    main()
