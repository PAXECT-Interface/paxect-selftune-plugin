# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
Demo 06 — Batch File I/O
PAXECT SelfTune 5-in-1 (NumPy Integrated)
-----------------------------------------
Demonstrates deterministic batch processing of JSONL-formatted input metrics.
Each record is processed through SelfTune, benchmarked with NumPy, and written
to an output file with full UTC logging.
"""

import json
from datetime import datetime
from pathlib import Path
from paxect_selftune_plugin import tune, get_logs, run_matrix_benchmark

# Define input/output paths
input_file = Path("input_batches.jsonl")
output_file = Path("output_results.jsonl")

print("\nPAXECT SelfTune Batch File I/O (v1.3.3, NumPy integrated)\n")

# Create dummy input batch if it does not exist
if not input_file.exists():
    sample_data = [
        {"exec_time": 0.9, "overhead": 0.2, "last_bytes": 4096},
        {"exec_time": 1.2, "overhead": 0.3, "last_bytes": 8192},
        {"exec_time": 1.5, "overhead": 0.4, "last_bytes": 16384},
        {"exec_time": 0.8, "overhead": 0.25, "last_bytes": 65536},
    ]
    with input_file.open("w", encoding="utf-8") as f:
        for item in sample_data:
            f.write(json.dumps(item) + "\n")
    print(f"Created sample input file: {input_file}")

print("\nProcessing input batches...\n")

results = []
with input_file.open("r", encoding="utf-8") as f:
    for line_no, line in enumerate(f, start=1):
        record = json.loads(line.strip())
        decision = tune(**record)
        decision["benchmark_time"] = run_matrix_benchmark(64)
        decision["record_id"] = line_no
        results.append(decision)
        print(f"Record {line_no} processed → Decision: {decision}")

# Write deterministic output
with output_file.open("w", encoding="utf-8") as f:
    for result in results:
        f.write(json.dumps(result) + "\n")

print(f"\nBatch file processing completed successfully at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"Output written to: {output_file.resolve()}")

# Display last few logs
logs = get_logs(3)
print("\nRecent tuning logs:")
for log in logs:
    print(log)

