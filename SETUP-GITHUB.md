# เอาขึ้น GitHub — คู่มือ Step-by-Step สำหรับ Boss

มี 2 วิธี เลือกอันไหนก็ได้ — แนะนำ **GitHub Desktop** ถ้าไม่ถนัด terminal

---

## วิธีที่ 1: GitHub Desktop (แนะนำ — ใช้ UI คลิก)

### Step 1 — ดาวน์โหลด GitHub Desktop
1. ไปที่ https://desktop.github.com
2. ดาวน์โหลดเวอร์ชัน **macOS** → ติดตั้ง
3. เปิดแอป → Sign in ด้วย GitHub account ของ Boss

### Step 2 — เพิ่ม project ที่ผมสร้างให้
1. ในแอป GitHub Desktop → เมนูบน → **File → Add Local Repository**
2. กด **Choose...** → เลือกโฟลเดอร์:
   ```
   /Volumes/WORK/PROJECT DANDY HOME/DANDY HOME/dandy-label-generator
   ```
3. แอปจะแจ้งว่า "This directory does not appear to be a Git repository" → กด **create a repository** (ลิงก์สีน้ำเงินในข้อความนั้น)
4. กรอก:
   - Name: `dandy-label-generator`
   - Description: `DANDY HOME — automated product label & barcode generator`
   - กด **Create Repository**

### Step 3 — ใส่ฟอนต์ Codec Pro ก่อน push
1. หาไฟล์ฟอนต์ Codec Pro Regular ที่ Boss ซื้อ license แล้ว (.ttf หรือ .otf)
2. ก๊อปวางในโฟลเดอร์ `fonts/` และ **เปลี่ยนชื่อให้เป็น** `CodecPro-Regular.ttf` ตรงเป๊ะ
3. ถ้าเป็น .otf ให้แปลงเป็น .ttf หรือแก้ใน `generate_labels.py` บรรทัด `FONT_REGULAR = FONT_DIR / "CodecPro-Regular.ttf"` ให้เป็น .otf

### Step 4 — Commit ครั้งแรก
1. กลับมาที่ GitHub Desktop → ด้านล่างซ้ายจะเห็นช่อง **Summary**
2. พิมพ์: `Initial: DANDY label & barcode generator`
3. กด **Commit to main** (ปุ่มน้ำเงินด้านล่าง)

### Step 5 — Push ขึ้น GitHub (private)
1. ที่บาร์บน → **Publish repository**
2. **ติ๊ก** ✅ "Keep this code private" — สำคัญมาก เพราะมีไฟล์ฟอนต์ที่มี license
3. กด **Publish repository**

เสร็จ — repo อยู่ที่ `https://github.com/<your-username>/dandy-label-generator`

### Step 6 — เปิด GitHub Actions (ทำให้รันอัตโนมัติบนคลาวด์)
1. ในแอป → Top-right กด **View on GitHub** (เปิด browser)
2. ไปที่ tab **Actions** → ถ้าโชว์ "Workflows aren't being run on this repository" → กด **I understand my workflows, go ahead and enable them**
3. ในเมนูซ้าย เลือก **Generate Product Labels** → ทดลองกด **Run workflow** → เลือก branch main → **Run**
4. รอ ~1 นาที — ป้ายจะถูก build เสร็จ ดาวน์โหลดเป็น artifact ได้ที่หน้า run

---

## วิธีที่ 2: Terminal (gh CLI — สำหรับคนถนัด command line)

```bash
# 1. ติดตั้ง gh (ครั้งเดียว)
brew install gh

# 2. login
gh auth login
# เลือก: GitHub.com → HTTPS → Login with a web browser

# 3. เข้าไปที่ project folder
cd "/Volumes/WORK/PROJECT DANDY HOME/DANDY HOME/dandy-label-generator"

# 4. ใส่ฟอนต์ Codec Pro ก่อน
cp ~/Downloads/CodecPro-Regular.ttf fonts/

# 5. init + commit + push (private)
git init
git add .
git commit -m "Initial: DANDY label & barcode generator"
gh repo create dandy-label-generator --private --source=. --push

# 6. เปิดใน browser
gh repo view --web
```

---

## หลัง push แล้ว — workflow อัตโนมัติทำงานยังไง

ระบบเดินอัตโนมัติ **3 ทาง** พร้อมกัน:

### A. Claude Cowork (แนะนำ — Boss ใช้ทุกวัน)
- ✅ ตั้งให้แล้ว: รันทุกวัน 09:09 น.
- ตรวจ `input/` → เจอ Excel ใหม่/แก้ไข → รัน label + barcode
- ไม่มีอัปเดต = ไม่ทำอะไร (ตามที่ Boss ขอ)

### B. GitHub Actions (สำรอง / สำหรับทีม)
- รันเองทุกวันบนคลาวด์ + เมื่อ push ไฟล์ Excel ใหม่
- ดาวน์โหลด output ได้จากหน้า Actions tab

### C. Local manual
- เปิด Terminal → `cd` ไปที่โฟลเดอร์ → `./run.sh`
- หรือ `python3 watch_and_run.py`

---

## เวลามีคอลเลคชั่นใหม่

1. เตรียม Excel ตามฟอร์แมต (5 คอลัมน์: Product name, SKU, Color, Size, Price)
2. วางใน `input/` → ตั้งชื่อไฟล์ตามชื่อคอลเลคชั่น (เช่น `Spring 2026 Polo.xlsx`)
3. ทางเลือก:
   - **รอ** — Cowork จะ auto-run พรุ่งนี้ 9 โมง
   - **รันเลย** — ใน Cowork พิมพ์ "รัน dandy-label-watch ตอนนี้"
   - **GitHub Desktop** — Commit + Push → GitHub Actions เริ่มทำงานในคลาวด์

ผลลัพธ์ออกที่ `output/Spring 2026 Polo/labels/` และ `output/Spring 2026 Polo/barcodes/`

---

## เช็คว่า scheduled task ทำงานไหม

ใน Cowork sidebar → กด **Scheduled** → เห็น task ชื่อ `dandy-label-watch`
- กด **Run now** เพื่อทดลองรันมือก่อน
- ดู log ของแต่ละรอบได้ที่นั่น
