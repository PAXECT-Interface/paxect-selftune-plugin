


# Contributing Guidelines

Welcome, and thank you for your interest in contributing to **PAXECT SelfTune**!
Your effort helps keep the project deterministic, reproducible, and cross-platform across all major operating systems.

---

## Overview

**PAXECT SelfTune** is part of the broader **PAXECT Interface** ecosystem.
All contributions must remain **deterministic**, **platform-agnostic**, and **dependency-light** —
no AI, telemetry, or random behavior is allowed.

SelfTune focuses on **runtime control**, **adaptive overhead regulation**, and **deterministic performance tuning**.
Every contribution must preserve bit-identical outputs across all runs and platforms.

---

## Development Setup

1. **Fork** this repository to your own GitHub account.

2. **Clone** your fork locally:

   ```bash
   git clone https://github.com/PAXECT-Interface/paxect-selftune-plugin.git
   cd paxect-selftune-plugin
   ```

3. **Create a virtual environment** (recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Verify deterministic behavior** before making changes:

   ```bash
   python demos/selftune_enterprise_demo_01_standalone.py
   python demos/selftune_enterprise_demo_02_safety_throttle.py
   python demos/selftune_enterprise_demo_03_adaptive_benchmark.py
   python demos/selftune_enterprise_demo_04_metrics_server.py
   ```

> 🧩 Each demo must complete without drift or deviation between runs —
> investigate any inconsistent metrics before submitting code.

---

## Contribution Rules

* Keep commits focused and clear.
  Example:
  `fix: stabilize throttle timing on Windows` or
  `feat: add deterministic smoothing interval`.
* All files must include SPDX headers:

  ```python
  # SPDX-FileCopyrightText: © 2025 PAXECT
  # SPDX-License-Identifier: Apache-2.0
  ```
* Test on **at least two operating systems** (Linux + Windows/macOS).
* Avoid adding randomness, pseudo-AI logic, or heuristic parameters.
* All pull requests must pass **CI + CodeQL** validation.

---

## Pull Request Workflow

1. Create a new feature branch:

   ```bash
   git checkout -b feature/your-change
   ```
2. Push your changes:

   ```bash
   git push origin feature/your-change
   ```
3. Open a **Pull Request** describing the goal and rationale.
4. Maintainers will review determinism, platform parity, and structure.
5. Once approved, your PR will be merged and scheduled for the next release.

> ✨ The goal: measurable, deterministic progress — not arbitrary speed.

---

## Communication

* **Issues:** for bug reports, enhancement ideas, and reproducibility concerns
* **Discussions:** for architecture or policy refinement
* **Security:** please see [SECURITY.md](./SECURITY.md) for responsible disclosure

---

## Thank You 💛

Every contribution helps make **PAXECT SelfTune** a stronger, fairer, and more predictable component in the PAXECT ecosystem.
Your technical precision and time are deeply appreciated.

> Together we keep PAXECT deterministic, safe, and reproducible — across all environments.

---



