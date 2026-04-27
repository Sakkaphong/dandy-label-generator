"""
DANDY COSMO — Price Tag Generator (v2 strict spec)
====================================================
Reads SKU data from Excel and produces one PNG per SKU at 1600x1200 px,
ready for 3x4cm print at ~1000 DPI.

STRICT SPEC (do not modify without retesting print quality):
- Canvas: 1600x1200 px, white background
- Font: Codec Pro Regular ONLY (no fallback — errors if missing)
- Header (product name): X=center, Y=92, start 116px, shrink to 60 if needed
- Color label: X=98, value X=405, Y=253, font 98px
- Size  label: X=98, value X=405, Y=384, font 98px
- Price label: X=98, value X=405, Y=515, font 98px ("THB 1,290" format)
- Barcode: Code 128, X=132, Y=660, W=1336, H=390, no quiet zone, even pixel distribution
- Footer: "www.DANDYCOSMO.com", X=center, Y=1082, font 90px

Output structure:
  output/{excel_filename}/{SKU}.png
  output/{excel_filename}/{excel_filename}.zip

Usage:
    python generate_labels.py --excel input/products.xlsx --out output/

Author: built for Boss / DANDY HOME
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from barcode.codex import Code128

# =============================================================================
# CONFIGURATION — locked layout, do not modify without test
# =============================================================================

CANVAS_W = 1600
CANVAS_H = 1200
BG_COLOR = (255, 255, 255)
FG_COLOR = (0, 0, 0)

# --- Font: Codec Pro Regular REQUIRED, no fallback ---
FONT_DIR = Path(__file__).parent / "fonts"
FONT_REGULAR = FONT_DIR / "CodecPro-Regular.ttf"

# --- Header (product name) ---
HEADER_Y = 92
HEADER_FONT_MAX = 116
HEADER_FONT_MIN = 60
HEADER_PADDING = 60   # left+right safe margin from canvas edge

# --- Info rows (Color / Size / Price) ---
INFO_FONT_SIZE = 98
INFO_LABEL_X = 98
INFO_VALUE_X = 405
INFO_Y = {
    "Color": 253,
    "Size":  384,
    "Price": 515,
}

# --- Barcode ---
BARCODE_X = 132
BARCODE_Y = 660
BARCODE_W = 1336
BARCODE_H = 390

# --- Footer ---
FOOTER_TEXT = "www.DANDYCOSMO.com"
FOOTER_Y = 1082
FOOTER_FONT_SIZE = 90
FOOTER_BARCODE_GAP_MIN = 24

# Sanity check: gap from barcode bottom to footer top
assert FOOTER_Y - (BARCODE_Y + BARCODE_H) >= FOOTER_BARCODE_GAP_MIN, \
    "Layout violation: footer too close to barcode"


# =============================================================================
# DATA
# =============================================================================

@dataclass(frozen=True)
class TagRow:
    sku: str
    product_name: str
    color: str
    size: str
    price: str

    @classmethod
    def from_excel_row(cls, row) -> "TagRow":
        return cls(
            sku=str(row["SKU"]).strip(),
            product_name=str(row["Product name"]).strip(),
            color=str(row["Color"]).strip(),
            size=str(row["Size"]).strip(),
            price=f"{int(float(row['Price'])):,}",
        )


# =============================================================================
# FONT
# =============================================================================

def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load Codec Pro at given size. Raises if font missing — no fallback."""
    if not FONT_REGULAR.exists():
        raise FileNotFoundError(
            f"REQUIRED FONT NOT FOUND: {FONT_REGULAR}\n"
            "This system requires Codec Pro Regular per spec — fallback is forbidden.\n"
            "Place 'CodecPro-Regular.ttf' in fonts/ folder."
        )
    return ImageFont.truetype(str(FONT_REGULAR), size=size)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def fit_header_font(draw, text: str, max_width: int) -> ImageFont.FreeTypeFont:
    """Find largest font size in [HEADER_FONT_MIN, HEADER_FONT_MAX] that fits one line."""
    for size in range(HEADER_FONT_MAX, HEADER_FONT_MIN - 1, -1):
        f = load_font(size)
        w, _ = text_size(draw, text, f)
        if w <= max_width:
            return f
    return load_font(HEADER_FONT_MIN)


# =============================================================================
# BARCODE — Code 128, even pixel distribution, no quiet zone
# =============================================================================

def render_barcode_uniform(sku: str, width: int, height: int) -> Image.Image:
    """
    Render Code 128 barcode with EXACT requested width/height, edge-to-edge,
    no quiet zone, with module widths distributed evenly to avoid the
    'last bar thicker' problem.

    Strategy: each module's pixel boundary is computed via integer math
    (i*width)//n — ensures every pixel is assigned to exactly one module,
    bar widths differ by at most 1 px across the whole barcode.
    """
    code = Code128(sku)
    raw = code.build()  # returns list of binary strings, e.g. ["10110010..."]
    if not raw:
        raise ValueError(f"Code128 build returned empty for SKU={sku!r}")
    binary = raw[0]
    n = len(binary)
    if n == 0:
        raise ValueError(f"Code128 produced 0 modules for SKU={sku!r}")

    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    for i, bit in enumerate(binary):
        if bit != "1":
            continue
        x_start = (i * width) // n
        x_end = ((i + 1) * width) // n
        # Every module gets at least 1 pixel (unless barcode width < num modules)
        if x_end > x_start:
            draw.rectangle([x_start, 0, x_end - 1, height - 1], fill=FG_COLOR)
    return img


# =============================================================================
# RENDERER
# =============================================================================

def render_tag(row: TagRow) -> Image.Image:
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # ---- HEADER (product name, centered, auto-fit one line) ----
    max_header_w = CANVAS_W - 2 * HEADER_PADDING
    header_font = fit_header_font(draw, row.product_name, max_header_w)
    hw, _ = text_size(draw, row.product_name, header_font)
    header_x = (CANVAS_W - hw) // 2
    draw.text((header_x, HEADER_Y), row.product_name, font=header_font, fill=FG_COLOR)

    # ---- INFO ROWS (Color / Size / Price) ----
    info_font = load_font(INFO_FONT_SIZE)
    rows = [
        ("Color", row.color),
        ("Size",  row.size),
        ("Price", f"THB {row.price}"),
    ]
    for label, value in rows:
        y = INFO_Y[label]
        draw.text((INFO_LABEL_X, y), label, font=info_font, fill=FG_COLOR)
        draw.text((INFO_VALUE_X, y), value, font=info_font, fill=FG_COLOR)

    # ---- BARCODE ----
    bc = render_barcode_uniform(row.sku, BARCODE_W, BARCODE_H)
    canvas.paste(bc, (BARCODE_X, BARCODE_Y))

    # ---- FOOTER ----
    footer_font = load_font(FOOTER_FONT_SIZE)
    fw, _ = text_size(draw, FOOTER_TEXT, footer_font)
    footer_x = (CANVAS_W - fw) // 2
    draw.text((footer_x, FOOTER_Y), FOOTER_TEXT, font=footer_font, fill=FG_COLOR)

    return canvas


# =============================================================================
# MAIN
# =============================================================================

def _zip_folder(folder: Path, zip_name: str) -> Path:
    pngs = sorted(folder.glob("*.png"))
    if not pngs:
        return folder / zip_name
    # cleanup old zip files so renamed/old ones don't accumulate
    for old_zip in folder.glob("*.zip"):
        try:
            old_zip.unlink()
        except OSError:
            pass
    zip_path = folder / zip_name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in pngs:
            zf.write(p, arcname=p.name)
    return zip_path


def generate_all(excel_path: Path, out_root: Path,
                 mode: str = "tag", make_zip: bool = True) -> None:
    """
    Generate price tags for every SKU in the given Excel file.

    Output structure:
        out_root/{excel_stem}/
            {SKU}.png
            {excel_stem}.zip

    `mode` is accepted for backward compatibility but ignored — only one
    output type exists per the v2 spec.
    """
    excel_stem = excel_path.stem
    base_dir = out_root / excel_stem
    base_dir.mkdir(parents=True, exist_ok=True)

    sheets = pd.read_excel(excel_path, sheet_name=None)
    df = pd.concat(sheets.values(), ignore_index=True)
    required = {"SKU", "Product name", "Color", "Size", "Price"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Excel missing required columns: {missing}")

    # cleanup old subfolders from v1 spec (labels/ barcodes/) if present
    for legacy in ("labels", "barcodes"):
        legacy_dir = base_dir / legacy
        if legacy_dir.is_dir():
            for f in legacy_dir.iterdir():
                try:
                    f.unlink()
                except OSError:
                    pass
            try:
                legacy_dir.rmdir()
            except OSError:
                pass

    print(f"[{excel_stem}] {len(df)} rows -> generating tags")
    n = 0
    for _, row in df.iterrows():
        try:
            r = TagRow.from_excel_row(row)
        except Exception as e:
            print(f"  [SKIP] bad row: {e}")
            continue
        out_path = base_dir / f"{r.sku}.png"
        render_tag(r).save(out_path, "PNG", optimize=True)
        n += 1
        print(f"  -> {r.sku}")

    if make_zip and n:
        zip_name = f"{excel_stem}.zip"
        # also clean any old labels.zip / barcodes.zip / "* - labels.zip" leftovers
        for old in base_dir.glob("*.zip"):
            try:
                old.unlink()
            except OSError:
                pass
        zp = _zip_folder(base_dir, zip_name)
        print(f"  Bundled: {zp.name}")

    print(f"[{excel_stem}] Done. tags={n}")


def main() -> None:
    ap = argparse.ArgumentParser(description="DANDY COSMO price tag generator (v2)")
    ap.add_argument("--excel", required=True, type=Path, help="Input .xlsx file")
    ap.add_argument("--out", default=Path("output"), type=Path, help="Output root dir")
    ap.add_argument("--no-zip", action="store_true", help="Skip building zip bundles")
    # mode flag kept for backward compatibility
    ap.add_argument("--mode", default="tag",
                    help=argparse.SUPPRESS)  # ignored
    args = ap.parse_args()
    generate_all(args.excel, args.out, mode=args.mode, make_zip=not args.no_zip)


if __name__ == "__main__":
    main()
