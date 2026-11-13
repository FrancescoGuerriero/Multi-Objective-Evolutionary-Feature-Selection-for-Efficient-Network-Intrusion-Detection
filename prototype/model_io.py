from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib


def load_pipeline(path: str | Path) -> Any:
    model_path = Path(path)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}. "
            "Train/export a pipeline first or use prototype.train_demo_model for a smoke test."
        )
    return joblib.load(model_path)
