# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
Demo 02 — Integration Loop
PAXECT SelfTune 5-in-1 (NumPy Integrated)
-----------------------------------------
Demonstrates continuous integration of SelfTune within a simulated runtime loop.
Each iteration performs a tuning step and a deterministic matrix benchmark.
"""

import time
from paxect_selftune_plugin import tune, get_logs, run_matrix_benchmark

print("\nPAXECT SelfTune Integration Loop (v1.3.3, NumPy integrated)\n")

# --- Configuration ---
iterations = 5
exec_time = 1.0
overhead_base = 0.2
data_size = 1024 * 32  # 32 KB payload

for i in range(iterations):
    overhead = overhead_base + (i * 0.05)
    print(f"\nIteration {i + 1}/{iterations}")
    decision = tune(exec_time=exec_time, overhead=overhead, last_bytes=data_size)
    print("Decision:", decision)

    # Run benchmark per iteration
    matrix_time = run_matrix_benchmark(128)
    print(f"Matrix benchmark time: {matrix_time:.6f} seconds")

    time.sleep(0.5)

# --- Retrieve and display last few logs ---
logs = get_logs(5)
print("\nRecent tuning logs:")
for log in logs:
    print(log)

print("\nIntegration loop completed successfully.")

