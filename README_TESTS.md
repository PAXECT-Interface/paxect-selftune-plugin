
# PAXECT SelfTune Plugin — Test and Quality Validation

This document provides a detailed overview of the testing, coverage, and validation framework for the  
**PAXECT SelfTune 5-in-1 Hybrid Plugin**.

---

## 1. Overview

The SelfTune Plugin is validated through a comprehensive test suite designed to guarantee:
- Deterministic runtime and reproducible behavior  
- Stable adaptive control and safe failover under varying workloads  
- Cross-platform consistency (Linux, macOS, Windows)  
- Complete offline validation with zero external dependencies  

Testing and coverage are performed using:
- **pytest** for structured test execution  
- **coverage.py** for detailed coverage analysis  
- **NumPy** (optional) for computational benchmarks  

---

## 2. Repository Structure

```

paxect-selftune-plugin/
├── paxect_selftune_hybrid.py       # Core engine logic
├── tests/                          # Test suite
│   ├── test_autotune_fail_safe.py
│   ├── test_autotune_modes.py
│   ├── test_benchmarks.py
│   ├── test_buckets.py
│   ├── test_persistence_logging.py
│   ├── test_public_api.py
│   └── ...
├── coverage_run.sh                 # Script to execute coverage tests
├── pytest.ini                      # Pytest configuration
└── README_TESTS.md                 # This document

````

---

## 3. Environment Setup

```bash
# Clone the repository
git clone https://github.com/<your-org>/paxect-selftune-plugin.git
cd paxect-selftune-plugin

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
python3 -m pip install -r requirements.txt
````

Optional dependency (for advanced benchmarking):

```bash
python3 -m pip install numpy
```

---

## 4. Running Tests

To run the entire test suite with coverage:

```bash
./coverage_run.sh
```

or manually:

```bash
python3 -m coverage run -m pytest -v
python3 -m coverage report -m
```

This executes all core and auxiliary tests, including mode switching, persistence validation, and adaptive learning feedback.

---

## 5. Test Metrics

| Metric        | Result                |
| ------------- | --------------------- |
| Tests Passed  | 100% (13/13)          |
| Coverage      | 94%                   |
| Framework     | pytest + coverage.py  |
| Compatibility | Linux, macOS, Windows |
| Python        | 3.9 – 3.12            |

---

## 6. CI/CD Integration

The testing framework is fully CI-compatible and can be integrated with major automation platforms:

* **GitHub Actions:** Run `./coverage_run.sh` or define `make coverage` in your workflow.
* **GitLab CI:** Define a `pytest` stage for automated testing and reporting.
* **Jenkins / Bamboo:** Execute coverage runs inside isolated virtual environments.

Artifacts such as `.coverage` and `.pytest_cache/` are automatically excluded via `.gitignore`.

---

## 7. Test Modules

| Module                        | Description                                            |
| ----------------------------- | ------------------------------------------------------ |
| `test_autotune_fail_safe.py`  | Validates fail-safe throttling logic                   |
| `test_autotune_modes.py`      | Tests all operational modes and epsilon-decay learning |
| `test_benchmarks.py`          | Benchmarks matrix and I/O performance                  |
| `test_buckets.py`             | Validates bucket classification and sizing thresholds  |
| `test_persistence_logging.py` | Tests state persistence and JSON log integrity         |
| `test_public_api.py`          | Ensures API consistency and singleton behavior         |

---

## 8. Quality Principles

The SelfTune Plugin is developed and tested according to the following standards:

* **Reproducibility:** Identical behavior across runs and environments
* **Safety:** Controlled feedback loops with automatic failover
* **Isolation:** No external side-effects or data dependencies
* **Transparency:** Deterministic and fully inspectable runtime decisions

---

## 9. License

All test utilities and scripts are released under the same license as the core engine: **Apache 2.0**.
© 2025 PAXECT Systems. All rights reserved.

```



