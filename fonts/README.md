# Fonts directory

⚠️ **This folder is intentionally empty in the GitHub repo.**

`.gitignore` blocks all `.ttf` / `.otf` files from being uploaded — Codec Pro is a commercial font with a paid license, and uploading it (even to a private repo) violates the license unless every team member has their own seat.

## What you need to do

1. Buy or already own Codec Pro Regular from https://www.solpera.com/typefaces/codec-pro (or Monotype)
2. Drop your licensed font file in this folder, named exactly:
   ```
   fonts/CodecPro-Regular.ttf
   ```
3. The file stays on your machine only — never gets pushed to GitHub.

## Distributing to teammates

For DANDY HOME team members who need to run the generator:
- Send the font file via private channel (LINE, AirDrop, password-protected Drive folder)
- Each person places it in their local `fonts/` folder
- Or buy additional seats for each user (recommended for compliance)

## Without the font

The script falls back to DejaVu Sans and prints a warning. Output works for testing but typography will not match DANDY brand standards.

