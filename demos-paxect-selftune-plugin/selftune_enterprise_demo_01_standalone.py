#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
PAXECT SelfTune Plugin — Enterprise Demo 01 (Stand-alone)
----------------------------------------------------------
Adaptive controller demonstration.

Shows how the SelfTune engine autonomously adjusts performance
parameters, maintains persistent state, and provides lightweight
observability endpoints.
"""

import json
import random
import time
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from paxect_selftune_plugin import Autotune

# Configuration
STATE_PATH = tempfile.gettempdir() + "/paxect_selftune_enterprise_state.json"
LOG_PATH = tempfile.gettempdir() + "/paxect_selftune_enterprise_log.jsonl"
PORT = 8090

# Initialize SelfTune engine
tuner = Autotune(state_path=STATE_PATH, log_path=LOG_PATH, mode="learn")
stats = {"ok": 0, "err": 0, "cycle": 0}


# Observability handler
class PAXECTHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/ping":
            self._send(200, {"status": "pong", "timestamp": int(time.time())})
        elif self.path == "/ready":
            self._send(200, {"ready": True})
        elif self.path == "/metrics":
            text = (
                f"paxect_selftune_ok {stats['ok']}\n"
                f"paxect_selftune_err {stats['err']}\n"
                f"paxect_selftune_epsilon {tuner.epsilon:.3f}\n"
            )
            self._send(200, text, ctype="text/plain")
        elif self.path == "/state":
            self._send(200, tuner._stats)
        else:
            self._send(404, {"error": "unknown endpoint"})

    def _send(self, code, data, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        if isinstance(data, str):
            self.wfile.write(data.encode())
        else:
            self.wfile.write(json.dumps(data).encode())

    def log_message(self, *args):
        return


# Start observability service in background
threading.Thread(
    target=lambda: HTTPServer(("127.0.0.1", PORT), PAXECTHandler).serve_forever(),
    daemon=True,
).start()

# Adaptive control loop
print("=== PAXECT SelfTune Enterprise Demo 01 – Stand-alone Adaptive Controller ===")
print(f"Observability available at http://127.0.0.1:{PORT}/[ping|ready|metrics|state]\n")

for i in range(1, 151):
    stats["cycle"] = i
    # Simulated workload
    bytes_processed = random.choice([32_000, 256_000, 2_000_000])
    exec_time = random.uniform(0.0001, 0.002)
    overhead = random.uniform(0.0001, 0.0008)

    result = tuner.tune(exec_time=exec_time, overhead=overhead, last_bytes=bytes_processed)

    success = not result["fail_safe"]
    stats["ok" if success else "err"] += 1

    print(
        f"[{i:03d}] label={result['label']:<9} "
        f"fail_safe={str(result['fail_safe']):<5} "
        f"throttle={result['throttle_percent']:>3}%  "
        f"epsilon={tuner.epsilon:.3f}"
    )
    time.sleep(0.05)

tuner._save_state()
print(f"\nDemo complete. State saved to: {STATE_PATH}")
print(f"Log written to: {LOG_PATH}")
print(f"Metrics endpoint: http://127.0.0.1:{PORT}/metrics")
