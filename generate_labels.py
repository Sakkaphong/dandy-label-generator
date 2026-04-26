"""
DANDY COSMO — Deterministic Label Generator
=====================================================
Reads SKU data from Excel and produces pixel-identical PNG outputs every run.

TWO OUTPUT MODES (both produced by default):
  1. labels/   — full product label (800x600, name + color/size/price + barcode + footer)
  2. barcodes/ — barcode-only image (600x300, just bars + SKU text + footer)

Output structure:
  output/
    {excel_filename}/
      labels/    {SKU}.png ...  + labels.zip
      barcodes/  {SKU}.png ...  + barcodes.zip

Usage:
    python generate_labels.py --excel input/products.xlsx --out output/
    python generate_labels.py --excel input/products.xlsx --out output/ --mode label
    python generate_labels.py --excel input/products.xlsx --out output/ --mode barcode

Author: built for Boss / DANDY HOME
"""

from __future__ import annotations

import argparse
import io
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter

# =============================================================================
# CONFIGURATION — change here, never inside render code
# =============================================================================

# --- Full product label canvas (800 x 600) ---
CANVAS_W = 800
CANVAS_H = 600

# --- Barcode-only canvas (600 x 300) ---
BARCODE_CANVAS_W = 600
BARCODE_CANVAS_H = 300
BARCODE_ONLY_BARS_RATIO = 0.55     # 55% of canvas height for the bars
BARCODE_ONLY_SKU_FONT = 22         # SKU text size below bars
BARCODE_ONLY_FOOTER_FONT = 14
BARCODE_ONLY_PADDING_X = 30
BARCODE_ONLY_PADDING_TOP = 24

BG_COLOR = (255, 255, 255)
FG_COLOR = (0, 0, 0)

# Font file path — locked to repo. Replace with licensed Codec Pro file.
FONT_DIR = Path(__file__).parent / "fonts"
FONT_REGULAR = FONT_DIR / "CodecPro-Regular.ttf"
# Fallback (only if Codec Pro not present — used for first-run testing)
FONT_FALLBACK = FONT_DIR / "DejaVuSans.ttf"

# Layout (all in px, measured from top-left)
PADDING_X = 40                 # left/right margin
PADDING_TOP = 30               # space above product name
PRODUCT_NAME_MAX_FONT = 38     # auto-shrinks to fit one line
PRODUCT_NAME_MIN_FONT = 18
DETAILS_FONT_SIZE = 32         # Color / Size / Price label size
DETAILS_LINE_GAP = 12          # vertical gap between detail lines
DETAILS_COLON_GAP = 14         # space after the ":" before value
BARCODE_HEIGHT_RATIO = 0.30    # <= 1/3 of canvas height
BARCODE_BOTTOM_GAP = 12        # space between barcode and footer
FOOTER_FONT_SIZE = 16
FOOTER_TEXT = "www.DANDYCOSMO.com"
FOOTER_BOTTOM_PADDING = 18

DETAIL_FIELDS = ("Color", "Size", "Price")
PRICE_PREFIX = "THB "


# =============================================================================
# DATA TYPES
# =============================================================================

@dataclass(frozen=True)
class LabelRow:
    sku: str
    product_name: str
    color: str
    size: str
    price: str

    @classmethod
    def from_excel_row(cls, row) -> "LabelRow":
        return cls(
            sku=str(row["SKU"]).strip(),
            product_name=str(row["Product name"]).strip(),
            color=str(row["Color"]).strip(),
            size=str(row["Size"]).strip(),
            price=f"{int(float(row['Price'])):,}",
        )


# =============================================================================
# FONT LOADING — locked, with explicit fallback warning
# =============================================================================

def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load Codec Pro at given size, or fallback if not present."""
    if FONT_REGULAR.exists():
        return ImageFont.truetype(str(FONT_REGULAR), size=size)
    if FONT_FALLBACK.exists():
        return ImageFont.truetype(str(FONT_FALLBACK), size=size)
    # last resort — system search
    for candidate in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    raise RuntimeError(
        "No font found. Place CodecPro-Regular.ttf in ./fonts/ "
        "or DejaVuSans.ttf as fallback."
    )


def warn_if_fallback() -> None:
    if not FONT_REGULAR.exists():
        print(
            "[WARN] fonts/CodecPro-Regular.ttf not found. "
            "Using fallback font — output will not match production exactly. "
            "Place the licensed Codec Pro file in fonts/ for final output.",
            file=sys.stderr,
        )


# =============================================================================
# TEXT MEASUREMENT HELPERS
# =============================================================================

def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def fit_one_line_font(draw, text: str, max_width: int,
                      max_size: int, min_size: int) -> ImageFont.FreeTypeFont:
    """Find largest font size that fits text in one line within max_width."""
    for size in range(max_size, min_size - 1, -1):
        f = load_font(size)
        if text_width(draw, text, f) <= max_width:
            return f
    return load_font(min_size)


# =============================================================================
# BARCODE — Code 128, fixed dimensions
# =============================================================================

def render_barcode_image(sku: str, target_width: int, target_height: int) -> Image.Image:
    """Generate Code 128 barcode as PIL image at exact target dimensions."""
    code128 = barcode.get_barcode_class("code128")
    writer = ImageWriter()
    # Tighten writer options — we'll resize anyway, but smaller font/quiet zone helps
    options = {
        "module_width": 0.4,
        "module_height": 12.0,
        "quiet_zone": 2.0,
        "write_text": False,    # we don't render the human-readable text under bars
        "background": "white",
        "foreground": "black",
        "dpi": 300,
    }
    bc = code128(sku, writer=writer)
    buf = io.BytesIO()
    bc.write(buf, options=options)
    buf.seek(0)
    img = Image.open(buf).convert("RGB")
    # Resize to exact target — preserve crisp bars by using NEAREST
    img = img.resize((target_width, target_height), Image.NEAREST)
    return img


# =============================================================================
# LABEL RENDERER
# =============================================================================

def render_label(row: LabelRow) -> Image.Image:
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    inner_left = PADDING_X
    inner_right = CANVAS_W - PADDING_X
    inner_width = inner_right - inner_left
    cursor_y = PADDING_TOP

    # ---- 1. PRODUCT NAME — top center, single line, auto-fit ----
    name_font = fit_one_line_font(
        draw, row.product_name, inner_width,
        PRODUCT_NAME_MAX_FONT, PRODUCT_NAME_MIN_FONT,
    )
    name_w = text_width(draw, row.product_name, name_font)
    name_x = (CANVAS_W - name_w) // 2
    draw.text((name_x, cursor_y), row.product_name, font=name_font, fill=FG_COLOR)
    name_h = text_height(draw, row.product_name, name_font)
    cursor_y += name_h + 24

    # ---- 2. PRODUCT DETAILS — left aligned, value column aligned ----
    details_font = load_font(DETAILS_FONT_SIZE)
    labels = [f"{k}:" for k in DETAIL_FIELDS]
    values = [row.color, row.size, f"{PRICE_PREFIX}{row.price}"]

    # Find widest label so all values start at same x
    max_label_w = max(text_width(draw, lbl, details_font) for lbl in labels)
    value_x = inner_left + max_label_w + DETAILS_COLON_GAP

    for label, value in zip(labels, values):
        draw.text((inner_left, cursor_y), label, font=details_font, fill=FG_COLOR)
        draw.text((value_x, cursor_y), value, font=details_font, fill=FG_COLOR)
        line_h = text_height(draw, label, details_font)
        cursor_y += line_h + DETAILS_LINE_GAP

    cursor_y += 8  # breathing space before barcode

    # ---- 4. FOOTER — reserve space first so barcode can fill remaining ----
    footer_font = load_font(FOOTER_FONT_SIZE)
    footer_h = text_height(draw, FOOTER_TEXT, footer_font)
    footer_y = CANVAS_H - FOOTER_BOTTOM_PADDING - footer_h
    barcode_bottom = footer_y - BARCODE_BOTTOM_GAP

    # ---- 3. BARCODE — full width, height capped at 1/3 of canvas ----
    bc_max_h = int(CANVAS_H * BARCODE_HEIGHT_RATIO)
    bc_available_h = barcode_bottom - cursor_y
    bc_h = min(bc_max_h, max(bc_available_h, 80))
    bc_w = inner_width  # full edge-to-edge within padding
    bc_img = render_barcode_image(row.sku, bc_w, bc_h)
    bc_y = barcode_bottom - bc_h
    canvas.paste(bc_img, (inner_left, bc_y))

    # ---- footer text ----
    footer_w = text_width(draw, FOOTER_TEXT, footer_font)
    footer_x = (CANVAS_W - footer_w) // 2
    draw.text((footer_x, footer_y), FOOTER_TEXT, font=footer_font, fill=FG_COLOR)

    return canvas


# =============================================================================
# BARCODE-ONLY RENDERER (for tags / inventory stickers)
# =============================================================================

def render_barcode_only(row: LabelRow) -> Image.Image:
    """Standalone barcode image: bars + SKU text + DANDYCOSMO footer."""
    canvas = Image.new("RGB", (BARCODE_CANVAS_W, BARCODE_CANVAS_H), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    inner_left = BARCODE_ONLY_PADDING_X
    inner_w = BARCODE_CANVAS_W - 2 * BARCODE_ONLY_PADDING_X

    # Footer reserved at bottom
    footer_font = load_font(BARCODE_ONLY_FOOTER_FONT)
    footer_h = text_height(draw, FOOTER_TEXT, footer_font)
    footer_y = BARCODE_CANVAS_H - 14 - footer_h

    # SKU text just above footer
    sku_font = load_font(BARCODE_ONLY_SKU_FONT)
    sku_h = text_height(draw, row.sku, sku_font)
    sku_y = footer_y - 8 - sku_h

    # Barcode fills space from top padding to just above SKU
    bars_top = BARCODE_ONLY_PADDING_TOP
    bars_bottom = sku_y - 10
    bars_h = max(60, bars_bottom - bars_top)
    bars_h = min(bars_h, int(BARCODE_CANVAS_H * BARCODE_ONLY_BARS_RATIO + 40))
    bars_img = render_barcode_image(row.sku, inner_w, bars_h)
    canvas.paste(bars_img, (inner_left, bars_top))

    # SKU text centered
    sku_w = text_width(draw, row.sku, sku_font)
    draw.text(((BARCODE_CANVAS_W - sku_w) // 2, sku_y),
              row.sku, font=sku_font, fill=FG_COLOR)

    # Footer
    f_w = text_width(draw, FOOTER_TEXT, footer_font)
    draw.text(((BARCODE_CANVAS_W - f_w) // 2, footer_y),
              FOOTER_TEXT, font=footer_font, fill=FG_COLOR)
    return canvas


# =============================================================================
# MAIN
# =============================================================================

def _zip_folder(folder: Path, zip_name: str) -> Path:
    pngs = sorted(folder.glob("*.png"))
    if not pngs:
        return folder / zip_name
    zip_path = folder / zip_name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in pngs:
            zf.write(p, arcname=p.name)
    return zip_path


def generate_all(excel_path: Path, out_root: Path,
                 mode: str = "both", make_zip: bool = True) -> None:
    """
    Generate labels and/or barcodes for every row in the given Excel file.

    Output goes to: out_root/{excel_stem}/labels/  and  out_root/{excel_stem}/barcodes/
    """
    warn_if_fallback()
    excel_stem = excel_path.stem  # e.g. "Barcode Muscle Fit Alpha Polo"
    base_dir = out_root / excel_stem
    base_dir.mkdir(parents=True, exist_ok=True)

    # Read every sheet, concat
    sheets = pd.read_excel(excel_path, sheet_name=None)
    df = pd.concat(sheets.values(), ignore_index=True)
    required = {"SKU", "Product name", "Color", "Size", "Price"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Excel missing required columns: {missing}")

    do_label = mode in ("both", "label")
    do_barcode = mode in ("both", "barcode")

    label_dir = base_dir / "labels"
    barcode_dir = base_dir / "barcodes"
    if do_label:
        label_dir.mkdir(parents=True, exist_ok=True)
    if do_barcode:
        barcode_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{excel_stem}] {len(df)} rows -> mode={mode}")
    n_label = n_barcode = 0
    for _, row in df.iterrows():
        try:
            r = LabelRow.from_excel_row(row)
        except Exception as e:
            print(f"  [SKIP] bad row: {e}")
            continue
        if do_label:
            render_label(r).save(label_dir / f"{r.sku}.png", "PNG", optimize=True)
            n_label += 1
        if do_barcode:
            render_barcode_only(r).save(barcode_dir / f"{r.sku}.png", "PNG", optimize=True)
            n_barcode += 1
        print(f"  -> {r.sku}")

    if make_zip:
        if do_label and n_label:
            print(f"  Bundled: {_zip_folder(label_dir, 'labels.zip').name}")
        if do_barcode and n_barcode:
            print(f"  Bundled: {_zip_folder(barcode_dir, 'barcodes.zip').name}")

    print(f"[{excel_stem}] Done. labels={n_label}  barcodes={n_barcode}")


def main() -> None:
    ap = argparse.ArgumentParser(description="DANDY COSMO label & barcode generator")
    ap.add_argument("--excel", required=True, type=Path, help="Input .xlsx file")
    ap.add_argument("--out", default=Path("output"), type=Path, help="Output root dir")
    ap.add_argument("--mode", choices=["both", "label", "barcode"], default="both",
                    help="What to generate (default: both)")
    ap.add_argument("--no-zip", action="store_true", help="Skip building zip bundles")
    args = ap.parse_args()
    generate_all(args.excel, args.out, mode=args.mode, make_zip=not args.no_zip)


if __name__ == "__main__":
    main()
