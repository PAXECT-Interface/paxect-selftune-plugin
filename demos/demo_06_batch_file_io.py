"""
Demo 06 – Batch File I/O
PAXECT SelfTune Plugin (5-in-1)
--------------------------------
Demonstrates batch processing of input data files.
The SelfTune engine reads JSONL-formatted metrics, processes them sequentially,
and writes deterministic tuning decisions to an output file.

Run with:
    python demos/demo_06_batch_file_io.py
"""

import json
from datetime import datetime
from pathlib import Path
from paxect_selftune_plugin import SelfTune

# Define file paths (local only)
input_file = Path("input_batches.jsonl")
output_file = Path("output_results.jsonl")

print("\n[Demo 06] Preparing batch file I/O environment...\n")

# Create a dummy input batch if it doesn't exist
if not input_file.exists():
    sample_data = [
        {"cpu_load": 30, "memory_mb": 256, "io_wait_ms": 5.0},
        {"cpu_load": 55, "memory_mb": 384, "io_wait_ms": 7.2},
        {"cpu_load": 68, "memory_mb": 512, "io_wait_ms": 8.4},
        {"cpu_load": 75, "memory_mb": 640, "io_wait_ms": 9.1},
    ]
    with input_file.open("w", encoding="utf-8") as f:
        for item in sample_data:
            f.write(json.dumps(item) + "\n")
    print(f"[Info] Created sample input file: {input_file}")

# Initialize SelfTune engine
engine = SelfTune(
    name="demo_06_batch_file_io",
    mode="batch",
    verbose=True
)

print("\n[Demo 06] Processing input batches...\n")

# Read input line by line and process
results = []
with input_file.open("r", encoding="utf-8") as f:
    for line_no, line in enumerate(f, start=1):
        record = json.loads(line.strip())
        result = engine.run(record)
        results.append(result)
        print(f"[{datetime.utcnow().isoformat()}Z] Record {line_no} processed.")

# Write results deterministically to output file
with output_file.open("w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r) + "\n")

print(f"\n[Demo 06] All batches processed successfully.")
print(f"[Output] Results saved to: {output_file.resolve()}")
