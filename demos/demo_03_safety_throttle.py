"""
Demo 03 – Safety Throttle
PAXECT SelfTune Plugin (5-in-1)
--------------------------------
Demonstrates the built-in safety throttle mechanism.
The engine monitors simulated performance metrics and automatically
reduces its operation rate if safety thresholds are exceeded.

Run with:
    python demos/demo_03_safety_throttle.py
"""

import time
from datetime import datetime
from paxect_selftune_plugin import SelfTune

# Initialize SelfTune with safety mode enabled
engine = SelfTune(
    name="demo_03_safety_throttle",
    mode="safe",
    verbose=True
)

print("\n[Demo 03] Starting safety throttle simulation...\n")

# Simulate changing system load
for cycle in range(6):
    # Increasing CPU load and temperature
    metrics = {
        "cpu_load": 40 + cycle * 12,
        "temperature_c": 50 + cycle * 5,
        "io_latency_ms": 6 + (cycle * 0.8),
    }

    result = engine.run(metrics)

    print(f"[{datetime.utcnow().isoformat()}Z] Cycle {cycle+1} → Decision:")
    print(result)

    # If SelfTune decides to throttle, apply delay
    if result.get("fail_safe"):
        delay = (result.get("throttle_percent", 0) / 100.0) * 2.0
        print(f"[Throttle] Applying {result['throttle_percent']}% slowdown ({delay:.2f}s)...\n")
        time.sleep(delay)
    else:
        time.sleep(0.5)

print("\n[Demo 03] Safety throttle simulation completed successfully.")
