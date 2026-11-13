# Integrated React / FastAPI dashboard for Windows

The React production build is served from the same localhost origin as the read-only FastAPI API. No separate Vite server is needed in normal Windows use.

## Launch

From the repository root on Windows, after installing Python 3.12, Node.js 20+ and the Python requirements:

```powershell
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File tools/start_windows_dashboard.ps1
```

Open **http://127.0.0.1:8000/**. The launcher builds Vite assets into `frontend/dist` and starts `uvicorn`, which serves both the dashboard and the API.

The dashboard shows Windows TCP/UDP connection metadata, the latest externally exported compatible-flow classifications from `results/alerts.jsonl`, dataset presence, and the historical five-seed results in `results/final_summary.csv`.

To create synthetic smoke-test decisions, in a second terminal run from the project root:

```bash
python -m prototype.train_demo_model
python -m prototype.windows_ids watch-flows --csv results/demo_rows.csv --model models/demo_pipeline.joblib --iterations 1 --output results/alerts.jsonl
```

Refresh the dashboard. **Synthetic data is a wiring test and does not measure network intrusion detection accuracy.**

## React development mode

Start FastAPI separately with `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`; then run `npm install` and `npm run dev` inside `frontend/`. Visit `http://localhost:5173`. React requests localhost:8000 only when opened on port 5173; in production it requests same-origin `/api` endpoints.

## Scientific boundaries

* Socket snapshots are passive, not model predictions; socket metadata does not contain UNSW-NB15 engineered features.
* A model only classifies **schema-compatible complete flow rows** from a separate exporter. `watch-flows` does not sniff network packets.
* Historical comparison metrics are not real-time Windows detection metrics.
* No packet interception, firewall alteration, or automatic blocking.
* The canonical latest 300-evaluation research suite and NSGA-II source must still be synchronised from the Windows workstation before the complete claimed experiment can be recreated solely from GitHub.

## Verification

```bash
python -m pytest -q research/tests prototype/tests backend/tests
cd frontend && npm install && npm run build
```

The Python tests can pass without the Vite build; the integrated home page `/` is served when `frontend/dist/index.html` exists.
