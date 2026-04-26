#!/usr/bin/env bash
# Quick local runner — processes every .xlsx in input/
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p output
for f in input/*.xlsx; do
  [ -e "$f" ] || { echo "No .xlsx files in input/ — drop one in and re-run."; exit 1; }
  name=$(basename "$f" .xlsx)
  echo "==> $name"
  python3 generate_labels.py --excel "$f" --out "output/$name"
done
echo "Done. Open output/ to see your labels."
