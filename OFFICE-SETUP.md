# 📦 ระบบสร้างป้าย DANDY COSMO — คู่มือติดตั้งที่ออฟฟิศ

> **เอกสารนี้สำหรับ:** พนักงานออฟฟิศ DANDY ที่จะติดตั้งระบบทำป้ายราคาบนเครื่องคอมพิวเตอร์ของออฟฟิศ
>
> **เวลาที่ใช้:** 15-20 นาที (ทำครั้งเดียว ใช้ตลอด)

---

## 🎯 ระบบนี้คืออะไร

ระบบสร้าง **ป้ายราคาสินค้า + Barcode** อัตโนมัติจากไฟล์ Excel

- ใส่ Excel ที่มีรายการสินค้า → ได้ภาพ PNG พร้อมปริ้น
- ป้ายขนาด **3×4 cm** มี Barcode สแกนได้จริง
- ทุกป้ายเป๊ะเหมือนกันทุกตัว — ตัวอักษร Codec Pro ตำแหน่งเป๊ะ
- **1 SKU = 1 ภาพ PNG** → รวม ZIP ส่งโรงปริ้นได้

---

## 📋 ก่อนเริ่ม — สิ่งที่คุณต้องได้รับจากคุณเก่ง (Boss)

| ลำดับ | สิ่งที่ต้องได้ | ทางที่รับ |
|---|---|---|
| 1 | **ไฟล์ฟอนต์ Codec Pro Regular** (.ttf) | LINE / Email / Drive |
| 2 | **ไฟล์ Excel สินค้า** (.xlsx) | LINE / Email / Drive |
| 3 | (ทางเลือก) GitHub username + token | ถ้าต้องการ pull/push code |

> ⚠️ **ห้าม** ส่งฟอนต์ Codec Pro ต่อให้คนนอก หรืออัปโหลดไปเว็บสาธารณะ (ละเมิด license)

---

## 🍎 ติดตั้งบน Mac

### Step 1: ติดตั้ง Python และ Git (ใช้คำสั่งเดียว)

เปิด **Terminal** (Cmd+Space → พิมพ์ Terminal → Enter) → paste บรรทัดนี้:

```bash
xcode-select --install
```

→ Mac จะ popup ให้กด **Install** → รอ ~5 นาที

ตรวจว่าสำเร็จ:
```bash
python3 --version
```
ควรเห็น `Python 3.x.x`

### Step 2: ติดตั้ง GitHub Desktop

1. เปิด browser → https://desktop.github.com
2. กด **Download for macOS** → ติดตั้ง
3. เปิดแอป → **Sign in to GitHub.com** ด้วย account ออฟฟิศ
   > (ใช้ account ใครก็ได้ — ไม่ต้องเป็น account คุณเก่ง)

### Step 3: Clone repo จาก GitHub

ใน GitHub Desktop:
1. **File → Clone Repository**
2. แท็บ **URL** → paste:
   ```
   https://github.com/Sakkaphong/dandy-label-generator
   ```
3. Local path → ใช้ default `~/Documents/GitHub/dandy-label-generator`
4. กด **Clone** → รอ ~30 วินาที

### Step 4: ติดตั้ง Python libraries

ใน GitHub Desktop → เมนูบน **Repository → Open in Terminal** → paste:

```bash
pip3 install -r requirements.txt
```

→ รอ ~1-2 นาที

### Step 5: ใส่ฟอนต์ Codec Pro

1. หาไฟล์ `CodecPro-Regular.ttf` ที่ได้รับจากคุณเก่ง
2. เปิด Finder → ไปที่ `~/Documents/GitHub/dandy-label-generator/fonts/`
3. ลากไฟล์ฟอนต์ไปวางในนั้น
4. ⚠️ **ตรวจชื่อไฟล์** — ต้องเป็น `CodecPro-Regular.ttf` เป๊ะ (case-sensitive)

### Step 6: ใส่ไฟล์ Excel

1. หา `*.xlsx` ที่ได้รับจากคุณเก่ง
2. ลากไปวางใน `~/Documents/GitHub/dandy-label-generator/input/`

### Step 7: รันระบบ

ใน Terminal (ที่เปิดจาก GitHub Desktop):

```bash
python3 watch_and_run.py
```

→ ระบบจะสร้างป้ายให้ทุก SKU ใน Excel

ผลลัพธ์อยู่ที่:
```
~/Documents/GitHub/dandy-label-generator/output/
└── {ชื่อ Excel}/
    ├── SKU1.png
    ├── SKU2.png
    ├── ...
    └── {ชื่อ Excel}.zip
```

ดับเบิลคลิก ZIP เพื่อแตกไฟล์ → ส่งโรงปริ้นได้

---

## 🪟 ติดตั้งบน Windows

### Step 1: ติดตั้ง Python

1. https://www.python.org/downloads/ → กด **Download Python 3.11+**
2. รัน installer
3. ⚠️ **สำคัญ** — ติ๊ก ✅ **"Add Python to PATH"** ก่อนกด Install
4. กด **Install Now** → รอ ~3 นาที

ตรวจ — เปิด **Command Prompt** (Win+R พิมพ์ `cmd` → Enter) → paste:
```
python --version
```

### Step 2: ติดตั้ง Git for Windows

https://git-scm.com/download/win → ดาวน์โหลด → ติดตั้ง (กด Next ตลอด)

### Step 3: ติดตั้ง GitHub Desktop

https://desktop.github.com → ดาวน์โหลด Windows → Sign in

### Step 4-7: เหมือน Mac

แค่เปลี่ยน:
- `python3` → `python` (Windows ใช้แค่ python)
- `pip3` → `pip`

---

## 📅 การใช้งานประจำวัน

### เมื่อมีคอลเลคชั่นใหม่

1. **คุณเก่งส่ง Excel ใหม่** มาทาง LINE / Drive
2. **ลากไปวาง** ใน folder `input/`
3. **รัน:** เปิด Terminal → `python3 watch_and_run.py`
4. **ป้ายใหม่ออกใน folder** `output/{ชื่อ Excel}/`
5. **ส่ง ZIP ให้โรงปริ้น** หรือปริ้นเอง

### เมื่อมีอัปเดตโค้ดจาก GitHub

ถ้าคุณเก่งแก้โค้ดที่ฝั่งของคุณเก่งและ push ขึ้น GitHub แล้ว — ที่ออฟฟิศต้อง pull มาก่อน:

ใน GitHub Desktop:
- เปิดแอป → ปุ่มบน **"Fetch origin"** → ถ้ามีอัปเดตจะเห็นเลข
- กด **Pull origin** → รอ 5 วินาที → จบ

---

## 🆘 ปัญหาที่อาจเจอ

### ❌ `REQUIRED FONT NOT FOUND`
**สาเหตุ:** ไฟล์ฟอนต์ไม่อยู่ใน `fonts/` หรือชื่อผิด
**แก้:** ตรวจชื่อไฟล์เป็น `CodecPro-Regular.ttf` เป๊ะ (มีขีด `-` ตัว `R` ใหญ่)

### ❌ `ModuleNotFoundError: No module named 'PIL'`
**สาเหตุ:** Python libraries ยังไม่ติดตั้ง
**แก้:**
```bash
pip3 install -r requirements.txt
```

### ❌ `Excel missing required columns`
**สาเหตุ:** ไฟล์ Excel มีหัวคอลัมน์ผิด
**แก้:** ต้องมี 5 คอลัมน์ ชื่อตรงเป๊ะ (case-sensitive):

| Product name | SKU | Color | Size | Price |
|---|---|---|---|---|

### ❌ ป้ายไม่ออก / ไม่อัปเดต ทั้งที่แก้ Excel
**สาเหตุ:** ระบบ cache คิดว่าไฟล์ยังเหมือนเดิม
**แก้:** บังคับให้รันใหม่ทุกไฟล์
```bash
python3 watch_and_run.py --force
```

### ❌ Barcode สแกนไม่ขึ้น
**สาเหตุ:** ปริ้นเล็กเกินไป หรือคุณภาพปริ้นต่ำ
**แก้:**
1. ปริ้นที่ขนาด **4 cm กว้าง × 3 cm สูง** เป๊ะ (ห้ามย่อ)
2. ใช้กระดาษคุณภาพดี (ไม่ใช่กระดาษมัน)
3. ปริ้นที่ DPI สูง (≥600 DPI)

---

## 📞 ติดต่อคุณเก่ง (Boss)

ถ้าติดปัญหาที่แก้ไม่ได้ — ส่ง:
1. **Screenshot ของ error** ที่ Terminal
2. **ชื่อ Excel** ที่กำลังรัน
3. **คำสั่งที่พิมพ์ก่อน error**

---

## ✅ Checklist ติดตั้งเครื่องใหม่

```
[ ] 1. ติดตั้ง Python 3 (xcode-select --install บน Mac)
[ ] 2. ติดตั้ง GitHub Desktop + Sign in
[ ] 3. Clone repo จาก github.com/Sakkaphong/dandy-label-generator
[ ] 4. รัน pip3 install -r requirements.txt
[ ] 5. รับฟอนต์ Codec Pro จากคุณเก่ง → วางใน fonts/
[ ] 6. รับ Excel จากคุณเก่ง → วางใน input/
[ ] 7. ทดลองรัน python3 watch_and_run.py
[ ] 8. เช็คผลลัพธ์ที่ output/ → ป้ายขึ้น = สำเร็จ ✓
```

---

## 🎁 Bonus — ตั้งให้รันอัตโนมัติทุกวัน (ทางเลือก)

ถ้าต้องการให้ระบบเช็ค Excel ใหม่อัตโนมัติทุกวัน — ตั้ง **Cron Job** บน Mac:

```bash
crontab -e
```

เพิ่มบรรทัดนี้:
```
0 9 * * * cd ~/Documents/GitHub/dandy-label-generator && /usr/bin/python3 watch_and_run.py >> ~/dandy-cron.log 2>&1
```

→ ระบบจะรันอัตโนมัติทุกวัน 9 โมงเช้า ไม่ต้องเปิด Terminal เอง

---

**📌 สรุป:** ระบบนี้คือ Excel → ป้าย PNG → ZIP → ปริ้น

มีคอลเลคชั่นใหม่เมื่อไหร่ — ลาก Excel ใส่ folder + รัน 1 คำสั่ง = เสร็จ
