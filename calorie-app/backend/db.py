"""
db.py
ไฟล์สำหรับจัดการการเชื่อมต่อฐานข้อมูล MySQL

ทำงานได้ 2 โหมด:
1) รันบนเครื่องตัวเอง (XAMPP)  -> ไม่ต้องตั้งค่าอะไรเพิ่ม ใช้ค่า default ด้านล่างได้เลย
2) รันบนเซิร์ฟเวอร์จริง (เช่น Render + db4free.net) -> ตั้งค่า environment variables
   DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT ตามที่ผู้ให้บริการฐานข้อมูลให้มา
   (ดูวิธีตั้งค่าใน README.md หัวข้อ "การนำขึ้นเว็บจริง")
"""

import os
import mysql.connector
from mysql.connector import Error

# ตั้งค่าการเชื่อมต่อฐานข้อมูล
# ค่าเริ่มต้น (fallback) คือค่ามาตรฐานของ XAMPP: host=localhost, user=root, password ว่าง
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "mysql-37f0a13b-web-julong.l.aivencloud.com"),
    "user": os.environ.get("DB_USER", "avnadmin"),
    "password": os.environ.get("DB_PASSWORD", "AVNS_AB35MPIfJeHMq5mTSq6"),
    "database": os.environ.get("DB_NAME", "defaultdb"),
    "port": int(os.environ.get("DB_PORT", 16208)),
}


def get_connection():
    """สร้างและคืนค่า connection ไปยังฐานข้อมูล MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"เชื่อมต่อฐานข้อมูลไม่สำเร็จ: {e}")
        raise
