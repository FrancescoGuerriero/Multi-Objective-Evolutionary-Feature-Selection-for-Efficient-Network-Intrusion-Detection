# Canonical source upload audit — 13 November 2026

## Uploaded archive reviewed

`COMP1818_EvoNIDS_with_React.zip` supplied in conversation contained **51 ZIP entries (including directories), ~278 KB uncompressed** under `COMP1818_EvoNIDS_Submission/`. This is the earlier *submission support package*, not the complete canonical Windows research project.

The package contains a four-page report and its DOCX source, a previous standalone React/Vite dashboard, passive socket telemetry, synthetic demo-model replay, four aggregate summary CSVs and source-copying utilities.

**Do not overwrite the newer GitHub React/FastAPI integration with the older standalone prototype:** the repository already contains a working one-origin dashboard, a PowerShell launcher, modernised API and CI integration checks.

## Test performed on uploaded package

From the extracted package root, `python -m pytest -q prototype/tests`: **2 passed**.

After removing test-generated caches, `python tools/verify_submission.py`: **PASS**.

These checks establish the basic prototype and archive layout only. They **do not** verify reproduction of the final five-seed research claims.

## Source still absent from supplied archive and current GitHub repository

- `research/src/run_fair_budget_suite.py` and the complete 300-unique-evaluation GA/BPSO/PSO runners.
- `research/src/run_nsga2_suite.py` and NSGA-II/Pareto archive implementation.
- `research/src/run_full_feature_baselines.py`.
- `research/src/analyse_final_results.py`, `statistical_analysis.py`, `build_final_report_tables.py`.
- `research/src/evaluate_feature_subset.py` and `research/src/utils/evaluation_budget.py`.
- `results/fair_budget_300/`, `results/nsga2_300/`, `results/full_feature_baselines/`, `results/final_analysis/`, `results/final_report_tables/` and the statistical-analysis evidence.

The aggregate values in `results/final_summary.csv` are *reported* five-seed experimental results; they cannot currently be recalculated from the uploaded repository alone.

## Complete the single canonical Windows project

Retain the existing project root:
`C:\Users\Francesco\EvoNIDS_COMP1818_Phase1\EvoNIDS_COMP1818`.

Upload those exact files and results from the **canonical source folder**. Do not train a replacement model or fabricate the missing per-seed data. `data/raw/*.csv`, `.venv/`, cache folders, `node_modules/`, `frontend/dist/`, secrets and temporary outputs must remain untracked.

After synchronization, run `python -m pytest`, compile/inspect research modules, rerun lightweight reproducibility checks, and compare committed outputs against the mean/std values in the report. Only then change the repository from *provisional* to *fully reproducible*.
