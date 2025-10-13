"""
Demo 04 – Timed Throttle
PAXECT SelfTune Plugin (5-in-1)
--------------------------------
Demonstrates time-based throttling behavior.
The SelfTune engine applies throttling for a limited duration when
operating under elevated load or transient resource pressure.

Run with:
    python demos/demo_04_timed_throttle.py
"""

import time
from datetime import datetime
from paxect_selftune_plugin import SelfTune

# Initialize SelfTune in timed-safety mode
engine = SelfTune(
    name="demo_04_timed_throttle",
    mode="timed",
    verbose=True
)

print("\n[Demo 04] Starting timed throttle simulation...\n")

# Simulated runtime conditions
for t in range(10):
    metrics = {
        "cpu_load": 35 + (t * 5),
        "memory_mb": 300 + (t * 20),
        "runtime_sec": t * 1.5
    }

    result = engine.run(metrics)

    print(f"[{datetime.utcnow().isoformat()}Z] Tick {t+1} → Decision:")
    print(result)

    # Apply timed throttling if triggered
    if result.get("fail_safe"):
        throttle_time = (result.get("throttle_percent", 0) / 100.0) * 1.5
        print(f"[Timed] Throttle {result['throttle_percent']}% → delay {throttle_time:.2f}s\n")
        time.sleep(throttle_time)
    else:
        time.sleep(0.3)

print("\n[Demo 04] Timed throttle simulation completed successfully.")
