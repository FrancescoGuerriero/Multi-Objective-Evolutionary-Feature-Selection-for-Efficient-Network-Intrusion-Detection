# EvoNIDS implementation phases

## Phase 1 — Windows scaffold
Status: COMPLETE

- Python 3.12 environment
- FastAPI
- React/TypeScript/Vite
- baseline ML infrastructure
- GA/BPSO core
- tests

## Phase 2 — UNSW-NB15 validation and baselines
Status: IN PROGRESS

- preserve official UNSW train/test split
- create validation split only from training data
- binary target leakage controls
- multiclass target leakage controls
- dataset schema inspector
- baseline Logistic Regression
- baseline Random Forest
- baseline XGBoost
- five-seed result summaries

## Phase 3 — GA feature selection
- lock classifier used inside wrapper fitness
- parameter study
- equal evaluation budget
- five repeated seeds

## Phase 4 — BPSO feature selection
- inertia / c1 / c2 experiments
- equal evaluation budget
- five repeated seeds

## Phase 5 — PSO comparison
- define defensible feature-selection encoding
- same evaluation budget
- five repeated seeds

## Phase 6 — NSGA-II multi-objective extension
- maximise Macro-F1
- minimise feature count
- optional inference-cost objective
- Pareto front
- repeated runs / stability

## Phase 7 — final evaluation
- untouched official test partition
- final full-feature vs GA vs BPSO vs PSO vs NSGA-II comparison
- uncertainty and computational-cost analysis

## Phase 8 — real IDS prototype
- Windows flow/PCAP adapter
- trained model inference
- FastAPI alerts
- PostgreSQL
- React dashboard

## Phase 9 — coursework evidence
- figures/tables
- reproducibility manifest
- paper comparison
- critical discussion
