# DANDY COSMO — Label Generator

Pixel-identical product labels from Excel. Same input → same output, every time.

## Why this exists

ChatGPT renders each label as a fresh image — fonts shift, positions drift, batch jobs are unreliable. This repo solves that by treating label rendering as code:

- **Locked font** — `fonts/CodecPro-Regular.ttf` is committed to the repo. The script refuses to use anything else.
- **Deterministic layout** — every coordinate is fixed in `generate_labels.py`. No AI, no randomness.
- **Batch by default** — drop a 1,000-row Excel in `input/`, get 1,000 PNGs in `output/`.
- **Scheduled runs** — GitHub Actions rebuilds labels automatically when Excel files change, or on a daily cron.

## Spec (do not change without testing print quality)

| Element | Value |
|---|---|
| Canvas | 800 × 600 px (3:4 horizontal) |
| Background | #FFFFFF |
| Text color | #000000 |
| Font | Codec Pro Regular (NOT bold) |
| Product name | Top center, single line, auto-fit 18-38pt |
| Color/Size/Price | Left aligned, values column-aligned, 32pt |
| Barcode | Code 128, full width within padding, height ≤ 1/3 of canvas |
| Footer | `www.DANDYCOSMO.com` centered, 16pt, bottom |

## Setup (one time)

1. Clone the repo.
2. **Drop the licensed Codec Pro font file** into `fonts/`:
   - File must be named `CodecPro-Regular.ttf`
   - Without it, the script falls back to DejaVu Sans and prints a warning.
3. Install Python deps:

```bash
pip install -r requirements.txt
```

## Usage

### Single Excel file

```bash
python generate_labels.py --excel input/products.xlsx --out output/
```

Outputs:
- `output/{SKU}.png` — one PNG per SKU
- `output/labels.zip` — all PNGs bundled

### Excel format (required columns)

| Product name | SKU | Color | Size | Price |
|---|---|---|---|---|
| Muscle Fit Alpha Knit Polo | MS_ALPHAPOLO_BLACK_M | BLACK | M | 1650 |

Multiple sheets are concatenated automatically.

### Skip the zip

```bash
python generate_labels.py --excel input/products.xlsx --out output/ --no-zip
```

## Automation (GitHub Actions)

`.github/workflows/generate-labels.yml` runs the generator:
- on every push that changes `input/*.xlsx`
- on manual trigger from the Actions tab
- daily at 09:00 Bangkok time (02:00 UTC)

The PNG bundle is uploaded as a build artifact. Download from the workflow run page.

## When labels look wrong

| Symptom | Fix |
|---|---|
| Font looks generic / wrong | `fonts/CodecPro-Regular.ttf` missing — drop it in. |
| Product name overflows | Max font is 38pt; rename product or raise `PRODUCT_NAME_MAX_FONT`. |
| Barcode won't scan | Increase `module_width` in `render_barcode_image`, or lower `BARCODE_HEIGHT_RATIO` so bars get thicker per dot. |
| Price shows decimals | Excel cell is text — make sure the column type is number. |
| Output looks different on two machines | Confirm both have the same font file, same Pillow version (pinned in `requirements.txt`). |

## Layout knobs (top of `generate_labels.py`)

All layout numbers live in the CONFIGURATION block. Change there, not inside `render_label`. Test one SKU before committing.

## License notes

- Codec Pro is a commercial font from Monotype/Solpera. The `.ttf` is **not** in this repo by default — you commit your licensed copy under your own seat. Do not redistribute.
- Code 128 is a free, open barcode standard.
