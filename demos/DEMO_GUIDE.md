#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
PAXECT SelfTune Plugin — Demo 1: Quickstart
-------------------------------------------
▶ Demonstrates adaptive decision logic within 10 seconds.
▶ Runs purely on synthetic workload simulation (no NumPy required).
▶ Cross-platform: Linux | macOS | Windows | BSD
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from paxect_selftune_hybrid import tune, get_autotune
import time, random, platform

print("╔══════════════════════════════════════════════════════════════════╗")
print("║        🚀 PAXECT SelfTune Demo 1 — Quickstart (v1.0)             ║")
print("╚══════════════════════════════════════════════════════════════════╝\n")

autotune = get_autotune(mode="learn")
system_info = f"{platform.system()} {platform.release()}"
print(f"[Info] Platform: {system_info}")
print(f"[Info] Mode: {autotune.mode}\n")

for i in range(10):
    n_bytes = random.randint(16 * 1024, 8 * 1024 * 1024)
    decision = tune(last_bytes=n_bytes)
    print(f"[{i+1:02d}] {decision}")
    time.sleep(0.5)

print("\n✅ Quickstart completed successfully.")
print("   Logs are stored in /tmp/autotune_log.jsonl\n")

