# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
Demo 01 — Quick Start
PAXECT SelfTune 5-in-1 (NumPy Integrated)
-----------------------------------------
Basic quick-start demonstration with deterministic matrix benchmark.
"""

from paxect_selftune_plugin import tune, get_logs, run_matrix_benchmark
import time

print("\n PAXECT SelfTune Quick Start (v1.3.3, NumPy integrated)\n")

# --- Example workload parameters ---
exec_time = 1.0       # seconds (simulated)
overhead = 0.2        # seconds (simulated)
last_bytes = 4096     # bytes processed

# --- Run tuning decision ---
decision = tune(exec_time=exec_time, overhead=overhead, last_bytes=last_bytes)
print("Decision:", decision)

# --- Run NumPy benchmark for deterministic test ---
matrix_time = run_matrix_benchmark(128)
print(f"Matrix benchmark time: {matrix_time:.6f} seconds")

# --- Show recent logs ---
logs = get_logs(3)
print("\n Last 3 logs:")
for log in logs:
    print(log)

print("\n Demo completed successfully at", time.strftime('%Y-%m-%d %H:%M:%S'))

