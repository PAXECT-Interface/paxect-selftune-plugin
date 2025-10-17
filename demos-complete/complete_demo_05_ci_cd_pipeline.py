#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# PAXECT Core Complete — Demo 05: Enterprise Smoke (Audit + Fairness)
# Deterministic, zero-deps, ASCII-only. Prints human summary + single-line JSON for CI.

import json
import time
import hashlib
import tempfile
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pathlib import Path

# === CONFIG ================================================================
LOG_PATH = Path(tempfile.gettempdir()) / "paxect_enterprise_audit.jsonl"
STATE_PATH = Path(tempfile.gettempdir()) / "paxect_state.json"
HASH_BLOCK_SIZE = 1 << 16  # 64 KiB
POLICY_BUCKETS = ["alpha", "beta", "gamma", "delta"]

# === HELPERS ===============================================================
def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(HASH_BLOCK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()

def log_event(level: str, msg: str, data: Optional[Dict[str, Any]] = None) -> None:
    entry = {"ts": now_utc(), "level": level, "msg": msg, "data": data or {}}
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    # Keep stdout readable but minimal for demo
    print(f"[{level}] {msg}")

# === FAIRNESS METRIC (deterministic placeholder) ===========================
def fairness_scan(buckets: list) -> Dict[str, Any]:
    # Simulate a fairness check over buckets; all pass deterministically
    results = {b: 1.0 for b in buckets}
    bias_flags = 0
    return {"results": results, "bias_flags": bias_flags}

# === AUDIT EXECUTION =======================================================
def enterprise_audit_cycle() -> Dict[str, Any]:
    log_event("INFO", "Starting enterprise audit cycle")
    start = time.perf_counter()

    # 1) Create deterministic state
    STATE_PATH.write_text(json.dumps({"policy": POLICY_BUCKETS, "seed": 42}, indent=2), encoding="utf-8")

    # 2) Hash before
    hash_before = sha256(STATE_PATH)
    log_event("DEBUG", "State hash before", {"sha256": hash_before})

    # 3) Fairness
    fairness = fairness_scan(POLICY_BUCKETS)
    log_event("INFO", "Fairness scan complete", fairness)

    # 4) Hash after (should be identical)
    hash_after = sha256(STATE_PATH)
    identical = (hash_before == hash_after)
    log_event("INFO", "Integrity verification", {
        "identical": identical,
        "hash_before": hash_before,
        "hash_after": hash_after
    })

    # 5) Runtime
    runtime = round(time.perf_counter() - start, 3)
    log_event("INFO", "Audit runtime complete", {"seconds": runtime})

    # 6) Summary object for stdout + CI
    summary = {
        "runtime_s": runtime,
        "bias_flags": fairness["bias_flags"],
        "deterministic": identical
    }
    log_event("AUDIT", "Summary report", summary)
    return summary

# === MAIN ==================================================================
def main():
    print("\n=== PAXECT Core Complete — Enterprise Smoke Test ===")
    # Fresh log each run (demo behavior)
    if LOG_PATH.exists():
        try:
            LOG_PATH.unlink()
        except Exception:
            pass

    summary = enterprise_audit_cycle()

    # Human-readable summary
    print("\n--- Final Audit Summary ---")
    print(json.dumps(summary, indent=2))
    print("\nEnterprise audit completed successfully [OK].")

    # Machine-friendly single-line JSON (easy to copy/parse)
    print("AUDIT_SUMMARY_JSON=" + json.dumps(summary, separators=(",", ":")))

    print(f"Log saved at: {LOG_PATH}")

if __name__ == "__main__":
    main()
