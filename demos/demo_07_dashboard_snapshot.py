"""
Demo 07 – Dashboard Snapshot
PAXECT SelfTune Plugin (5-in-1)
--------------------------------
Generates a compact performance dashboard snapshot from prior batch results.
This demo reads deterministic output data and aggregates key runtime statistics
for quick offline visualization or integration into enterprise dashboards.

Run with:
    python demos/demo_07_dashboard_snapshot.py
"""

import json
from datetime import datetime
from pathlib import Path
from statistics import mean

# File produced by demo_06_batch_file_io.py
input_file = Path("output_results.jsonl")
snapshot_file = Path("dashboard_snapshot.json")

print("\n[Demo 07] Generating dashboard snapshot...\n")

if not input_file.exists():
    raise FileNotFoundError(
        f"Input file '{input_file}' not found. "
        "Please run demo_06_batch_file_io.py first."
    )

# Load all records
records = []
with input_file.open("r", encoding="utf-8") as f:
    for line in f:
        try:
            records.append(json.loads(line.strip()))
        except json.JSONDecodeError:
            continue

if not records:
    raise RuntimeError("No valid records found in output file.")

# Aggregate deterministic metrics
snapshot = {
    "datetime_utc": datetime.utcnow().isoformat() + "Z",
    "total_records": len(records),
    "avg_blocksize": mean(r.get("decision", {}).get("blocksize", 0) for r in records),
    "avg_overhead": mean(r.get("overhead", 0.0) for r in records),
    "avg_throttle_percent": mean(
        r.get("decision", {}).get("throttle_percent", 0)
        for r in records
        if isinstance(r.get("decision", {}).get("throttle_percent", 0), (int, float))
    ),
    "policies_used": list({r.get("decision", {}).get("policy", "n/a") for r in records}),
}

# Write snapshot to JSON
with snapshot_file.open("w", encoding="utf-8") as f:
    json.dump(snapshot, f, indent=4)

print("[Dashboard Snapshot]")
for k, v in snapshot.items():
    print(f"  {k}: {v}")

print(f"\n[Demo 07] Snapshot saved to: {snapshot_file.resolve()}")
