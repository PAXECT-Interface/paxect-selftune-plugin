# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
Demo 04 — Timed Throttle
PAXECT SelfTune 5-in-1 (NumPy Integrated)
-----------------------------------------
Demonstrates time-based throttling every 5 and 30 minutes.
Simulates runtime progression with varying system load and delay intervals.
"""

import time
from paxect_selftune_plugin import tune, get_logs, run_matrix_benchmark
from datetime import datetime

print("\nPAXECT SelfTune Timed Throttle Simulation (v1.3.3, NumPy integrated)\n")

ticks = 10
exec_time = 0.6
overhead_base = 0.3
data_size = 1024 * 128  # 128 KB payload

for t in range(ticks):
    overhead = overhead_base + (t * 0.07)
    print(f"\nTick {t + 1}/{ticks}")
    decision = tune(exec_time=exec_time, overhead=overhead, last_bytes=data_size)
    print("Decision:", decision)

    matrix_time = run_matrix_benchmark(128)
    print(f"Matrix benchmark time: {matrix_time:.6f} seconds")

    if decision.get("fail_safe"):
        throttle = decision.get("throttle_percent", 100)
        delay = (throttle / 100.0) * 1.5
        print(f"Fail-safe triggered: {throttle}% throttle applied for {delay:.2f}s")
        time.sleep(delay)
    else:
        time.sleep(0.3)

logs = get_logs(5)
print("\nRecent tuning logs:")
for log in logs:
    print(log)

print(f"\nTimed throttle simulation completed successfully at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

