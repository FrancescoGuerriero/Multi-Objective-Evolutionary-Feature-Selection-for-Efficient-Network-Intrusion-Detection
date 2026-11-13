from __future__ import annotations

import argparse
from pathlib import Path
import shutil


EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
}

EXCLUDE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
    ".bak",
}

TOP_LEVEL_ALLOW = {
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    ".gitignore",
    "research",
    "backend",
    "frontend",
    "prototype",
    "results",
    "docs",
    "report",
    "tools",
}


def ignore_filter(directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        path = Path(directory) / name
        if name in EXCLUDE_DIRS:
            ignored.add(name)
        elif path.suffix.lower() in EXCLUDE_SUFFIXES:
            ignored.add(name)
        elif name.startswith(".env"):
            ignored.add(name)
    return ignored


def copy_item(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(
            source,
            destination,
            dirs_exist_ok=True,
            ignore=ignore_filter,
        )
    elif source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a clean COMP1818 submission/reproducibility folder."
    )
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination", required=True)
    args = parser.parse_args()

    source = Path(args.source).resolve()
    destination = Path(args.destination).resolve()

    if not source.exists():
        raise FileNotFoundError(source)
    if destination == source or source in destination.parents:
        raise ValueError("Destination must be outside the source project tree.")

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    for name in TOP_LEVEL_ALLOW:
        item = source / name
        if item.exists():
            copy_item(item, destination / name)

    data_readme = destination / "data" / "README.md"
    data_readme.parent.mkdir(parents=True, exist_ok=True)
    data_readme.write_text(
        "UNSW-NB15 raw CSV files are not bundled. Download them from the official UNSW source "
        "and place them under data/raw/.\n",
        encoding="utf-8",
    )

    print(f"Clean submission folder created at: {destination}")


if __name__ == "__main__":
    main()
