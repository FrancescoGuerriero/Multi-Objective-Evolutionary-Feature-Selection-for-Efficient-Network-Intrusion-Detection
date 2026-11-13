# Reproduction guide

## 1. Clean clone / unzip

Work from a new directory that does not contain an existing virtual environment.

## 2. Create Python 3.12 environment

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Smoke verification without the research dataset

```bash
python tools/verify_submission.py
python -m pytest
python -m prototype.train_demo_model --output models/demo_pipeline.joblib --csv-output results/demo_rows.csv
python -m prototype.windows_ids replay --csv results/demo_rows.csv --model models/demo_pipeline.joblib --output results/demo_scored.csv
python -m prototype.windows_ids monitor --iterations 1
```

The synthetic model verifies prototype wiring only and must not be reported as an experiment.

## 4. Obtain UNSW-NB15

Download the dataset from the official UNSW source:

https://research.unsw.edu.au/projects/unsw-nb15-dataset

Place:

```text
data/raw/UNSW_NB15_training-set.csv
data/raw/UNSW_NB15_testing-set.csv
```

## 5. Full reproduction

Run the experiment commands documented in the root `README.md` after the canonical `research/` source has been copied into the repository.

## Clean-room release test status

The generated submission-support package is tested in a fresh virtual environment for:

- package structure verification;
- pytest prototype tests;
- synthetic model creation;
- CSV replay scoring;
- passive connection-monitor execution.

The full 5-seed, 300-evaluation research suite is not re-executed in the release clean room because the original UNSW-NB15 dataset and canonical local research source are not available inside the ChatGPT execution container. The submitted GitHub repository must contain those canonical local files before final delivery.

## Windows near-real-time compatible-flow watcher

Run `python -m prototype.windows_ids watch-flows --csv results/demo_rows.csv --model models/demo_pipeline.joblib --iterations 1 --output results/alerts.jsonl` after `python -m prototype.train_demo_model`. With an actual compatible exported flow file, the watcher only scores complete appended records. Windows socket snapshots alone cannot reconstruct the model's input features. This distinction is a validity boundary and must be explained in the report.
