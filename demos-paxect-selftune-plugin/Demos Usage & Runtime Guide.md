
---

## 🧩 Demos – PAXECT SelfTune Plugin

Each demo is self-contained, plug-and-play, and runs cross-platform (Linux / macOS / Windows / BSD / Android / iOS).
All demos use local JSON state/logs under `/tmp` or `tempfile.gettempdir()`.
No internet connection or external libraries are required.

---

### ⚙️ Installation (before running demos)

```bash
# Optional: create an isolated virtual environment
python3 -m venv venv
source venv/bin/activate          # on Linux/macOS
# venv\Scripts\activate.bat       # on Windows

# Install numpy only if you want real matrix benchmarks (optional)
pip install numpy
```

> 🧠  NumPy is **optional** — the plugin automatically falls back to a deterministic simulation if it’s missing.

---

### ▶️ Demo 01 – Quick Start Adaptive Loop

**File:** `selftune_enterprise_demo_01_quick_start.py`
**Duration:** ~15 seconds
**What it shows:**

* Runs 150 learning cycles.
* Demonstrates adaptive epsilon decay, automatic profile selection, and baseline → parallel transitions.
* Writes persistent state to `/tmp/paxect_selftune_enterprise_state.json`.

**Run:**

```bash
python3 selftune_enterprise_demo_01_quick_start.py
```

---

### ▶️ Demo 02 – Safety & Throttle Simulation

**File:** `selftune_enterprise_demo_02_throttle_safety.py`
**Duration:** ~20 seconds
**What it shows:**

* Simulates rapid calls to trigger throttling.
* Prints allowed vs throttled operations.
* Demonstrates automatic short-run and long-run cooldown recovery.

**Run:**

```bash
python3 selftune_enterprise_demo_02_throttle_safety.py
```

---

### ▶️ Demo 03 – Adaptive Benchmark Mode

**File:** `selftune_enterprise_demo_03_adaptive_benchmark.py`
**Duration:** ~30 seconds (with NumPy)
**What it shows:**

* Measures matrix and I/O times per cycle.
* Shows how the tuner adjusts between profiles (“parallel”, “compress”, “baseline”).
* Demonstrates fail-safe trigger and recovery under heavy load.

**Run:**

```bash
python3 selftune_enterprise_demo_03_adaptive_benchmark.py
```

---

### ▶️ Demo 04 – Metrics & Observability Server

**File:** `selftune_enterprise_demo_04_metrics_server.py`
**Duration:** runs until stopped (`Ctrl+C`)
**What it shows:**

* Starts a lightweight HTTP server with endpoints:

  * `/ping` → health
  * `/ready` → readiness
  * `/metrics` → Prometheus-style metrics
  * `/last` → last tuner decision
* Used by automated tests and dashboards.

**Run:**

```bash
python3 selftune_enterprise_demo_04_metrics_server.py
```

---

### ▶️ Demo 05 – Smoke & Fault Verification

**File:** `selftune_enterprise_demo_05_smoke_verification.py`
**Duration:** ~2 minutes
**What it shows:**

* Stress test with deliberate micro-faults and recoveries.
* Verifies throttling, fail-safe logic, and recovery time (auto baseline mode).
* Generates a final JSON report at `/tmp/paxect_selftune_smoke_report.json`.

**Run:**

```bash
python3 selftune_enterprise_demo_05_smoke_verification.py
```

---

### 📊 Logs & Output

All demos automatically store:

* State: `/tmp/paxect_selftune_*.json`
* Logs:  `/tmp/paxect_selftune_*.jsonl`
* Reports: `/tmp/paxect_selftune_smoke_report.json`

You can tail them live:

```bash
tail -f /tmp/paxect_selftune_enterprise_log.jsonl
```

---

### ✅ Tips

| Use case                   | Recommended demo |
| -------------------------- | ---------------- |
| Quick visual check         | Demo 01          |
| Safety/throttle proof      | Demo 02          |
| Real benchmark (NumPy)     | Demo 03          |
| Dashboard / metrics        | Demo 04          |
| Fault injection + recovery | Demo 05          |


