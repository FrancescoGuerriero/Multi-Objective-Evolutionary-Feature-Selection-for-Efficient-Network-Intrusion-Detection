# Multi-Objective Evolutionary Feature Selection for Efficient Network Intrusion Detection

**COMP-1818 Artificial Intelligence Applications — University of Greenwich**

**Repository state:** provisional, awaiting synchronization of the complete canonical source and final five-seed experiment outputs from the Windows development workstation. The downloadable release archive was assembled and smoke-tested separately; **do not treat this repository as full experiment reproduction until the remaining research source has been pushed**.

## Research

UNSW-NB15 binary network intrusion detection with 42 original predictors (drop `id` and `attack_cat`). Four feature-selection approaches: GA, BPSO, PSO and NSGA-II. Five seeds (42, 101, 202, 303, 404), each with 300 *unique expensive classifier evaluations*.

| Classifier / selector | Mean Macro-F1 | Raw features | Feature reduction |
|---|---:|---:|---:|
| Full XGBoost | 0.870417 | 42 | 0% |
| GA + RF | 0.865394 | 10.2 | 75.71% |
| Full Random Forest | 0.864225 | 42 | 0% |
| BPSO + RF | 0.861518 | 12.2 | 70.95% |
| PSO + RF | 0.859817 | 11.4 | 72.86% |
| NSGA-II + RF | 0.856150 | 10.6 | 74.76% |

GA has the best feature-selection trade-off; full XGBoost has the best absolute mean Macro-F1. Friedman omnibus p=0.178 across 5 seeds did not establish a statistically significant difference among feature selectors. These are reported experimental findings, **not yet independently reproducible from this provisional remote snapshot**.

**Official dataset:** https://research.unsw.edu.au/projects/unsw-nb15-dataset

Required local filenames: `data/raw/UNSW_NB15_training-set.csv` and `data/raw/UNSW_NB15_testing-set.csv`. Raw datasets are not committed to GitHub.

## Windows IDS extension

The passive Windows monitor reads local socket metadata (TCP/UDP connections, processes); it does not block network traffic. The ML replay/watch pipeline only classifies records from an **externally exported, schema-compatible flow CSV**, using a matching fitted preprocessing+classifier pipeline. **Windows sockets are not equivalent to the UNSW-NB15 feature vector**; the packet/flow extraction bridge and real trained model export remain required for real-world live classification. A synthetic demo model is strictly a wiring test, not coursework performance evidence.

The full development workstation must sync its canonical source before these commands are available on this GitHub repository:

```bash
python -m pytest
python -m prototype.train_demo_model
python -m prototype.windows_ids monitor --interval 2 --iterations 3
python -m prototype.windows_ids replay --csv results/demo_rows.csv --model models/demo_pipeline.joblib
python -m prototype.windows_ids watch-flows --csv results/demo_rows.csv --model models/demo_pipeline.joblib --iterations 1 --output results/alerts.jsonl
```

## Final coursework submission

Submit the **four-page + references PDF** to Moodle. Include a link to this public repository and the official dataset within the PDF. Full source and model/results evidence must be synchronized and verified before the tutor relies on this repository for rerunning the final research results.

## Source upload from canonical Windows project

From `C:/Users/Francesco/EvoNIDS_COMP1818_Phase1/EvoNIDS_COMP1818`, first merge the vetted prototype/release package into the same canonical project, then check `.gitignore`, use `git status`, and push source, results and report to this repository. Avoid committing local `.venv`, caches, raw data, credentials or machine-specific generated outputs. Preserve your original project; do not create competing canonical copies.
