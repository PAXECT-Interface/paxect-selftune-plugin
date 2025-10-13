# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
Demo 07 — Dashboard Snapshot
PAXECT SelfTune 5-in-1 (NumPy Integrated)
-----------------------------------------
Generates an aggregated snapshot from deterministic SelfTune batch results.
Reads output_results.jsonl (from Demo 06) and computes runtime statistics
for enterprise dashboard or monitoring integration.
"""

import json
from datetime import datetime
from pathlib import Path
from statistics import mean, pstdev

# File produced by Demo 06
input_file = Path("output_results.jsonl")
snapshot_file = Path("dashboard_snapshot.json")

print("\nPAXECT SelfTune Dashboard Snapshot (v1.3.3, NumPy integrated)\n")

if not input_file.exists():
    raise FileNotFoundError(
        f"Required file '{input_file}' not found. Run demo_06_batch_file_io.py first."
    )

# Load deterministic records
records = []
with input_file.open("r", encoding="utf-8") as f:
    for line in f:
        try:
            records.append(json.loads(line.strip()))
        except json.JSONDecodeError:
            continue

if not records:
    raise RuntimeError("No valid records found in output_results.jsonl")

# Compute aggregate statistics
blocksizes = [r.get("blocksize", 0) for r in records]
overheads = [r.get("avg_overhead", 0.0) if "avg_overhead" in r else r.get("overhead", 0.0) for r in records]
benchmarks = [r.get("benchmark_time", 0.0) for r in records]
throttles = [r.get("throttle_percent", 0) for r in records if isinstance(r.get("throttle_percent", 0), (int, float))]
labels = list({r.get("label", "n/a") for r in records})
policies = list({r.get("policy", "n/a") for r in records})

snapshot = {
    "datetime_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    "total_records": len(records),
    "avg_blocksize": round(mean(blocksizes), 2) if blocksizes else 0,
    "avg_overhead": round(mean(overheads), 4) if overheads else 0.0,
    "avg_benchmark_time": round(mean(benchmarks), 6) if benchmarks else 0.0,
    "avg_throttle_percent": round(mean(throttles), 2) if throttles else 0.0,
    "blocksize_stddev": round(pstdev(blocksizes), 2) if len(blocksizes) > 1 else 0.0,
    "benchmark_stddev": round(pstdev(benchmarks), 6) if len(benchmarks) > 1 else 0.0,
    "profiles_used": labels,
    "policies_used": policies,
}

# Write snapshot JSON
with snapshot_file.open("w", encoding="utf-8") as f:
    json.dump(snapshot, f, indent=4)

print("Dashboard Snapshot Summary:")
for k, v in snapshot.items():
    print(f"  {k}: {v}")

print(f"\nSnapshot saved to: {snapshot_file.resolve()}")
print("\n✅ Demo 07 completed successfully.")

