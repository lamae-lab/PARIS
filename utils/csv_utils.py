"""
Helpers for reading and updating master_research_data.csv.

Used by pdf_retriever_agent and pdf_analyzer_agent to update
the CSV safely: one row at a time, without corrupting existing data.
"""

from __future__ import annotations
import csv
from pathlib import Path


def load_csv(csv_path: str | Path) -> list[dict]:
    """Load CSV as list of dicts. Returns [] if file is empty or header-only."""
    path = Path(csv_path)
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_csv(rows: list[dict], csv_path: str | Path) -> None:
    """Write rows back to CSV. Derives fieldnames from first row."""
    if not rows:
        return
    path = Path(csv_path)
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def update_row(rows: list[dict], paper_id: str, updates: dict) -> bool:
    """
    Apply updates to the row matching paper_id (column 'id').
    Returns True if found, False otherwise.
    Ensures new columns are present on all rows (backfills with "").
    """
    found = False
    new_keys = set(updates.keys())

    for row in rows:
        # ensure all rows have the new columns
        for key in new_keys:
            if key not in row:
                row[key] = ""
        if str(row.get("id", "")) == str(paper_id):
            row.update(updates)
            found = True

    return found


def get_accepted_rows(rows: list[dict]) -> list[dict]:
    """Return only rows where accepted == 'True'."""
    return [r for r in rows if str(r.get("accepted", "")).strip().lower() == "true"]


def get_downloaded_rows(rows: list[dict]) -> list[dict]:
    """Return only rows where downloaded == 'True'."""
    return [r for r in rows if str(r.get("downloaded", "")).strip().lower() == "true"]
