"""
Demo 02 – Integration Loop
PAXECT SelfTune Plugin (5-in-1)
--------------------------------
Demonstrates continuous integration of SelfTune within an application loop.
This version simulates a runtime that feeds dynamic metrics into the engine
and collects deterministic decisions over multiple iterations.

Run with:
    python demos/demo_02_integration_loop.py
"""

import time
from datetime import datetime
from paxect_selftune_plugin import SelfTune

# Initialize SelfTune
engine = SelfTune(
    name="demo_02_integration_loop",
    mode="learn",
    verbose=True
)

print("\n[Demo 02] Starting integration loop...\n")

# Simulated dynamic metrics
for step in range(5):
    metrics = {
        "cpu_load": 30 + step * 8,
        "memory_mb": 256 + step * 32,
        "io_wait_ms": 4.0 + (step * 0.5),
    }

    result = engine.run(metrics)
    print(f"[{datetime.utcnow().isoformat()}Z] Step {step+1} → Decision:")
    print(result)
    time.sleep(0.5)

print("\n[Demo 02] Integration loop completed successfully.")
