#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
PAXECT SelfTune Plugin — Enterprise Demo 03 (Adaptive Benchmark)
----------------------------------------------------------------
This demo evaluates the SelfTune engine's ability to adapt its
runtime decisions to hardware performance profiles.

It compares two execution modes:
  - Without NumPy (pure Python path)
  - With NumPy (hardware-accelerated vector path)

Outputs comparative timings and adaptive profile results.
"""

import os
import json
import time
import tempfile
from paxect_selftune_plugin import Autotune, HAS_NUMPY, matrix_benchmark, io_benchmark

STATE_PATH = os.path.join(tempfile.gettempdir(), "paxect_selftune_benchmark_state.json")
LOG_PATH = os.path.join(tempfile.gettempdir(), "paxect_selftune_benchmark_log.jsonl")

print("=== PAXECT SelfTune Enterprise Demo 03 – Adaptive Benchmark ===")
print(f"NumPy detected: {HAS_NUMPY}")
print(f"State file: {STATE_PATH}")
print(f"Log file: {LOG_PATH}\n")

tuner = Autotune(state_path=STATE_PATH, log_path=LOG_PATH, mode="learn")

# --- Phase 1: Baseline run (no hardware acceleration) ---
print("[Phase 1] Baseline simulation (no NumPy path)")
baseline_results = []
for i in range(10):
    result = tuner.tune(run_benchmarks=False)
    baseline_results.append(result["label"])
    time.sleep(0.05)
print("Baseline label distribution:", {x: baseline_results.count(x) for x in set(baseline_results)})
time.sleep(1)

# --- Phase 2: Accelerated run (NumPy path) ---
print("\n[Phase 2] Hardware acceleration path (NumPy enabled if available)")
if HAS_NUMPY:
    bench_results = []
    for i in range(10):
        matrix_t = matrix_benchmark(128)
        io_t = io_benchmark(256)
        result = tuner.tune(exec_time=matrix_t, overhead=io_t, run_benchmarks=True)
        bench_results.append({
            "matrix_t": matrix_t,
            "io_t": io_t,
            "label": result["label"],
            "fail_safe": result["fail_safe"]
        })
        time.sleep(0.05)
    avg_matrix = sum(x["matrix_t"] for x in bench_results) / len(bench_results)
    avg_io = sum(x["io_t"] for x in bench_results) / len(bench_results)
    print(f"Average matrix time: {avg_matrix:.6f}s | I/O time: {avg_io:.6f}s")
    print("Adaptive labels:", [x["label"] for x in bench_results])
else:
    print("NumPy not available — skipping accelerated phase.")

# --- Summary ---
summary = {
    "numpy_detected": HAS_NUMPY,
    "final_epsilon": tuner.epsilon,
    "state_path": STATE_PATH,
    "log_path": LOG_PATH,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
}
print("\n[Summary]")
print(json.dumps(summary, indent=2))
print("\nDemo complete. Adaptive benchmark finished successfully.")
