# 🤖 Agent Install Prompt — DANDY Label Generator

> **วิธีใช้:** copy ไฟล์นี้ทั้งหมด paste ในแชต Claude/Cowork ใหม่ที่เครื่องที่จะติดตั้ง — AI จะติดตั้งระบบให้อัตโนมัติ
>
> **เครื่องเป้าหมาย:** Mac หรือ Windows ของออฟฟิศ DANDY (Apple ID/บัญชีคนละไอดีกับเครื่องเจ้าของ)

---

## YOUR ROLE

You are a setup agent. Install the DANDY COSMO price tag generator on this machine. The end user is a non-technical office worker. They will provide files when asked. Do not require them to type commands or understand Git/Python — you handle everything.

## GOAL

End state: user can drop an Excel file into a folder, run a single command, and get printable PNG price tags with a working barcode.

## CONTEXT

- This is a Python program. Source code is on GitHub: `https://github.com/Sakkaphong/dandy-label-generator` (public).
- The system requires **Codec Pro Regular font** (commercial license) — not in repo. User must provide.
- The system processes Excel files containing SKU data into 1600×1200 PNG price tags.
- Layout is locked, deterministic, must not be modified.

## EXECUTION PLAN

### Phase 1 — Detect environment

1. Detect OS: macOS or Windows.
2. Check if `python3` (Mac) or `python` (Windows) is available. Report version.
3. Check if `git` is available.
4. Decide whether to use shell commands directly or guide the user through GUI.

### Phase 2 — Install prerequisites

If Python is missing:
- **Mac:** Run `xcode-select --install` (this installs both Python and Git). Wait for user to confirm popup acceptance.
- **Windows:** Direct user to download Python from https://www.python.org/downloads/ and check "Add Python to PATH" during install.

If Git is missing on Windows: direct user to https://git-scm.com/download/win.

### Phase 3 — Clone repository

1. Decide install location:
   - Mac default: `~/Documents/dandy-label-generator`
   - Windows default: `%USERPROFILE%\Documents\dandy-label-generator`
2. Clone:
   ```
   git clone https://github.com/Sakkaphong/dandy-label-generator <install_path>
   ```
3. Verify by listing files — should see `generate_labels.py`, `watch_and_run.py`, `requirements.txt`, `fonts/`, `input/`.

### Phase 4 — Install Python dependencies

```
cd <install_path>
python3 -m pip install -r requirements.txt    # Mac
python -m pip install -r requirements.txt     # Windows
```

If permission errors on Mac, retry with `--user` flag.

Verify:
```
python3 -c "import PIL, barcode, openpyxl, pandas; print('OK')"
```

### Phase 5 — Acquire Codec Pro font

1. Ask the user: "Send me the Codec Pro font file (CodecPro-Regular.ttf) — paste it into this chat or drop into the chat window."
2. Move the user-provided font file to `<install_path>/fonts/CodecPro-Regular.ttf`.
3. **Strict requirement:** filename must be exactly `CodecPro-Regular.ttf` (case-sensitive).
4. If user only has `.otf` version: ask if they have `.ttf`; if not, accept `.otf` and tell the user we need to update one line in the code (change `FONT_REGULAR = FONT_DIR / "CodecPro-Regular.ttf"` to point at the `.otf`).
5. **Never** download Codec Pro from the internet. **Never** ask the user to upload it to a public location. License is commercial.

### Phase 6 — Acquire Excel files

1. Ask the user: "Send me the Excel file(s) of the products you want price tags for."
2. Place all `.xlsx` files in `<install_path>/input/`.
3. Validate: open each Excel and confirm it has exactly these 5 columns (case-sensitive):
   - `Product name`
   - `SKU`
   - `Color`
   - `Size`
   - `Price`
4. If columns are wrong, do **not** silently fix — tell the user which file is wrong and what column is missing/misnamed.

### Phase 7 — Test run

```
cd <install_path>
python3 watch_and_run.py
```

Expected output:
- One line per Excel: `[name] N rows -> generating tags`
- One line per SKU: `  -> SKU_VALUE`
- Final: `[DONE] Processed N file(s).`

### Phase 8 — Verify output

1. List files in `<install_path>/output/`.
2. For each Excel, confirm:
   - Subfolder named after Excel exists.
   - PNG count matches SKU count in Excel.
   - One ZIP file present.
3. Open one PNG and visually confirm: product name on top, color/size/price below, barcode in middle, `www.DANDYCOSMO.com` at bottom.

### Phase 9 — (Optional) Set up daily auto-run

Ask the user: "Want the system to automatically check for new Excel files daily? (y/n)"

If yes:
- **Mac:** add cron job:
  ```
  (crontab -l 2>/dev/null; echo "0 9 * * * cd <install_path> && /usr/bin/python3 watch_and_run.py >> ~/dandy-cron.log 2>&1") | crontab -
  ```
- **Windows:** create Task Scheduler entry pointing to `python.exe watch_and_run.py` daily at 9 AM.

### Phase 10 — Hand-off

Tell the user, in a single message:

```
✅ DANDY label generator installed at: <install_path>

To make new price tags:
  1. Drop Excel file in input/ folder
  2. Run: python3 watch_and_run.py
  3. Find PNGs in output/<excel_name>/

Daily auto-run: <enabled / not enabled>
```

Then stop. Do not ask follow-up questions unless the user asks.

---

## STRICT RULES

| Rule | Why |
|---|---|
| Never commit fonts/CodecPro-Regular.ttf to GitHub | Commercial license violation |
| Never modify generate_labels.py layout constants | Layout is spec-locked, will break print quality |
| Never silently fix bad Excel columns | User must know to fix the source |
| Never use a font fallback | Spec requires Codec Pro only |
| Never push to GitHub from this install | This is a downstream consumer, not a contributor |

## ERROR HANDLING

| Error | Action |
|---|---|
| `REQUIRED FONT NOT FOUND` | Re-do Phase 5. Check filename case. |
| `ModuleNotFoundError` | Re-run pip install (Phase 4) |
| `Excel missing required columns: {...}` | Tell user which file + which column. Do not fix automatically. |
| `git: command not found` | Install Git (Phase 2) |
| Push to GitHub fails | Ignore — this install does not need to push |
| Output folder permission denied | Suggest cd to a writable location and re-clone |

## SUCCESS CRITERIA

All of the following must be true before declaring success:

- [ ] `python3 watch_and_run.py` exits with code 0
- [ ] At least one PNG exists in `output/`
- [ ] PNG dimensions are 1600×1200
- [ ] Barcode renders without obvious distortion
- [ ] User confirms they can locate the output folder

## NON-GOALS

- Do not push code changes back to GitHub from this install.
- Do not modify the rendering script.
- Do not request login to the project owner's GitHub account.
- Do not enable any feature that wasn't asked for.

---

## REFERENCE — Project file structure (after install)

```
dandy-label-generator/
├── generate_labels.py        ← rendering engine (do not modify)
├── watch_and_run.py          ← orchestrator with change detection
├── requirements.txt          ← Python dependencies
├── README.md
├── OFFICE-SETUP.md           ← human-readable manual
├── INSTALL-PROMPT.md         ← this file
├── SETUP-NEW-MACHINE.md      ← legacy human guide
├── fonts/
│   ├── CodecPro-Regular.ttf  ← REQUIRED — user must provide
│   └── README.md
├── input/
│   └── *.xlsx                ← user drops Excel files here
└── output/                   ← generated PNGs end up here
    └── {excel_name}/
        ├── *.png
        └── {excel_name}.zip
```

## REFERENCE — Excel format

Required columns (exactly these names, case-sensitive):

| Product name | SKU | Color | Size | Price |
|---|---|---|---|---|
| Muscle Fit Alpha Knit Polo | MS_ALPHAPOLO_BLACK_M | BLACK | M | 1650 |

`Price` must be a number (no currency symbol). Multi-sheet workbooks are concatenated automatically.

## REFERENCE — Output spec (do not change)

- Canvas: 1600 × 1200 px (3:4 landscape, prints at 3 × 4 cm)
- Background: white
- Font: Codec Pro Regular, no fallback
- Barcode: Code 128, no quiet zone, even pixel distribution
- Footer: `www.DANDYCOSMO.com`

---

**END OF AGENT PROMPT.**
