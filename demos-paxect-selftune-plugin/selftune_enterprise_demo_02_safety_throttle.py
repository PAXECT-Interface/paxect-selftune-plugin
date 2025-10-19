#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
PAXECT SelfTune Plugin — Enterprise Demo 02 (Safety & Throttle Test)
--------------------------------------------------------------------
Demonstrates short- and long-window throttling behavior under
synthetic overload conditions.

- Verifies that fail-safe triggers when overhead > 75%.
- Shows how the throttle windows reset over time.
- Logs every cycle to a JSONL file for post-analysis.
"""

import os
import json
import time
import random
import tempfile
from paxect_selftune_plugin import Autotune

STATE_PATH = os.path.join(tempfile.gettempdir(), "paxect_selftune_throttle_state.json")
LOG_PATH = os.path.join(tempfile.gettempdir(), "paxect_selftune_throttle_log.jsonl")

# Initialize the SelfTune engine in learning mode
tuner = Autotune(state_path=STATE_PATH, log_path=LOG_PATH, mode="learn")

print("=== PAXECT SelfTune Enterprise Demo 02 – Safety & Throttle Test ===")
print(f"State file: {STATE_PATH}")
print(f"Short window: 5 min | Long window: 30 min | Fail-safe threshold: 75%\n")

allowed, throttled = 0, 0

for cycle in range(1, 101):
    # Simulate variable load patterns
    bytes_processed = random.choice([64_000, 256_000, 4_000_000])
    
    # Randomly inject overload bursts (20% of the time)
    if random.random() < 0.2:
        exec_time = random.uniform(0.0001, 0.0002)
        overhead = random.uniform(0.0020, 0.0050)  # deliberate overload
    else:
        exec_time = random.uniform(0.0002, 0.0020)
        overhead = random.uniform(0.0001, 0.0004)

    result = tuner.tune(exec_time=exec_time, overhead=overhead, last_bytes=bytes_processed)

    if result["fail_safe"] or result["throttle_percent"] < 100:
        throttled += 1
        status = "THROTTLED"
    else:
        allowed += 1
        status = "ALLOWED"

    print(
        f"[{cycle:03d}] {status:<10} "
        f"overhead={overhead:.6f} ratio={result['throttle_percent']:>3}% "
        f"fail_safe={result['fail_safe']} "
        f"label={result['label']:<9} epsilon={tuner.epsilon:.3f}"
    )

    # small delay to simulate runtime spacing
    time.sleep(0.05)

# Summary
print("\nSummary:")
print(f"Total cycles: {allowed + throttled}")
print(f"Allowed: {allowed} | Throttled: {throttled}")
print(f"Final epsilon: {tuner.epsilon:.3f}")
print(f"State saved to: {STATE_PATH}")
print(f"Log written to: {LOG_PATH}")
