# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
Demo 01 — Quick Start
PAXECT SelfTune 5-in-1 (NumPy Integrated)
-----------------------------------------
Minimal demonstration of the SelfTune engine.
Performs one deterministic tuning step and a matrix benchmark.
"""

from paxect_selftune_plugin import tune, get_logs, run_matrix_benchmark
from datetime import datetime

print("\nPAXECT SelfTune Quick Start (v1.3.3, NumPy integrated)\n")

decision = tune(exec_time=1.0, overhead=0.2, last_bytes=4096)
print("Decision:", decision)

benchmark_time = run_matrix_benchmark(128)
print(f"Matrix benchmark time: {benchmark_time:.6f} seconds")

logs = get_logs(3)
print("\nLast 3 logs:")
for log in logs:
    print(log)

print(f"\nDemo completed successfully at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")


