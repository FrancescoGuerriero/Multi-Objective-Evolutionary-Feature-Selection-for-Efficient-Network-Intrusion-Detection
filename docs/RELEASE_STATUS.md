# Release verification

* GitHub repository: public; full canonical code synchronization pending.
* Archived research source available from previous EvoNIDS archives: preprocessing, GA/BPSO/PSO baseline components, backend and React scaffold.
* Final 300-budget search scripts and NSGA-II source: not in the archived snapshot; remain on the developer's Windows workstation.
* Local release package smoke test: 14 Python tests passed; synthetic trained model generated; 20 compatible CSV flow rows scored via append-only watcher; passive socket monitor completed one snapshot.
* Live alerting requires externally generated **feature-compatible** flow CSVs and a trained production-model export. No packet-sniffing or firewall blocking has been claimed.
* Official UNSW-NB15 dataset must be obtained from the source link in README.
* 4-page PDF should be updated to link to the public repository before final Moodle submission.

**Reproducibility gate:** upload full canonical source, verify dependency installation on clean Windows Python 3.12, run the published test suite, and compare regenerated per-seed CSV/JSON outputs with reported summaries.
