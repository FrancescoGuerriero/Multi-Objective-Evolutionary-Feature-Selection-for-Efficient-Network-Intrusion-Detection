# EvoNIDS implementation and validation status

## Research: completed on canonical Windows workstation (results recorded)

- UNSW-NB15 binary classification with leakage controls and official held-out testing
- Full-feature Dummy, Logistic Regression, Random Forest and XGBoost baselines
- GA/BPSO/PSO, five seeds, 300 unique expensive evaluations each
- NSGA-II, five seeds, validation-only representative selection and Pareto analysis
- Feature stability, budget sensitivity, generalisation gaps and nonparametric comparisons
- Final report, four main pages + references

**Source-provenance gate:** the present repository includes earlier archived GA/BPSO/PSO modules but the latest fair-budget, NSGA-II and final-analysis scripts/results exist only on the Windows workstation. Synchronise those before claiming complete independent reproduction.

## Windows IDS integration: proof-of-integration implemented

- Read-only local TCP/UDP socket snapshots and associated process names
- Offline CSV replay with schema-checked saved scikit-learn pipeline
- Append-only compatible-flow CSV scoring with JSONL decision output
- Localhost FastAPI monitor/status/alerts/benchmark endpoints
- React/TypeScript dashboard presenting socket telemetry and model-scored flow events separately
- Python tests for the integration

**Not implemented:** packet-to-UNSW engineered feature parity, Windows Npcap flow extractor, deployment-grade model export, Windows-native end-to-end frontend build verification, authentication for remote hosting, persistence beyond JSONL, blocking or automated mitigation. These are deliberately excluded from the claimed assessment results.

## Before tutor demonstration

1. Copy missing latest optimisation source, model-export utility and full per-seed outputs from canonical Windows repository.
2. Re-run the README commands and clean-environment tests on Windows Python 3.12.
3. Install React dependencies, run `npm run build`, launch the API on localhost and check the dashboard.
4. Check that the four-page report PDF links to the public repo and official UNSW dataset source.
5. Confirm GitHub visibility without sign-in and Moodle PDF format/page count.
