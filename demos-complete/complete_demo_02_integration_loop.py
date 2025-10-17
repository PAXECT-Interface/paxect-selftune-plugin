#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
PAXECT Core — Complete · Demo 02 (Integration Loop, full stack)
Stack: Core + SelfTune + Link + AEAD + Polyglot
Goal: Run multiple iterations with varying sizes; wait per-iteration so results are deterministic.
"""

import os, sys, time, json, base64, subprocess, secrets, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "inbox"
OUTBOX = ROOT / "outbox"
LINK_LOG = ROOT / "paxect_link_log.jsonl"

# Expected script names (adjust if yours differ)
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

    # SelfTune in learn mode for this demo
    os.environ.setdefault("AUTOTUNE_MODE", "learn")
    os.environ.setdefault("AUTOTUNE_LOG_LEVEL", "info")
    os.environ.setdefault("AUTOTUNE_STATE_PATH", str((ROOT / "paxect_state.json").resolve()))
    os.environ.setdefault("AUTOTUNE_LOG_PATH", str((ROOT / "paxect_log.jsonl").resolve()))
    os.environ["PAXECT_CORE"] = os.environ.get("PAXECT_CORE", f"python3 {CORE}")

    INBOX.mkdir(exist_ok=True); OUTBOX.mkdir(exist_ok=True)
    ensure_link_running()

    # Clean leftovers from previous runs (optional)
    for pat in ("iter_*.txt", "iter_*_poly.txt", "iter_*.aead", "recovered_*.txt"):
        for f in ROOT.glob(pat):
            try: f.unlink()
            except Exception: pass
    for pat in ("iter_*",):
        for f in (INBOX.glob(pat) | OUTBOX.glob(pat) if hasattr(INBOX, "glob") else []):
            try: f.unlink()
            except Exception: pass

    N = 20
    all_ok = True
    for i in range(1, N+1):
        plain = ROOT / f"iter_{i}.txt"
        poly  = ROOT / f"iter_{i}_poly.txt"
        aead  = ROOT / f"iter_{i}.aead"
        outp  = OUTBOX / f"iter_{i}"
        recov = ROOT / f"recovered_{i}.txt"

        # Produce random payload (8–128 KiB), base64 for safe text transforms
        kib = secrets.randbelow(121) + 8
        raw = secrets.token_bytes(kib * 1024)
        b64 = base64.b64encode(raw).decode("ascii")
        plain.write_text(b64, encoding="utf-8")

        # Polyglot transform
        subprocess.check_call([sys.executable, str(POLY), "--mode", "lower", "-i", str(plain), "-o", str(poly)])

        # AEAD encrypt
        with poly.open("rb") as fin, aead.open("wb") as fout:
            enc = subprocess.Popen([sys.executable, str(AEAD), "--mode","encrypt","--cipher","auto","--pass","demo-pass"],
                                   stdin=fin, stdout=fout)
            enc.communicate()
            if enc.returncode != 0:
                print(f"[ERROR] AEAD encrypt failed at iter {i}", file=sys.stderr)
                sys.exit(1)

        # Hand to Link and wait for outbox/iter_i
        (INBOX / aead.name).exists() and (INBOX / aead.name).unlink()
        (ROOT / aead.name).rename(INBOX / aead.name)

        # Wait (bounded) until Link produces outbox file
        t0 = time.time()
        while not outp.exists():
            if time.time() - t0 > 10.0:
                if LINK_LOG.exists():
                    print("\n— Link log (tail) —")
                    print(LINK_LOG.read_text()[-1000:])
                print(f"[ERROR] Timed out waiting for {outp}", file=sys.stderr)
                sys.exit(1)
            time.sleep(0.1)

        # Decrypt back and verify determinism for this iteration
        with outp.open("rb") as fin, recov.open("wb") as fout:
            dec = subprocess.Popen([sys.executable, str(AEAD), "--mode","decrypt","--pass","demo-pass"], stdin=fin, stdout=fout)
            dec.communicate()
            if dec.returncode != 0:
                print(f"[ERROR] AEAD decrypt failed at iter {i}", file=sys.stderr)
                sys.exit(1)

        if sha256_file(poly) == sha256_file(recov):
            print(f"OK iter_{i}")
        else:
            print(f"MISMATCH iter_{i}")
            all_ok = False
            break

    if all_ok:
        # Show recent SelfTune signals
        if AUTOTUNE_LOG.exists():
            print("\n— SelfTune (last 5 entries) —")
            lines = AUTOTUNE_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
            for ln in lines[-5:]:
                try:
                    obj = json.loads(ln)
                    print(f"{obj.get('decision',{}).get('label','?'):>9}  fail_safe={obj.get('fail_safe')}  throttle={obj.get('throttle_percent')}")
                except Exception:
                    print(ln)
        print("\nDemo 02 — SUCCESS ✅")
    else:
        print("\nDemo 02 — PARTIAL (fix mismatch above) ❌")

if __name__ == "__main__":
    main()
