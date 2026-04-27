# DANDY COSMO — Price Tag Generator

Pixel-identical product price tags from Excel. Same input → same output, every time. Print-ready at 3×4 cm.

## Why this exists

ChatGPT renders each label as a fresh image — fonts shift, positions drift, batch jobs are unreliable. This repo solves that by treating tag rendering as code:

- **Locked font** — Codec Pro Regular only, no fallback. Script errors if font missing.
- **Deterministic layout** — every coordinate is fixed in `generate_labels.py`. No AI, no randomness.
- **Batch by default** — drop a 1,000-row Excel in `input/`, get 1,000 PNGs in `output/`.
- **Change detection** — `watch_and_run.py` only re-renders Excel files that actually changed.
- **Scheduled runs** — runs daily via Claude Cowork or GitHub Actions.

## Spec v2 (current — do not change without retesting print quality)

| Element | Value |
|---|---|
| Canvas | **1600 × 1200 px** (prints at 3 × 4 cm, ~1000 DPI) |
| Background | #FFFFFF |
| Text color | #000000 |
| Font | Codec Pro Regular only (`fonts/CodecPro-Regular.ttf` required) |
| Header (product name) | Center, Y=92, font 116pt → shrinks to 60pt to fit one line |
| Color row | Label X=98, Value X=405, Y=253, font 98pt |
| Size row | Label X=98, Value X=405, Y=384, font 98pt |
| Price row | Label X=98, Value X=405, Y=515, font 98pt, format `THB 1,290` |
| Barcode | Code 128, X=132, Y=660, W=1336, H=390, no quiet zone, even pixel distribution |
| Footer | `www.DANDYCOSMO.com`, center, Y=1082, font 90pt |

Layout priority on collision: Barcode → Footer → Info → Header. Only the header font shrinks to resolve overflow.

## Setup (one time)

1. Clone the repo.
2. **Drop the licensed Codec Pro font file** into `fonts/`:
   - File must be named exactly `CodecPro-Regular.ttf`
   - Codec Pro is commercial and **not** committed (blocked by `.gitignore`).
3. Install Python deps:

```bash
pip install -r requirements.txt
```

## Usage

### Run once on a single Excel file

```bash
python generate_labels.py --excel input/products.xlsx --out output/
```

### Watch & run all Excel files (recommended)

Detects which Excel files are new or modified and processes only those:

```bash
python watch_and_run.py
```

Force re-render everything (e.g., after font/layout changes):

```bash
python watch_and_run.py --force
```

### Output structure

```
output/
└── {excel_filename}/
    ├── {SKU1}.png        ← 1600×1200 price tag
    ├── {SKU2}.png
    ├── ...
    └── {excel_filename}.zip   ← all PNGs bundled
```

## Excel format (required columns)

| Product name | SKU | Color | Size | Price |
|---|---|---|---|---|
| Muscle Fit Alpha Knit Polo | MS_ALPHAPOLO_BLACK_M | BLACK | M | 1650 |

Column names must match exactly (case-sensitive). Multiple sheets in one file are concatenated automatically.

## Automation

### Claude Cowork (recommended for daily use)

A scheduled task `dandy-label-watch` runs daily at 09:09 local time. It calls `watch_and_run.py`, processes only modified Excel files, and reports results.

### GitHub Actions

`.github/workflows/generate-labels.yml` runs on every push to `input/*.xlsx` or on manual trigger. Outputs are uploaded as build artifacts. Note: the cloud runner falls back to system fonts because Codec Pro is not committed — Actions is for syntax validation, not production-quality output.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `REQUIRED FONT NOT FOUND` error | Place `CodecPro-Regular.ttf` in `fonts/` |
| Tag layout doesn't match spec | Don't edit constants outside the CONFIGURATION block in `generate_labels.py` |
| Barcode won't scan | Test print at exactly 4 cm wide; if still failing, increase `BARCODE_W` slightly or contact maintainer |
| Output looks different on two machines | Confirm both have the same Codec Pro file and pinned Pillow version |
| Same Excel won't re-render | Use `--force` flag or delete `.run_state.json` |

## License notes

- Codec Pro is a commercial font from Solpera/Monotype. Each user must have their own license — never commit the font file to a repo (public or private).
- Code 128 is a free, open barcode standard.
- Project code is for internal DANDY HOME use.
