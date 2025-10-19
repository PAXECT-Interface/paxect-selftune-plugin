#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
PAXECT SelfTune Plugin — Demo 04 (Metrics & Observability, timed)
-----------------------------------------------------------------
Starts a small observability server with /ping, /ready, /metrics,
and /throttle endpoints. Auto-stops after 5 minutes.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading, json, time, random, tempfile, os, sys
from paxect_selftune_plugin import Autotune

HOST, PORT = "127.0.0.1", 8091
STATE_PATH = os.path.join(tempfile.gettempdir(), "paxect_selftune_metrics_state.json")
LOG_PATH = os.path.join(tempfile.gettempdir(), "paxect_selftune_metrics_log.jsonl")

tuner = Autotune(state_path=STATE_PATH, log_path=LOG_PATH, mode="learn")
STOP_AFTER_SECONDS = 300  # 5 minutes

class SelfTuneMetricsHandler(BaseHTTPRequestHandler):
    def _send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text):
        body = text.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        now = int(time.time())
        if self.path == "/ping":
            self._send_json({"status": "pong", "ts": now})
        elif self.path == "/ready":
            self._send_json({"ready": True})
        elif self.path == "/throttle":
            self._send_json({
                "throttle_percent": tuner._current_percent,
                "epsilon": tuner.epsilon,
                "fail_safe": any(h > tuner.max_overhead_ratio for h in tuner._overhead_hist[-3:])
            })
        elif self.path == "/metrics":
            fail_safe = any(h > tuner.max_overhead_ratio for h in tuner._overhead_hist[-3:])
            metrics = [
                "# HELP paxect_selftune_throttle_percent Current throttle percent",
                "# TYPE paxect_selftune_throttle_percent gauge",
                f"paxect_selftune_throttle_percent {tuner._current_percent}",
                "# HELP paxect_selftune_fail_safe_active Fail-safe active flag",
                "# TYPE paxect_selftune_fail_safe_active gauge",
                f"paxect_selftune_fail_safe_active {1 if fail_safe else 0}",
                "# HELP paxect_selftune_epsilon Epsilon exploration factor",
                "# TYPE paxect_selftune_epsilon gauge",
                f"paxect_selftune_epsilon {tuner.epsilon}",
            ]
            self._send_text("\n".join(metrics))
        else:
            self.send_error(404, "Endpoint not found")

def background_tune(stop_time):
    while time.time() < stop_time:
        exec_time = random.uniform(0.0002, 0.0020)
        overhead = random.uniform(0.0001, 0.0008)
        tuner.tune(exec_time=exec_time, overhead=overhead, last_bytes=128000)
        time.sleep(0.25)

if __name__ == "__main__":
    print("=== PAXECT SelfTune Enterprise Demo 04 (Timed) ===")
    print(f"Serving metrics on http://{HOST}:{PORT}/metrics")
    print(f"Auto-stop after {STOP_AFTER_SECONDS/60:.1f} minutes\n")

    stop_time = time.time() + STOP_AFTER_SECONDS
    threading.Thread(target=background_tune, args=(stop_time,), daemon=True).start()

    server = HTTPServer((HOST, PORT), SelfTuneMetricsHandler)
    server.timeout = 2

    try:
        while time.time() < stop_time:
            server.handle_request()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n[Shutdown] Demo stopped after time limit.")
        sys.exit(0)
