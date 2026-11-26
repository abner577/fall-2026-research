"""Run folders and blank manual-grading tables shared by all six detectors."""

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path


EST = timezone(timedelta(hours=-5), "EST")
RESULT_COLUMNS = (
    "target_id", "expected_answer", "result", "reported_locations",
    "explanation", "points", "final_accuracy_percentage",
)


def now():
    return datetime.now(EST)


def initialize_comparison_files(folder):
    """Create ungraded rows; never replace a manually completed table."""
    (folder / "confusion-matrices").mkdir(exist_ok=True)
    try:
        with (folder / "results-table.csv").open("x", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(RESULT_COLUMNS)
            for target in [*(f"V{i}" for i in range(1, 11)), "TOTAL"]:
                writer.writerow([target, *([""] * (len(RESULT_COLUMNS) - 1))])
    except FileExistsError:
        pass


def create_run_folder(output_dir, case, started=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    started = (started or now()).astimezone(EST)
    stem = f"{started:%Y-%m-%d_%I-%M-%p}_EST_{case}"
    index = 0
    while True:
        suffix = f" ({index})" if index else ""
        folder = output_dir / (stem + suffix)
        try:
            folder.mkdir()
            break
        except FileExistsError:
            index += 1
    initialize_comparison_files(folder)
    return folder
