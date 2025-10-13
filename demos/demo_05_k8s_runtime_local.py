# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
Demo 05 — Kubernetes Runtime (Local Simulation)
PAXECT SelfTune 5-in-1 (NumPy Integrated)
------------------------------------------
Simulates a simplified Kubernetes-like environment with multiple pods.
Each pod reports its resource metrics to a shared SelfTune engine,
which performs deterministic tuning and throttling decisions per cycle.
"""

import time
import random
from datetime import datetime
from paxect_selftune_plugin import tune, get_logs, run_matrix_benchmark

print("\nPAXECT SelfTune Kubernetes Runtime Simulation (v1.3.3, NumPy integrated)\n")

pods = ["pod-a", "pod-b", "pod-c"]
cycles = 5

for cycle in range(cycles):
    print(f"\nCycle {cycle + 1}/{cycles} — Cluster iteration")

    for pod in pods:
        # Simulate per-pod metrics
        exec_time = 0.8 + random.random() * 0.2
        overhead = 0.2 + random.random() * 0.5
        data_size = 1024 * (16 + random.randint(0, 128))

        decision = tune(exec_time=exec_time, overhead=overhead, last_bytes=data_size)
        print(f"{pod} → Decision: {decision}")

        matrix_time = run_matrix_benchmark(64)
        print(f"{pod} → Matrix benchmark: {matrix_time:.6f} seconds")

    time.sleep(1.0)

logs = get_logs(5)
print("\nRecent tuning logs:")
for log in logs:
    print(log)

print(f"\nKubernetes runtime simulation completed successfully at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

