from pathlib import Path
import joblib

def load_pipeline(path):
    file = Path(path)
    if not file.is_file():
        raise FileNotFoundError(f"Model missing: {file}. Run the synthetic demo trainer for a smoke test.")
    return joblib.load(file)
