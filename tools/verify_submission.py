from __future__ import annotations

from pathlib import Path
import sys


REQUIRED = [
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    ".gitignore",
    "docs/EXPERIMENT_PROTOCOL.md",
    "docs/REPRODUCTION.md",
    "prototype/windows_ids.py",
    "prototype/replay.py",
    "prototype/telemetry.py",
    "prototype/train_demo_model.py",
    "prototype/config/selected_features.json",
    "results/final_summary.csv",
    "report/COMP1818_EvoNIDS_Report.pdf",
]

FORBIDDEN_NAMES = {
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".idea",
    ".vscode",
}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    missing = [item for item in REQUIRED if not (root / item).exists()]
    forbidden = [
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.name in FORBIDDEN_NAMES
    ]

    if missing:
        print("Missing required release files:")
        for item in missing:
            print(f"  - {item}")
    if forbidden:
        print("Forbidden machine-specific directories found:")
        for item in forbidden:
            print(f"  - {item}")

    if missing or forbidden:
        return 1

    print("Submission structure verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
