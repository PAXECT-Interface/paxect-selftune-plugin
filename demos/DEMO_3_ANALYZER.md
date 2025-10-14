#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
PAXECT SelfTune Plugin — Demo 3: Analyzer
-----------------------------------------
▶ Summarizes performance metrics and fail-safe frequency.
▶ Generates structured analytics report (JSON).
▶ Works even across multiple sessions (persistent state).
"""

import json, statistics, platform
from paxect_selftune_hybrid import get_logs

print("╔══════════════════════════════════════════════════════════════════╗")
print("║        📊 PAXECT SelfTune Demo 3 — Analyzer (v1.0)               ║")
print("╚══════════════════════════════════════════════════════════════════╝\n")

print(f"[Info] Platform: {platform.system()} {platform.release()}\n")

logs = get_logs(max_entries=500)
if not logs:
    print("⚠️  No logs found — run demo_quickstart or demo_enterprise_long first.\n")
else:
    overheads = [x["overhead"] for x in logs if x.get("overhead")]
    fail_safes = sum(1 for x in logs if x.get("fail_safe"))
    avg_overhead = statistics.mean(overheads) if overheads else 0
    print(f"Total log entries : {len(logs)}")
    print(f"Average overhead  : {avg_overhead:.6f}")
    print(f"Fail-safe triggers: {fail_safes}")
    print(f"Throttle samples  : {len([x for x in logs if x['throttle_percent'] < 100])}")

    report = {
        "entries": len(logs),
        "average_overhead": avg_overhead,
        "fail_safes": fail_safes,
        "platform": platform.system(),
        "version": "paxect-demo-suite-1.0",
    }
    with open("analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n✅ Analysis complete — report saved as analysis_report.json\n")
