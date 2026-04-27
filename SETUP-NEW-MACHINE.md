# คู่มือติดตั้งบนเครื่องใหม่ — DANDY Label Generator

ใช้ได้ทั้ง Mac และ Windows — เวลา 15-20 นาที (ครั้งเดียว แล้วใช้ตลอด)

---

## 📋 สิ่งที่ต้องมีก่อนเริ่ม

1. ✅ เครื่องคอมที่ต่อ internet ได้
2. ✅ GitHub account (Boss = `Sakkaphong`)
3. ✅ ไฟล์ฟอนต์ **Codec Pro Regular** (`.ttf` หรือ `.otf`) — เก็บไว้ใน USB / Drive / iCloud
4. ✅ ไฟล์ Excel ของคอลเลคชั่นที่ต้องการ render

---

## 🍎 สำหรับ Mac (Mac mini / iMac / MacBook อื่น)

### Step 1: ติดตั้ง Python 3

เปิด **Terminal** → paste:

```bash
xcode-select --install
```

→ Mac จะติดตั้ง Command Line Tools (รวม Python และ Git) ใช้เวลา ~5 นาที กดยอมรับ Apple's terms

ตรวจว่าติดตั้งสำเร็จ:
```bash
python3 --version
git --version
```

ควรเห็น `Python 3.x.x` และ `git version 2.x.x`

### Step 2: ติดตั้ง GitHub Desktop (เพื่อความสะดวก)

1. https://desktop.github.com → ดาวน์โหลด macOS
2. ลาก GitHub Desktop เข้า Applications → เปิด
3. **Sign in to GitHub.com** → กรอก user/pass ของ Boss

### Step 3: Clone repo

ใน GitHub Desktop:
1. **File → Clone Repository**
2. แท็บ **GitHub.com** → จะเห็นรายการ → เลือก `Sakkaphong/dandy-label-generator`
3. Local path → ใช้ `~/Documents/GitHub/` (default) หรือเลือกที่อื่นก็ได้
4. กด **Clone**

> หรือใช้ Terminal: `git clone https://github.com/Sakkaphong/dandy-label-generator.git ~/Documents/GitHub/dandy-label-generator`

### Step 4: ติดตั้ง Python dependencies

ใน GitHub Desktop → **Repository menu → Open in Terminal** → paste:

```bash
pip3 install -r requirements.txt
```

ใช้เวลา ~1 นาที — ติดตั้ง Pillow, python-barcode, openpyxl, pandas

### Step 5: ใส่ฟอนต์ Codec Pro

1. หาไฟล์ `CodecPro-Regular.ttf` ที่ Boss เก็บไว้ (USB / Drive)
2. Copy → paste ไปที่:
   ```
   ~/Documents/GitHub/dandy-label-generator/fonts/
   ```
3. ตั้งชื่อไฟล์ให้ตรงเป๊ะ: **`CodecPro-Regular.ttf`**

> ⚠️ ถ้าเป็นเครื่องที่ทีมงานคนอื่นใช้ — ต้องมี license Codec Pro ของแต่ละคน หรือซื้อ team license

### Step 6: ใส่ Excel + ทดสอบรัน

1. ลาก Excel ไฟล์ของ Boss ไปวางใน `input/`
2. ใน Terminal:
   ```bash
   python3 watch_and_run.py
   ```
3. ผลลัพธ์ออกใน `output/` — เปิดดูป้ายได้เลย

### Step 7 (ทางเลือก): ตั้ง Cowork schedule บนเครื่องนี้ด้วย

ถ้าต้องการให้รันอัตโนมัติทุกวัน — **ผูกกับ Cowork บนเครื่องเดียวเท่านั้น** ตั้งใหม่ที่เครื่องนี้:

ใน Cowork desktop app บนเครื่องนี้ → คุยกับ Claude → บอกว่า:
> "ตั้ง scheduled task รัน DANDY label generator ทุกวัน 9 โมงเช้า ที่ path /Users/<username>/Documents/GitHub/dandy-label-generator/"

Claude จะตั้ง schedule ให้ใหม่บนเครื่องนี้

---

## 🪟 สำหรับ Windows (PC ที่ออฟฟิศ)

### Step 1: ติดตั้ง Python 3

1. https://www.python.org/downloads/windows/ → ดาวน์โหลด Python 3.11 หรือใหม่กว่า
2. รัน installer → ⚠️ **ติ๊ก ✅ "Add Python to PATH"** ก่อนกด Install
3. รอติดตั้ง ~3 นาที

ตรวจในเสร็จ — เปิด **Command Prompt** (Win+R พิมพ์ `cmd`) → paste:
```
python --version
```
ควรเห็น `Python 3.11.x`

### Step 2: ติดตั้ง Git for Windows

1. https://git-scm.com/download/win → ดาวน์โหลด
2. รัน installer → กด Next ตลอดทุกขั้น (default ดีอยู่)

### Step 3: ติดตั้ง GitHub Desktop

1. https://desktop.github.com → ดาวน์โหลด Windows
2. รัน installer → Sign in ด้วย GitHub account

### Step 4: Clone repo (เหมือน Mac)

GitHub Desktop → **File → Clone Repository** → เลือก `Sakkaphong/dandy-label-generator` → Clone

### Step 5: ติดตั้ง dependencies

GitHub Desktop → **Repository → Open in Command Prompt** → paste:

```cmd
pip install -r requirements.txt
```

### Step 6: ใส่ฟอนต์ + Excel เหมือน Mac

วาง `CodecPro-Regular.ttf` ใน `fonts/` และ Excel ใน `input/`

### Step 7: รัน

ใน Command Prompt (เปิดจาก GitHub Desktop):

```cmd
python watch_and_run.py
```

> หมายเหตุ: Windows ใช้คำสั่ง `python` ไม่ใช่ `python3`

---

## 🔄 อัปเดตจาก GitHub (ทุกครั้งก่อนใช้งาน)

ถ้า Boss แก้โค้ดที่เครื่องอื่นแล้ว push ขึ้น GitHub — เครื่องนี้ต้อง pull มาก่อนใช้:

### ใน GitHub Desktop
- เปิด repo → top toolbar → ถ้ามีอัปเดตจะเห็น **Pull origin** → กด

### ใน Terminal/Command Prompt
```bash
git pull
```

---

## 🆘 ปัญหาที่อาจเจอ

### "ModuleNotFoundError: No module named 'PIL'" (หรือ pandas, etc.)
→ Dependencies ยังไม่ถูกติดตั้ง — รัน `pip install -r requirements.txt` อีกที

### ป้ายตัวอักษรเป็น DejaVu (ไม่ใช่ Codec Pro)
→ ฟอนต์ไม่ได้อยู่ใน `fonts/` หรือชื่อไฟล์ผิด — ตรวจให้เป็น `CodecPro-Regular.ttf` เป๊ะ

### "fatal: not a git repository"
→ อยู่ผิดโฟลเดอร์ — `cd` เข้าไปใน `dandy-label-generator/` ก่อน

### Permission denied ตอน push
→ Token หมดอายุ — สร้างใหม่ที่ https://github.com/settings/tokens

### ป้ายไม่ได้ render ใหม่หลังแก้ Excel
→ ลองรันด้วย flag `--force`:
```bash
python3 watch_and_run.py --force
```

---

## 📦 สรุปสั้น — Checklist เครื่องใหม่

```
[ ] 1. ติดตั้ง Python 3
[ ] 2. ติดตั้ง Git / GitHub Desktop
[ ] 3. Clone repo: github.com/Sakkaphong/dandy-label-generator
[ ] 4. pip install -r requirements.txt
[ ] 5. วาง CodecPro-Regular.ttf ใน fonts/
[ ] 6. วาง Excel ใน input/
[ ] 7. python3 watch_and_run.py
[ ] 8. (ทางเลือก) ตั้ง Cowork schedule บนเครื่องนี้
```

ทำตาม 8 ขั้นนี้ครบ = ระบบทำงานเต็มรูปแบบบนเครื่องใหม่ทุกเครื่อง
