# CalCount — เว็บไซต์คำนวณแคลอรี่

โปรเจคนี้ประกอบด้วย 3 ส่วน:

```
calorie-app/
├── frontend/          → HTML + CSS + JavaScript (หน้าเว็บ)
│   ├── index.html
│   ├── style.css
│   └── script.js
├── backend/           → Python (Flask API)
│   ├── app.py
│   ├── db.py
│   └── requirements.txt
└── database/
    └── schema.sql     → คำสั่งสร้างฐานข้อมูล MySQL
```

---

## ขั้นตอนการติดตั้งและรัน (ทำตามลำดับ)

### 1) เตรียม XAMPP และฐานข้อมูล

1. เปิดโปรแกรม **XAMPP Control Panel**
2. กด **Start** ที่บริการ **Apache** และ **MySQL**
3. เปิดเบราว์เซอร์ไปที่ `http://localhost/phpmyadmin`
4. คลิกแท็บ **SQL** ที่ด้านบน
5. เปิดไฟล์ `database/schema.sql` ด้วยโปรแกรมแก้ไขข้อความ คัดลอกโค้ดทั้งหมด
6. วางลงในช่อง SQL ของ phpMyAdmin แล้วกด **Go / ไป**
   - ขั้นตอนนี้จะสร้างฐานข้อมูลชื่อ `calorie_app` พร้อมตาราง `foods`, `user_profile`, `food_logs` และข้อมูลอาหารตัวอย่าง

> ถ้า MySQL ของคุณตั้งรหัสผ่านให้ผู้ใช้ `root` ไว้ (ปกติ XAMPP ค่าเริ่มต้นจะไม่มีรหัสผ่าน) ให้ไปแก้ไขที่ไฟล์ `backend/db.py` ตรงค่า `"password": ""` ให้ตรงกับรหัสผ่านของคุณ

### 2) ติดตั้งและรัน Backend (Python)

เปิด Terminal / Command Prompt แล้วเข้าไปที่โฟลเดอร์ `backend`:

```bash
cd calorie-app/backend
```

แนะนำให้สร้าง virtual environment ก่อน (ไม่บังคับ แต่ช่วยไม่ให้ library ปนกับโปรเจคอื่น):

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

ติดตั้ง library ที่จำเป็น:

```bash
pip install -r requirements.txt
```

รันเซิร์ฟเวอร์:

```bash
python app.py
```

ถ้าสำเร็จ จะเห็นข้อความประมาณนี้ในเทอร์มินัล:

```
 * Running on http://127.0.0.1:5000
```

**ห้ามปิดหน้าต่างเทอร์มินัลนี้** ต้องเปิดค้างไว้ตลอดเวลาที่ใช้งานเว็บไซต์ เพราะเป็นตัวที่คอยรับ-ส่งข้อมูลกับฐานข้อมูล

### 3) เปิดหน้าเว็บ (Frontend)

**อัปเดต:** ตอนนี้ Flask เสิร์ฟหน้าเว็บให้เองในตัว (เพื่อให้โค้ดชุดเดียวกันใช้ได้ทั้งตอนรันในเครื่องและตอน deploy ขึ้นเว็บจริง) ไม่ต้องเปิดไฟล์ `index.html` ตรงๆ อีกต่อไป

หลังจากรัน `python app.py` แล้ว ให้เปิดเบราว์เซอร์ไปที่:

```
http://localhost:5000
```

เท่านี้ก็จะเห็นหน้าเว็บและใช้งานได้ครบทุกฟีเจอร์เลยครับ

---

## วิธีใช้งานเว็บไซต์

1. แท็บ **คำนวณ TDEE** — กรอกเพศ น้ำหนัก ส่วนสูง อายุ และระดับกิจกรรม แล้วกด "คำนวณ" ระบบจะคำนวณ BMR และ TDEE (พลังงานที่ควรได้รับต่อวัน) และบันทึกลงฐานข้อมูลอัตโนมัติ
2. แท็บ **บันทึกอาหารวันนี้** — เลือกอาหารจากคลัง หรือกรอกชื่อ/แคลอรี่เอง ใส่ปริมาณที่กิน (กรัม) แล้วกด "เพิ่มลงบันทึก" ระบบจะคำนวณแคลอรี่ให้อัตโนมัติและรวมยอดแสดงเป็นวงกลมด้านบน
3. แท็บ **คลังอาหาร** — เพิ่มรายการอาหารใหม่เข้าฐานข้อมูล เพื่อให้เลือกใช้ซ้ำได้ในแท็บบันทึกอาหาร

---

## หลักการคำนวณที่ใช้ในโปรเจค

- **BMR (Basal Metabolic Rate)** คำนวณด้วยสูตร Mifflin-St Jeor:
  - ผู้ชาย: `BMR = 10×น้ำหนัก(กก.) + 6.25×ส่วนสูง(ซม.) − 5×อายุ + 5`
  - ผู้หญิง: `BMR = 10×น้ำหนัก(กก.) + 6.25×ส่วนสูง(ซม.) − 5×อายุ − 161`
- **TDEE (Total Daily Energy Expenditure)** = BMR × ตัวคูณระดับกิจกรรม (1.2 – 1.9)

---

## แก้ปัญหาที่พบบ่อย

| ปัญหา | สาเหตุ / วิธีแก้ |
|---|---|
| หน้าเว็บขึ้นแจ้งเตือน "เชื่อมต่อเซิร์ฟเวอร์ไม่สำเร็จ" | ตรวจสอบว่ารัน `python app.py` อยู่หรือไม่ และพอร์ต 5000 ไม่ถูกโปรแกรมอื่นใช้งานอยู่ |
| `ModuleNotFoundError: No module named 'flask'` | ยังไม่ได้ `pip install -r requirements.txt` หรือยังไม่ได้ activate venv |
| เชื่อมต่อฐานข้อมูลไม่สำเร็จ (Access denied) | รหัสผ่าน MySQL ใน `backend/db.py` ไม่ตรงกับที่ตั้งไว้ใน XAMPP |
| ตาราง/ฐานข้อมูลไม่มี | ยังไม่ได้รันไฟล์ `database/schema.sql` ใน phpMyAdmin |

---

---

## การนำขึ้นเว็บจริง (ฟรีทั้งหมด)

สถาปัตยกรรมที่ใช้:

| ส่วน | บริการ |
|---|---|
| **ฐานข้อมูล MySQL** | [db4free.net](https://www.db4free.net) |
| **Backend (Flask API)** | [Render.com](https://render.com) free tier |
| **Frontend (HTML/CSS/JS)** | [Firebase Hosting](https://firebase.google.com) free tier |

> Firebase Hosting เพียงอย่างเดียว **ไม่ต้องผูกบัตรเครดิต** เพราะเป็นแค่การเสิร์ฟไฟล์ static (html/css/js) ส่วนที่ต้องใช้บัตร (Cloud Functions) เราไม่ได้ใช้ในแผนนี้ เพราะให้ Render เป็นคนรัน backend แทน

### ขั้นตอนที่ 1: ฐานข้อมูล (db4free.net)

เหมือนเดิมตามหัวข้อก่อนหน้า: สมัคร [db4free.net](https://www.db4free.net) → รันคำสั่งใน `database/schema.sql` ผ่าน phpMyAdmin ของ db4free (ข้ามส่วน `CREATE DATABASE`/`USE` เพราะมีฐานข้อมูลให้แล้ว)

### ขั้นตอนที่ 2: Backend (Render)

1. อัปโหลดโฟลเดอร์ `calorie-app` ขึ้น GitHub
2. สมัคร [render.com](https://render.com) (ไม่ต้องใช้บัตรเครดิต) → **New +** → **Web Service** → เลือก repo
3. ตั้งค่า:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free
4. เพิ่ม Environment Variables: `DB_HOST=db4free.net`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT=3306` (ตามที่ตั้งไว้กับ db4free.net)
5. กด **Create Web Service** รอสักครู่ จะได้ URL แบบ `https://ชื่อโปรเจค.onrender.com` — **คัดลอกลิงก์นี้เก็บไว้**

### ขั้นตอนที่ 3: แก้ไฟล์ frontend ให้ชี้ไปที่ backend

เปิดไฟล์ `frontend/script.js` แก้บรรทัดนี้:

```javascript
const RENDER_BACKEND_URL = "https://YOUR-APP-NAME.onrender.com"; // <-- แก้ตรงนี้!
```

เปลี่ยนเป็นลิงก์ Render ที่ได้จากขั้นตอนที่ 2 เช่น:

```javascript
const RENDER_BACKEND_URL = "https://calcount-api.onrender.com";
```

### ขั้นตอนที่ 4: Frontend (Firebase Hosting)

1. ติดตั้ง Node.js จาก [nodejs.org](https://nodejs.org) ถ้ายังไม่มี (ใช้แค่เพื่อรันเครื่องมือ Firebase CLI)
2. เปิด terminal แล้วติดตั้ง Firebase CLI:
   ```bash
   npm install -g firebase-tools
   ```
3. ล็อกอิน Firebase ด้วยบัญชี Google:
   ```bash
   firebase login
   ```
4. เข้าไปที่โฟลเดอร์โปรเจค (`calorie-app` ที่มีไฟล์ `firebase.json` อยู่แล้ว):
   ```bash
   cd calorie-app
   firebase init hosting
   ```
   - เลือก **Use an existing project** แล้วสร้างโปรเจคใหม่ที่ [console.firebase.google.com](https://console.firebase.google.com) ก่อน (ฟรี ไม่ต้องผูกบัตร) หรือเลือกสร้างระหว่างขั้นตอนนี้ก็ได้
   - พอถามว่า "What do you want to use as your public directory?" → ตอบ `frontend`
   - พอถามว่า "Configure as a single-page app?" → ตอบ `Yes`
   - ถ้าถามว่าจะเขียนทับ `frontend/index.html` ไหม → ตอบ **No** (ไม่งั้นไฟล์เดิมจะหาย)
5. Deploy ขึ้นเว็บจริง:
   ```bash
   firebase deploy --only hosting
   ```
6. เสร็จแล้วจะได้ลิงก์แบบ `https://ชื่อโปรเจค.web.app` เปิดดูได้เลย นี่คือลิงก์ที่ส่งให้คุณครูดู

### ถ้าแก้โค้ดเพิ่มทีหลัง

- แก้ backend (`app.py`, `db.py`) → push ขึ้น GitHub, Render จะ deploy ให้อัตโนมัติ
- แก้ frontend (`index.html`, `style.css`, `script.js`) → รัน `firebase deploy --only hosting` ใหม่อีกครั้ง

### แก้ปัญหาที่พบบ่อยตอน deploy

| ปัญหา | สาเหตุ / วิธีแก้ |
|---|---|
| หน้าเว็บ Firebase โหลดได้ แต่กดคำนวณ/บันทึกอาหารไม่ได้ | เช็คว่าแก้ `RENDER_BACKEND_URL` ใน `script.js` ถูกต้อง และ deploy ใหม่แล้วหรือยัง |
| เปิดครั้งแรกช้ามาก | ปกติของ Render free tier ที่ "หลับ" เมื่อไม่มีคนเข้า 15 นาที รอ 30-60 วิ ครั้งแรกเท่านั้น |
| CORS error ใน Console (F12) | ตรวจสอบว่า backend มี `CORS(app)` อยู่ใน `app.py` (มีอยู่แล้วในโค้ดชุดนี้) |

## ต่อยอดเพิ่มเติม (ถ้าต้องการทำเป็นโปรเจคที่สมบูรณ์ขึ้น)

- เพิ่มระบบสมัครสมาชิก/เข้าสู่ระบบ เพื่อรองรับผู้ใช้หลายคน
- เพิ่มกราฟแสดงแนวโน้มแคลอรี่ย้อนหลัง 7 วัน
- เพิ่มการแยกหมวดหมู่อาหาร (อาหารเช้า/กลางวัน/เย็น/ของว่าง)
