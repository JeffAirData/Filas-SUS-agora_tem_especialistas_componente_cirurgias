import csv
import json
from pathlib import Path


def _ensure_parent(filepath: str) -> Path:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_metadata_json(data: list[dict], filepath: str) -> None:
    path = _ensure_parent(filepath)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_metadata_csv(data: list[dict], filepath: str) -> None:
    path = _ensure_parent(filepath)
    if not data:
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        return

    fieldnames = list(data[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)