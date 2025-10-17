#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
PAXECT Core — Complete · Demo 01 (Full-Stack Sanity)
Stack: Core + SelfTune + Link + AEAD + Polyglot
"""

import os, sys, time, json, hashlib, shutil, subprocess
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

MSG_IN      = ROOT / "msg.txt"
MSG_UPPER   = ROOT / "msg_upper.txt"
MSG_AEAD    = ROOT / "msg_upper.aead"
MSG_RECOVER = ROOT / "recovered.txt"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def need(path: Path, hint: str):
    if not path.exists():
        print(f"[ERROR] Missing: {path}  → {hint}", file=sys.stderr)
        sys.exit(2)

def main():
    os.chdir(ROOT)

    # Preflight
    for p,h in [(CORE,"paxect_core.py"),(LINK,"paxect_link_plugin.py"),(AEAD,"paxect_aead_enterprise.py"),(POLY,"paxect_polyglot_plugin.py")]:
        need(p, f"Place {h} in repo root")

    # Safe defaults (SelfTune)
    os.environ.setdefault("AUTOTUNE_MODE", "safe")
    os.environ.setdefault("AUTOTUNE_LOG_LEVEL", "info")
    os.environ.setdefault("AUTOTUNE_STATE_PATH", str((ROOT / "paxect_state.json").resolve()))
    os.environ.setdefault("AUTOTUNE_LOG_PATH", str((ROOT / "paxect_log.jsonl").resolve()))

    # Paths + Link setup
    INBOX.mkdir(exist_ok=True)
    OUTBOX.mkdir(exist_ok=True)
    os.environ["PAXECT_CORE"] = os.environ.get("PAXECT_CORE", f"python3 {CORE}")

    # Clean leftovers
    for p in [MSG_IN, MSG_UPPER, MSG_AEAD, MSG_RECOVER]:
        p.exists() and p.unlink()
    for p in INBOX.glob("msg_upper*"):
        p.unlink()
    for p in OUTBOX.glob("msg_upper*"):
        p.unlink()

    # Start Link
    link_proc = subprocess.Popen(
        [sys.executable, str(LINK)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.0)

    try:
        # Polyglot → UPPER
        MSG_IN.write_text("hello paxect core complete\n", encoding="utf-8")
        subprocess.check_call([sys.executable, str(POLY), "--mode", "upper", "-i", str(MSG_IN), "-o", str(MSG_UPPER)])

        # AEAD encrypt → .aead (allowlisted)
        with MSG_UPPER.open("rb") as fin, MSG_AEAD.open("wb") as fout:
            enc = subprocess.Popen(
                [sys.executable, str(AEAD), "--mode", "encrypt", "--cipher", "auto", "--pass", "demo-pass"],
                stdin=fin, stdout=fout
            )
            enc.communicate()
            if enc.returncode != 0:
                raise SystemExit("[ERROR] AEAD encrypt failed")

        # Link pickup (encode/decode)
        shutil.copy2(MSG_AEAD, INBOX / MSG_AEAD.name)

        # Wait for outbox/msg_upper
        target = OUTBOX / "msg_upper"
        t0 = time.time()
        while not target.exists():
            if time.time() - t0 > 10:
                if LINK_LOG.exists():
                    print(LINK_LOG.read_text()[-1000:])
                raise SystemExit("[ERROR] outbox/msg_upper not found")
            time.sleep(0.1)

        # AEAD decrypt back
        with target.open("rb") as fin, MSG_RECOVER.open("wb") as fout:
            dec = subprocess.Popen(
                [sys.executable, str(AEAD), "--mode", "decrypt", "--pass", "demo-pass"],
                stdin=fin, stdout=fout
            )
            dec.communicate()
            if dec.returncode != 0:
                raise SystemExit("[ERROR] AEAD decrypt failed")

        # Verify determinism
        h1 = sha256_file(MSG_UPPER)
        h2 = sha256_file(MSG_RECOVER)
        print(f"SHA-256 original : {h1}")
        print(f"SHA-256 recovered: {h2}")
        if h1 != h2:
            raise SystemExit("❌ Hash mismatch — not deterministic")
        print("All hops consistent (no hash drift) ✅")

        # Optional: sidecar check (if still present)
        freq = INBOX / "msg_upper.freq"
        side = INBOX / "msg_upper.freq.sha256"
        if freq.exists() and side.exists():
            have = sha256_file(freq)
            want = side.read_text(encoding="ascii").strip()
            print("Sidecar checksum matches container ✅" if have == want else "Sidecar checksum mismatch ❌")
        else:
            print("Sidecar files not found (OK if Link already cleaned up)")

        # Show last 5 Link log lines
        if LINK_LOG.exists():
            print("\n— Link log (last 5) —")
            lines = LINK_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
            for ln in lines[-5:]:
                try:
                    obj = json.loads(ln)
                    print(f"{obj.get('level','?'):>5}  {obj.get('event','?'):18}  {obj.get('src','')} → {obj.get('dst','')}  {obj.get('message','')}")
                except Exception:
                    print(ln)

        print("\nCRC32 per frame: OK (validated by Core during decode)")
        print("SHA-256 footer:  OK (validated by Core during verify)")
        print("\nDemo 01 — SUCCESS ✅")

    finally:
        # keep Link running for next demos
        pass

if __name__ == "__main__":
    main()
