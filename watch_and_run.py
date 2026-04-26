"""
DANDY COSMO — Watch & Run
==========================
Scans `input/` for Excel files. Only processes files that are NEW or MODIFIED
since the last successful run. Skips silently if nothing changed.

Used by:
  - Claude Cowork scheduled task
  - Local cron / launchd
  - GitHub Actions (optional)

State is tracked in `.run_state.json` next to this script.

Usage:
    python watch_and_run.py
    python watch_and_run.py --force      # re-process everything regardless
    python watch_and_run.py --mode label # only product labels
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

from generate_labels import generate_all

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "input"
OUTPUT_DIR = ROOT / "output"
STATE_FILE = ROOT / ".run_state.json"


def _file_signature(p: Path) -> str:
    """Cheap fingerprint: size + mtime. Falls back to md5 if needed."""
    st = p.stat()
    return f"{st.st_size}-{int(st.st_mtime)}"


def _md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"files": {}, "last_run": None}


def save_state(state: dict) -> None:
    state["last_run"] = datetime.now().isoformat(timespec="seconds")
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def main() -> int:
    ap = argparse.ArgumentParser(description="Watch input/ for new Excel files and run generator")
    ap.add_argument("--force", action="store_true", help="Process every file, ignore state")
    ap.add_argument("--mode", choices=["both", "label", "barcode"], default="both")
    args = ap.parse_args()

    if not INPUT_DIR.exists():
        print(f"[ERROR] {INPUT_DIR} does not exist. Create it and drop .xlsx files in.")
        return 1

    excel_files = sorted(INPUT_DIR.glob("*.xlsx"))
    if not excel_files:
        print(f"[INFO] No .xlsx files found in {INPUT_DIR}. Nothing to do.")
        return 0

    state = load_state()
    if args.force:
        state["files"] = {}

    to_process = []
    for f in excel_files:
        # ignore Excel temp lock files
        if f.name.startswith("~$"):
            continue
        sig = _file_signature(f)
        last_sig = state["files"].get(f.name)
        if last_sig == sig:
            print(f"[SKIP] {f.name}  (unchanged)")
            continue
        to_process.append((f, sig))

    if not to_process:
        print(f"[OK] Nothing changed since last run ({state.get('last_run')})")
        save_state(state)  # touch last_run
        return 0

    print(f"[RUN] {len(to_process)} file(s) new or modified -> generating...")
    OUTPUT_DIR.mkdir(exist_ok=True)

    failed = []
    for f, sig in to_process:
        try:
            generate_all(f, OUTPUT_DIR, mode=args.mode, make_zip=True)
            state["files"][f.name] = sig
        except Exception as e:
            print(f"[FAIL] {f.name}: {e}")
            failed.append(f.name)

    save_state(state)

    if failed:
        print(f"\n[DONE WITH ERRORS] failed: {failed}")
        return 2
    print(f"\n[DONE] Processed {len(to_process)} file(s). Output: {OUTPUT_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
