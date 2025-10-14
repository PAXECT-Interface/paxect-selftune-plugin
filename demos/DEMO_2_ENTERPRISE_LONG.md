#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
PAXECT SelfTune Plugin — Demo 2: Enterprise Long Run
----------------------------------------------------
▶ Performs extended runtime with adaptive learning (≈10 minutes).
▶ Uses matrix & I/O benchmarks when NumPy is available.
▶ Exports full run statistics as enterprise_results.json
"""

import time, random, json, platform, sys
from paxect_selftune_hybrid import get_autotune, tune, HAS_NUMPY

print("╔══════════════════════════════════════════════════════════════════╗")
print("║        🧠 PAXECT SelfTune Demo 2 — Enterprise Long Run (v1.0)    ║")
print("╚══════════════════════════════════════════════════════════════════╝\n")

autotune = get_autotune(mode="learn")
print(f"[Info] Platform: {platform.system()} {platform.release()}")
print(f"[Info] NumPy detected: {HAS_NUMPY}")
print(f"[Info] Mode: {autotune.mode}\n")

results = []
start_time = time.time()
total_steps = 600  # ≈10 minutes (1 Hz)

try:
    for i in range(total_steps):
        n_bytes = random.randint(128 * 1024, 8 * 1024 * 1024)
        decision = tune(last_bytes=n_bytes, run_benchmarks=HAS_NUMPY)
        results.append(decision)
        if (i + 1) % 60 == 0:
            elapsed = int(time.time() - start_time)
            print(f"⏱  Progress: {i+1}/{total_steps}  |  Elapsed: {elapsed}s")
        time.sleep(1)

except KeyboardInterrupt:
    print("\n⚠️  Interrupted by user — saving partial results...")

finally:
    with open("enterprise_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    duration = round(time.time() - start_time, 2)
    print(f"\n✅ Enterprise run complete in {duration}s")
    print("   Results exported → enterprise_results.json\n")

