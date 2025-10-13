# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
"""
PAXECT SelfTune 5-in-1 Plugin — Production Hardened (Cross-Platform, NumPy Integrated)

Works on Linux / Windows / macOS / FreeBSD / OpenBSD / Android / iOS.
- Modes: off | auto | learn | manual | short_run
- Per bucket (small / medium / large): self-learning EMA per profile
- Adaptive epsilon-greedy (explore / exploit decay)
- Persistent state (JSON) with OS-neutral fallback via tempfile.gettempdir()
- Fail-safe throttle when average overhead > 75%
- Time-based throttle: every 5 min (50%), every 30 min (25%)
- Manual cooldown API
- Logging: console + .jsonl file (UTC)
- Matrix benchmarking via NumPy (real, deterministic performance test)
- Public API: Autotune, tune(), report(), get_logs(), get_autotune(), matrix_benchmark()
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import json, os, time, random, pathlib, tempfile
from math import inf
from datetime import datetime, timezone, timedelta

# 🔹 NEW: NumPy for deterministic matrix benchmarking
import numpy as np

# ---------------- Buckets & Profiles ----------------

BUCKET_SMALL_TH = 128 * 1024          # <128KB -> small
BUCKET_MEDIUM_TH = 4 * 1024 * 1024    # 128KB..4MB -> medium; >=4MB -> large
PROFILES = ("baseline", "compress", "parallel")

def bucket_of(n: int) -> str:
    if n >= BUCKET_MEDIUM_TH:
        return "large"
    if n >= BUCKET_SMALL_TH:
        return "medium"
    return "small"

def default_blocksize(bucket: str) -> int:
    return {"small": 8192, "medium": 16384, "large": 32768}[bucket]

def utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# -------------- Cross-platform default paths --------------

def default_state_path() -> pathlib.Path:
    p = os.getenv("AUTOTUNE_STATE_PATH")
    if p:
        return pathlib.Path(os.path.expanduser(p))
    home = pathlib.Path(os.path.expanduser("~"))
    cache = home / ".cache"
    try:
        cache.mkdir(parents=True, exist_ok=True)
        return cache / "autotune_state.json"
    except Exception:
        # OS-neutral fallback
        return pathlib.Path(tempfile.gettempdir()) / "autotune_state.json"

def default_log_path() -> pathlib.Path:
    p = os.getenv("AUTOTUNE_LOG_PATH")
    if p:
        return pathlib.Path(os.path.expanduser(p))
    home = pathlib.Path(os.path.expanduser("~"))
    cache = home / ".cache"
    try:
        cache.mkdir(parents=True, exist_ok=True)
        return cache / "autotune_log.jsonl"
    except Exception:
        # OS-neutral fallback
        return pathlib.Path(tempfile.gettempdir()) / "autotune_log.jsonl"

# ---------------------- NumPy Benchmark ----------------------

def matrix_benchmark(n: int = 256) -> float:
    """
    Perform a deterministic NumPy-based matrix multiplication benchmark.
    Returns the elapsed time in seconds.
    """
    np.random.seed(42)
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)
    start = time.time()
    np.dot(A, B)
    return round(time.time() - start, 6)

# ---------------------- Core ----------------------

@dataclass
class Autotune:
    mode: str = "learn"               # "off" | "auto" | "learn" | "manual" | "short_run"
    epsilon: float = 0.20
    epsilon_min: float = 0.02
    epsilon_decay: float = 0.995
    ema_alpha: float = 0.30
    max_history: int = 1000
    max_overhead_ratio: float = 0.75
    overhead_window: int = 3
    save_interval: int = 25
    state_path: Optional[str] = None
    log_path: Optional[str] = None
    log_to_file: bool = True

    _stats: Dict[str, Dict[str, Dict[str, float]]] = field(default_factory=dict)
    _best: Dict[str, str] = field(default_factory=dict)
    _history: List[Dict[str, Any]] = field(default_factory=list)
    _step: int = 0
    _last_choice: Optional[Dict[str, str]] = None
    _overhead_hist: List[float] = field(default_factory=list)
    _logfile: Optional[pathlib.Path] = None
    _current_percent: int = 100
    _throttle_until: Optional[datetime] = None
    _next_5m: Optional[datetime] = None
    _next_30m: Optional[datetime] = None
    _manual_throttle: Optional[Dict[str, Any]] = None
    _short_run_triggered: bool = False

    def __post_init__(self):
        self.mode = (self.mode or "off").lower()
        self.state_path = str(default_state_path()) if not self.state_path else self.state_path
        self.log_path = str(default_log_path()) if not self.log_path else self.log_path
        self._logfile = pathlib.Path(self.log_path) if self.log_to_file else None

        # Load persisted state if available
        if self.state_path and os.path.isfile(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._stats   = data.get("stats", {})
                self._best    = data.get("best", {})
                hist = data.get("history", [])
                self._history = hist if isinstance(hist, list) else []
                self._step    = int(data.get("step", 0))
                self.epsilon  = float(data.get("epsilon", self.epsilon))
            except Exception:
                self._stats, self._best, self._history, self._step = {}, {}, [], 0

        # Ensure buckets/profiles
        for b in ("small", "medium", "large"):
            self._stats.setdefault(b, {})
            for p in PROFILES:
                self._stats[b].setdefault(p, {"ema": inf, "count": 0.0})
            self._best.setdefault(b, "baseline")

        now = datetime.utcnow()
        self._next_5m = now + timedelta(minutes=5)
        self._next_30m = now + timedelta(minutes=30)

    def tune(self, *, exec_time: float, overhead: float, last_bytes: int,
             runtime_minutes: Optional[int] = None) -> Dict[str, Any]:
        b = bucket_of(int(last_bytes))
        overhead_ratio = float(overhead) / max(1e-6, exec_time + overhead)
        self._overhead_hist.append(overhead_ratio)
        if len(self._overhead_hist) > self.overhead_window:
            self._overhead_hist = self._overhead_hist[-self.overhead_window:]
        avg_overhead = sum(self._overhead_hist) / len(self._overhead_hist)
        fail_safe = avg_overhead >= self.max_overhead_ratio
        now = datetime.utcnow()

        # Short run mode (forced cooldowns)
        if self.mode == "short_run" and not self._short_run_triggered:
            if runtime_minutes is not None:
                if runtime_minutes < 5:
                    self.manual_cooldown(50, 60)
                elif runtime_minutes < 30:
                    self.manual_cooldown(25, 60)
            self._short_run_triggered = True

        # Manual mode
        if self.mode == "manual" and self._manual_throttle:
            until = self._manual_throttle['until_time']
            percent = self._manual_throttle['percent']
            if now < until:
                self._current_percent = percent
                self._throttle_until = until
            else:
                self._manual_throttle = None
                self._current_percent = 100
                self._throttle_until = None

        # Automatic throttling rules
        if fail_safe:
            self._current_percent = 25
            self._throttle_until = now + timedelta(seconds=60)
        elif self._next_30m and now >= self._next_30m:
            self._current_percent = 25
            self._throttle_until = now + timedelta(seconds=60)
            self._next_30m = now + timedelta(minutes=30)
        elif self._next_5m and now >= self._next_5m:
            if self._current_percent != 25:
                self._current_percent = 50
                self._throttle_until = now + timedelta(seconds=60)
            self._next_5m = now + timedelta(minutes=5)
        elif self._throttle_until and now >= self._throttle_until:
            self._current_percent = 100
            self._throttle_until = None

        # Learning feedback
        if self.mode == "learn" and exec_time and self._last_choice:
            self._apply_feedback(exec_time)

        # Decide profile
        if self.mode == "off" or fail_safe:
            label = "baseline"
        elif self.mode == "auto":
            label = {"small": "baseline", "medium": "compress", "large": "parallel"}[b]
        else:
            label = self._choose_label(b)

        self._last_choice = {"bucket": b, "label": label}
        decision = self._profile_cfg(label, b, self.mode)
        self._step += 1
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        # Optional: NumPy benchmark integration
        benchmark_time = matrix_benchmark(128)

        # History + periodic state save
        self._history.append({
            "t": time.time(),
            "bucket": b,
            "label": label,
            "exec_time": exec_time,
            "overhead": overhead,
            "avg_overhead": avg_overhead,
            "fail_safe": fail_safe,
            "throttle_percent": self._current_percent,
            "benchmark_time": benchmark_time,
            "utc": utc_now_str()
        })
        if len(self._history) > self.max_history:
            self._history = self._history[-self.max_history:]
        if self.state_path and (self._step % self.save_interval == 0):
            self._save_state()

        self._log_decision(decision, exec_time, overhead, avg_overhead, fail_safe, self._current_percent)
        decision.update({
            "fail_safe": fail_safe,
            "throttle_percent": self._current_percent,
            "benchmark_time": benchmark_time
        })
        return decision

    def manual_cooldown(self, percent: int, duration_secs: int):
        now = datetime.utcnow()
        self._manual_throttle = {
            "percent": percent,
            "until_time": now + timedelta(seconds=duration_secs)
        }
        self._current_percent = percent
        self._throttle_until = self._manual_throttle["until_time"]

    def report(self, n_bytes: int, exec_time: float, overhead: float = 0.0):
        if self.mode != "learn" or not self._last_choice:
            return
        self._apply_feedback(exec_time)

    def get_logs(self, max_entries: int = 100) -> List[Dict[str, Any]]:
        logs = self._history[-max_entries:]
        if self.log_to_file and self._logfile and self._logfile.exists():
            try:
                with open(self._logfile, "r", encoding="utf-8") as f:
                    file_logs = [json.loads(line) for line in f.readlines()]
                logs = file_logs[-max_entries:]
            except Exception:
                pass
        return logs

    def _apply_feedback(self, exec_time: float):
        b = self._last_choice["bucket"]
        p = self._last_choice["label"]
        rec = self._stats[b][p]
        if rec["count"] <= 0:
            rec["ema"] = exec_time
        else:
            rec["ema"] = self.ema_alpha * exec_time + (1.0 - self.ema_alpha) * rec["ema"]
        rec["count"] += 1.0
        self._best[b] = min(self._stats[b].items(), key=lambda kv: kv[1]["ema"])[0]

    def _choose_label(self, b: str) -> str:
        if random.random() < self.epsilon:
            return random.choice(PROFILES)
        stats_b = self._stats[b]
        if not any(v["count"] > 0 for v in stats_b.values()):
            return "baseline"
        return min(stats_b.items(), key=lambda kv: kv[1]["ema"])[0]

    def _profile_cfg(self, label: str, bucket: str, policy: str) -> Dict[str, Any]:
        cfg = {"blocksize": default_blocksize(bucket), "parallel": False, "compress": False}
        if label == "compress":
            cfg["compress"] = True
        elif label == "parallel":
            cfg["parallel"] = True
        return {"label": label, "policy": policy, **cfg}

    def _save_state(self):
        try:
            data = {
                "stats": self._stats,
                "best": self._best,
                "history": self._history,
                "step": self._step,
                "epsilon": self.epsilon,
                "version": "prod-1.3.3-numpy",
            }
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _log_decision(self, decision: Dict[str, Any], exec_time: float, overhead: float,
                      avg_overhead: float, fail_safe: bool, throttle_percent: int):
        log_entry = {
            "datetime_utc": utc_now_str(),
            "decision": decision,
            "exec_time": exec_time,
            "overhead": overhead,
            "avg_overhead": avg_overhead,
            "fail_safe": fail_safe,
            "throttle_percent": throttle_percent,
        }
        print(f"[SelfTune] {log_entry}")
        if self.log_to_file and self._logfile:
            try:
                with open(self._logfile, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception:
                pass

# -------- Module-level singleton & public API --------

_singleton: Optional[Autotune] = None

def get_autotune(mode: Optional[str] = None) -> Autotune:
    global _singleton
    if _singleton is None:
        _singleton = Autotune()
    if mode is not None:
        _singleton.mode = mode
    return _singleton

def tune(exec_time: float, overhead: float, last_bytes: int,
         runtime_minutes: Optional[int] = None) -> Dict[str, Any]:
    return get_autotune().tune(exec_time=exec_time, overhead=overhead,
                               last_bytes=last_bytes, runtime_minutes=runtime_minutes)

def report(n_bytes: int, exec_time: float, overhead: float = 0.0) -> None:
    return get_autotune().report(n_bytes, exec_time, overhead)

def get_logs(max_entries: int = 100) -> List[Dict[str, Any]]:
    return get_autotune().get_logs(max_entries)

# ✅ NEW: Public access to matrix benchmark
def run_matrix_benchmark(n: int = 256) -> float:
    return matrix_benchmark(n)
