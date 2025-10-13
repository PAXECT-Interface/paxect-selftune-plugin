"""
Demo 01 – Quick Start
PAXECT SelfTune Plugin (5-in-1)
--------------------------------
Minimal demonstration of baseline initialization and first-run tuning.
This example shows how the SelfTune engine performs its initial decision
cycle and logs a deterministic control action.

Run with:
    python demos/demo_01_quick_start.py
"""

from datetime import datetime
from paxect_selftune_plugin import SelfTune

# Initialize SelfTune with minimal configuration
engine = SelfTune(
    name="demo_01_quick_start",
    mode="baseline",
    verbose=True
)

print("\n[Demo 01] Starting baseline tuning sequence...\n")

# Example input payload (could be sensor values, metrics, etc.)
sample_input = {
    "cpu_load": 42.5,
    "memory_mb": 256,
    "io_wait_ms": 5.7
}

# Execute one deterministic tuning step
result = engine.run(sample_input)

# Display result
print(f"[{datetime.utcnow().isoformat()}Z] Decision output:")
print(result)

print("\n[Demo 01] Completed successfully.")
