#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# PAXECT Core Complete — Demo 04: Health & Metrics (zero-touch)
# Stack: Core + SelfTune + Link + AEAD + Polyglot (observability surface)
# Endpoints: /ping  /ready  /metrics  /last
# Notes: English-only messages, ASCII-safe output, no external dependencies.

import os
import json
import time
import socket
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
from pathlib import Path

# Config
PORT = int(os.environ.get("PAXECT_PORT", "8080"))
LOG_PATH = Path(tempfile.gettempdir()) / "paxect_health_metrics.jsonl"

# Optional: read recent counters from existing logs if present
ROOT = Path(__file__).resolve().parent.parent
SELF_LOG = ROOT / "paxect_log.jsonl"        # SelfTune decisions
LINK_LOG = ROOT / "paxect_link_log.jsonl"   # Link relay events

STATE = {
    "started_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    "ready": True,
    "requests": 0,
    "last_ok": None,
    "selftune_entries": 0,
    "link_relay_count": 0,
}

def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def log_event(level: str, msg: str, data: dict | None = None):
    entry = {"ts": now_utc(), "level": level, "msg": msg, "data": data or {}}
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex((host, port)) == 0

def maybe_refresh_counters():
    # Best-effort scan of last ~500 lines to estimate counters
    if SELF_LOG.exists():
        try:
            lines = SELF_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()[-500:]
            cnt = 0
            for ln in lines:
                try:
                    obj = json.loads(ln)
                    if isinstance(obj, dict) and "decision" in obj:
                        cnt += 1
                except Exception:
                    pass
            STATE["selftune_entries"] = cnt
        except Exception:
            pass
    if LINK_LOG.exists():
        try:
            lines = LINK_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()[-500:]
            cnt = 0
            for ln in lines:
                try:
                    obj = json.loads(ln)
                    ev = str(obj.get("event", "")).lower()
                    if ev.startswith("relay"):
                        cnt += 1
                except Exception:
                    pass
            STATE["link_relay_count"] = cnt
        except Exception:
            pass

class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload, content_type="application/json"):
        body = payload if isinstance(payload, (str, bytes)) else json.dumps(payload)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        STATE["requests"] += 1
        if self.path == "/ping":
            STATE["last_ok"] = "ping"
            self._send(200, {"ok": True, "ts": now_utc()})
            log_event("INFO", "ping")
        elif self.path == "/ready":
            self._send(200, {"ready": bool(STATE["ready"])})
            log_event("INFO", "ready", {"ready": STATE["ready"]})
        elif self.path == "/metrics":
            maybe_refresh_counters()
            payload = {
                "uptime_s": round(time.time() - START_TS, 3),
                "requests": STATE["requests"],
                "selftune_entries": STATE["selftune_entries"],
                "link_relay_count": STATE["link_relay_count"],
            }
            self._send(200, payload)
            log_event("INFO", "metrics", payload)
        elif self.path == "/last":
            self._send(200, {"last": STATE["last_ok"]})
            log_event("INFO", "last", {"last": STATE["last_ok"]})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *_args):
        # keep stdout clean (no default access logs)
        return

def run():
    global START_TS
    START_TS = time.time()

    # Clean previous log to keep demo output tidy
    if LOG_PATH.exists():
        try:
            LOG_PATH.unlink()
        except Exception:
            pass

    # Friendly port check
    if port_in_use("127.0.0.1", PORT):
        msg = (
            f"Port {PORT} already in use. "
            f"Start with a different port: PAXECT_PORT=8090 python demos/complete_demo_04_health_metrics.py"
        )
        print(msg)
        log_event("ERROR", "port_in_use", {"port": PORT})
        return

    log_event("INFO", "server_start", {"port": PORT})
    httpd = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"== PAXECT Health Server on http://127.0.0.1:{PORT} ==")
    print("Endpoints: /ping  /ready  /metrics  /last   (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    log_event("INFO", "server_stop", {"uptime_s": round(time.time() - START_TS, 3)})

if __name__ == "__main__":
    run()
