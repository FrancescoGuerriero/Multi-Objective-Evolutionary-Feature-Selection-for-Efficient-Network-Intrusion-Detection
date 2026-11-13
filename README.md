# Multi-Objective Evolutionary Feature Selection for Efficient Network Intrusion Detection

COMP1818 Artificial Intelligence Applications coursework implementation and reproducibility package.

## Project objective

This project evaluates Genetic Algorithm (GA), Binary Particle Swarm Optimisation (BPSO), Particle Swarm Optimisation (PSO), and NSGA-II feature selection for binary network intrusion detection on UNSW-NB15. The primary objective is to reduce raw network-traffic dimensionality while maintaining predictive performance.

The final controlled comparison uses five seeds (`42, 101, 202, 303, 404`) and an equal budget of **300 unique expensive fitness evaluations per optimiser per seed**. Random Forest is used as the wrapper classifier. Full-feature Dummy, Logistic Regression, Random Forest, and XGBoost baselines are also evaluated.

## Main result

GA + Random Forest achieved the strongest feature-selection trade-off:

- Macro-F1: **0.865394 +/- 0.003952**
- Mean selected raw predictors: **10.2 / 42**
- Mean feature reduction: **75.71%**
- False-positive rate: **0.254795**
- Full-feature RF Macro-F1: **0.864225 +/- 0.000689**
- Full-feature XGBoost Macro-F1: **0.870417 +/- 0.000866** (highest absolute predictive result)

The correct interpretation is that GA provides the strongest accuracy-dimensionality trade-off; XGBoost remains the strongest absolute full-feature classifier.

## Repository layout

```text
.
|-- README.md
|-- requirements.txt
|-- pyproject.toml
|-- .gitignore
|-- report/
|   |-- COMP1818_EvoNIDS_Report.docx
|   `-- COMP1818_EvoNIDS_Report.pdf
|-- docs/
|   |-- EXPERIMENT_PROTOCOL.md
|   `-- REPRODUCTION.md
|-- research/
|   `-- README.md
|-- prototype/
|   |-- windows_ids.py
|   |-- model_io.py
|   |-- telemetry.py
|   |-- replay.py
|   |-- train_demo_model.py
|   |-- config/selected_features.json
|   `-- tests/
|-- results/
|   |-- final_summary.csv
|   |-- budget_effect.csv
|   |-- generalisation_gap.csv
|   `-- feature_consensus.csv
`-- tools/
    |-- package_existing_project.py
    `-- verify_submission.py
```

## Dataset

Dataset: **UNSW-NB15**

Official source: https://research.unsw.edu.au/projects/unsw-nb15-dataset

Expected local files for the full coursework experiments:

```text
data/raw/UNSW_NB15_training-set.csv
data/raw/UNSW_NB15_testing-set.csv
```

Binary target: `label`.

The identifier `id` and multiclass attack category `attack_cat` are excluded from the binary predictor set, leaving **42 raw predictors**.

The raw dataset is intentionally not bundled in this repository package. Download it from the official source and place the two CSV files under `data/raw/`.

## Python environment

The coursework experiments were developed with Python 3.12.

### Windows / Git Bash

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Tests

```bash
python -m pytest
```

For the curated submission package, verify the expected release structure with:

```bash
python tools/verify_submission.py
```

## Full experiment commands

The canonical local project contains the complete research implementation. After the repository is populated from that canonical project, the principal commands are:

### Full-feature baselines

```bash
python -m research.src.run_full_feature_baselines \
  --train data/raw/UNSW_NB15_training-set.csv \
  --test data/raw/UNSW_NB15_testing-set.csv \
  --seeds 42 101 202 303 404 \
  --output-dir results/full_feature_baselines
```

### Equal-budget GA / BPSO / PSO comparison

```bash
python -m research.src.run_fair_budget_suite \
  --train data/raw/UNSW_NB15_training-set.csv \
  --test data/raw/UNSW_NB15_testing-set.csv \
  --seeds 42 101 202 303 404 \
  --budget 300 \
  --population 8 \
  --search-train-size 20000 \
  --search-valid-size 8000 \
  --output-dir results/fair_budget_300
```

### NSGA-II

```bash
python -m research.src.run_nsga2_suite \
  --train data/raw/UNSW_NB15_training-set.csv \
  --test data/raw/UNSW_NB15_testing-set.csv \
  --seeds 42 101 202 303 404 \
  --budget 300 \
  --population 20 \
  --search-train-size 20000 \
  --search-valid-size 8000 \
  --output-dir results/nsga2_300
```

### Rebuild final analysis

```bash
python -m research.src.analyse_final_results
python -m research.src.statistical_analysis
python -m research.src.build_final_report_tables
```

## Windows IDS prototype

The `prototype/` directory provides a **passive, defensive Windows IDS prototype** with two roles:

1. `replay`: run a trained scikit-learn pipeline against UNSW-NB15-compatible CSV rows.
2. `monitor`: display passive local TCP/UDP connection telemetry obtained through `psutil` without blocking traffic or changing firewall rules.

The live Windows telemetry is deliberately separated from the coursework benchmark model because Windows socket telemetry does not natively provide all UNSW-NB15 engineered features. It is therefore a prototype integration layer, not a claim that the benchmark model can classify arbitrary live sockets without a compatible flow-feature extractor.

Run:

```bash
python -m prototype.windows_ids --help
python -m prototype.windows_ids monitor --interval 2
python -m prototype.windows_ids replay --csv path/to/unsw_compatible.csv --model models/ga_rf_pipeline.joblib
```

A synthetic demonstration model can be created only for smoke-testing the prototype wiring:

```bash
python -m prototype.train_demo_model --output models/demo_pipeline.joblib
```

Synthetic demo results are **not** coursework benchmark results.

## Reproducible submission build

From the canonical local project root, use:

```bash
python tools/package_existing_project.py --source . --destination ../COMP1818_EvoNIDS_Submission
```

The packager excludes machine-specific and unnecessary material such as `.venv`, caches, IDE metadata, Node modules, temporary logs, build output, and Python bytecode while preserving research source, tests, results, report material, prototype code, and reproducibility documentation.

See `docs/REPRODUCTION.md` for a clean-room verification procedure.

## Coursework delivery

The formal Moodle submission is the report PDF. The report should contain:

- a clearly labelled GitHub implementation link;
- the official UNSW-NB15 dataset link;
- enough detail for the teaching team to map the report claims to code and result files.

Do **not** upload the code archive to Moodle unless the teaching team explicitly requests it; keep the implementation available through the GitHub link used in the report.

## Academic integrity and AI use

The report includes the required 60-100 word reflection on generative-AI use. Experimental outputs are generated by the implemented Python pipeline; AI assistance is described as development, explanation, review, and writing support rather than as a source of experimental measurements.

## Streaming-compatible flow integration (new)

`watch-flows` reads **only newly completed rows** appended to a CSV by an independently configured network-flow exporter and passes them through a persisted, named-column scikit-learn pipeline. This is a *near-real-time input interface*, not an implementation of UNSW-NB15 packet-derived features. Its exact feature schema must match the model's expected `feature_names_in_`.

```bash
python -m prototype.train_demo_model
python -m prototype.windows_ids watch-flows \
  --csv results/demo_rows.csv \
  --model models/demo_pipeline.joblib \
  --iterations 1 \
  --output results/demo_alerts.jsonl
```

The default decision threshold is 0.5. Override with `--threshold 0.7`. The CSV exporter must append complete newline-terminated records without multiline quoted values; only completed records are scored. Replaying the synthetic model demonstrates connectivity only, not scientific intrusion detection performance. **Do not present this as live UNSW-NB15 classification from Windows sockets.** A production adapter still requires packet capture (e.g. consented Npcap), bidirectional session aggregation, and feature-by-feature compatibility validation; historical contextual counters cannot be invented from socket snapshots. There is no automatic blocking.

## Tutor reproducibility: source provenance / current limitations

This release includes the source from the earlier EvoNIDS Python/React project archives plus the Windows proof-of-integration, report, and derived summary tables. The **final** 300-budget optimisation suites, NSGA-II implementation and trained final GA-RF pipeline were produced on the original Windows development workstation and are **not present in the available archived sources**. Consequently the final reported Macro-F1 results are documented evidence, but their full-run reproduction is *not yet available* from this packaged snapshot. Before citing this repository as fully reproducible, merge the latest local `research/src` code and complete per-seed `results` folders, preserve one canonical project, and run the clean-room verification using the official dataset. Do not substitute the synthetic demo model for the trained final model.

To update the canonical GitHub repository from the actual workstation:

```bash
git remote -v
git remote add origin https://github.com/FrancescoGuerriero/Multi-Objective-Evolutionary-Feature-Selection-for-Efficient-Network-Intrusion-Detection.git  # only if origin does not exist
git status --short
git add README.md .gitignore pyproject.toml requirements.txt backend frontend prototype research docs tools results report
git diff --cached --stat
git commit -m "Add reproducible EvoNIDS research and Windows IDS prototype"
git push -u origin main
```

Verify before pushing that raw UNSW files, `.venv`, synthetic/trained model artifacts (unless explicitly approved for distribution), secrets and generated caches are not staged. The `report/` PDF should link to this **public** repository and the official dataset source before final Moodle submission.

## Integrated local React dashboard (FastAPI + Vite)

The dashboard separates **live passive Windows socket telemetry** from **ML-scored compatible CSV flows** and displays the stored five-seed research comparison. No live connection is classified as an attack using incomplete socket fields.

In terminal 1 (from the project root):

```bash
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

In terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dashboard polls the local API on port 8000 every five seconds and reads `results/alerts.jsonl` as its compatible-flow decision stream. In terminal 3, run the demo commands below; the synthetic demo must not be represented as real traffic classification:

```bash
python -m prototype.train_demo_model
python -m prototype.windows_ids watch-flows --csv results/demo_rows.csv --model models/demo_pipeline.joblib --iterations 1 --output results/alerts.jsonl
```

The API is intentionally designed for `127.0.0.1` only and exposes **read-only** routes: `/health`, `/api/project`, `/api/data/status`, `/api/ids/status`, `/api/ids/connections`, `/api/ids/alerts`, and `/api/research/comparison`. Do **not** bind it to all network interfaces without implementing authentication and access controls; exposed process names, IPs and local network connections are sensitive telemetry. This dashboard is an integration demonstration, not a production-certified IDS.
