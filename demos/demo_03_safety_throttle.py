# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
Demo 03 — Safety Throttle
PAXECT SelfTune 5-in-1 (NumPy Integrated)
-----------------------------------------
Demonstrates automatic throttling when the average overhead exceeds the safe limit.
Each cycle simulates rising system load; SelfTune triggers fail-safe control if needed.
"""

import time
from paxect_selftune_plugin import tune, get_logs, run_matrix_benchmark
from datetime import datetime

print("\nPAXECT SelfTune Safety Throttle Simulation (v1.3.3, NumPy integrated)\n")

cycles = 6
exec_time = 0.8
overhead_base = 0.4
data_size = 1024 * 64  # 64 KB payload

for c in range(cycles):
    overhead = overhead_base + (c * 0.15)
    print(f"\nCycle {c + 1}/{cycles}")
    decision = tune(exec_time=exec_time, overhead=overhead, last_bytes=data_size)
    print("Decision:", decision)

    matrix_time = run_matrix_benchmark(128)
    print(f"Matrix benchmark time: {matrix_time:.6f} seconds")

    if decision.get("fail_safe"):
        throttle = decision.get("throttle_percent", 100)
        delay = (throttle / 100.0) * 2.0
        print(f"Fail-safe triggered: {throttle}% throttle applied for {delay:.2f}s")
        time.sleep(delay)
    else:
        time.sleep(0.5)

logs = get_logs(5)
print("\nRecent tuning logs:")
for log in logs:
    print(log)

print(f"\nSafety throttle simulation completed successfully at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

