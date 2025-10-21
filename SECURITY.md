<p align="center">
  <img src="ChatGPT%20Image%202%20okt%202025,%2022_33_51.png" alt="PAXECT logo" width="200"/>
</p>

# Security Policy — PAXECT SelfTune Plugin

## Supported Versions

Only the latest **main branch** and tagged releases are actively supported and reviewed for security issues.  
Older versions are provided as-is without any security guarantee.

| Version | Supported |
|----------|------------|
| main     | ✅ |
| 1.x      | ⚠️ Limited (best effort) |

---

## Reporting a Vulnerability

If you discover a potential vulnerability, please report it **privately**.

- Email: **PAXECT-Team@outlook.com** (preferred)  
- GitHub: use the “Private vulnerability report” option under *Security → Advisories*  
- Do **not** create public issues or pull requests for unresolved vulnerabilities.

---

## Disclosure Process

1. Reports are acknowledged within **72 hours**.  
2. A maintainer will contact you for technical details and reproduction steps.  
3. A fix or mitigation will be prepared and reviewed privately.  
4. Once resolved, a public advisory and changelog entry will be published.  
5. Researchers may be credited (if they wish) after coordinated disclosure.

---

## Security Guidelines

- Follow responsible disclosure practices.  
- Do not perform unauthorized testing on live systems.  
- Avoid denial-of-service, spam, or social engineering tests.  
- Respect privacy and data ownership at all times.  
- For deterministic safety tests, use offline or sandbox environments only.

---

## Scope

Security review applies to:
- **paxect_selftune_plugin.py** — runtime control engine  
- **demo suite (01–07)** — safe demonstration modules  
- **integration hooks** used by CI/CD or external controllers  

External tools or libraries (e.g., NumPy) are covered only under their own licenses.

---

## Contact

For any responsible disclosure or security questions:

📧 **PAXECT-Team@outlook.com**

All reports are handled confidentially and fairly by the maintainers.

---

© 2025 **PAXECT Systems** — Secure deterministic runtime control for modern enterprise workloads.


