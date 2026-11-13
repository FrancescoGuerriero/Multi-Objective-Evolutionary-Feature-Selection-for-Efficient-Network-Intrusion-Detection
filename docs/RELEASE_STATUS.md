# EvoNIDS GitHub reproducibility and IDS integration status

Source snapshot combines earlier archived EvoNIDS research code, the archived coursework report and results, and a separately developed defensive Windows prototype. It does **not** contain the latest Windows-only fair-budget optimisation suite, NSGA-II implementation or trained final GA model. No claim of fully reproducing the five-seed outcomes from this archive is made until the canonical source is synchronized.

## Verified in the release build environment

- Research tests and prototype tests: passing
- Backend FastAPI endpoints: passing
- Synthetic Random Forest pipeline creation and schema-compatible replay/watch: passing
- Passive connection monitor: executes in this environment (Windows privileges/process visibility may differ)
- Flow watcher recorded 20 scored synthetic rows once, with distinct socket and CSV telemetry paths

## Not verified here

- True clean Windows fresh-venv PyPI installation, because this execution container has network resolution restrictions
- React production build, because npm packages are absent and cannot be installed from the network here
- Real Windows packet capture and UNSW-compatible flow extraction (not implemented)
- Full 300-budget experiments (latest canonical local files not available)

The dashboard is localhost-only by design. Socket data includes IP addresses, ports and process names and should not be exposed publicly without access controls. No firewall modifications or automated blocking are performed.
