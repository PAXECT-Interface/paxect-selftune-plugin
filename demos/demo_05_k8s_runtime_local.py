"""
Demo 05 – Kubernetes Runtime (Local Simulation)
PAXECT SelfTune Plugin (5-in-1)
--------------------------------
Simulates a simplified Kubernetes-like environment with multiple pods.
Each simulated pod reports its resource metrics to a shared SelfTune engine,
which makes deterministic tuning decisions in isolation per pod.

Run with:
    python demos/demo_05_k8s_runtime_local.py
"""

import time
import random
from datetime import datetime
from paxect_selftune_plugin import SelfTune

# Simulated pod identifiers
pods = ["pod-a", "pod-b", "pod-c"]

# Create a shared SelfTune instance (cluster-level)
engine = SelfTune(
    name="demo_05_k8s_runtime_local",
    mode="cluster",
    verbose=True
)

print("\n[Demo 05] Starting local Kubernetes runtime simulation...\n")

# Simulate N scheduling cycles
for cycle in range(5):
    print(f"\n[Cycle {cycle+1}] ----------------------------")

    for pod in pods:
        metrics = {
            "pod": pod,
            "cpu_load": 20 + random.randint(0, 60),
            "memory_mb": 256 + random.randint(0, 256),
            "latency_ms": 3.0 + random.random() * 4.0,
        }

        # Each pod request goes through SelfTune deterministically
        result = engine.run(metrics)

        print(f"[{datetime.utcnow().isoformat()}Z] {pod} → Decision:")
        print(result)

    # Simulate cluster-level delay between cycles
    time.sleep(1.0)

print("\n[Demo 05] Local Kubernetes simulation completed successfully.")
