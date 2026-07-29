"""
app.py
Backend หลักของเว็บไซต์คำนวณแคลอรี่ (Flask + MySQL)

วิธีรัน:
    python app.py
เซิร์ฟเวอร์จะรันที่ http://localhost:5000
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import date
from db import get_connection

# ให้ Flask เสิร์ฟไฟล์ frontend (html/css/js) เองในตัว
# วิธีนี้ทำให้เว็บทั้งหมดอยู่ URL เดียว ไม่ต้องกังวลเรื่อง CORS ตอน deploy จริง
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)  # เผื่อกรณีเปิด frontend จากคนละ origin ตอนพัฒนา


@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# ==========================================================
# ฟังก์ชันคำนวณ BMR และ TDEE
# ==========================================================
ACTIVITY_FACTORS = {
    "sedentary": 1.2,       # นั่งทำงาน ไม่ค่อยออกกำลังกาย
    "light": 1.375,         # ออกกำลังกายเบา 1-3 วัน/สัปดาห์
    "moderate": 1.55,       # ออกกำลังกายปานกลาง 3-5 วัน/สัปดาห์
    "active": 1.725,        # ออกกำลังกายหนัก 6-7 วัน/สัปดาห์
    "very_active": 1.9,     # ออกกำลังกายหนักมาก / ใช้แรงงาน
}


def calculate_bmr(gender, weight_kg, height_cm, age):
    """คำนวณ BMR ด้วยสูตร Mifflin-St Jeor"""
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


# ==========================================================
# API: คำนวณ BMR / TDEE และบันทึกลงฐานข้อมูล
# ==========================================================
@app.route("/api/calculate-bmr", methods=["POST"])
def calculate_bmr_route():
    data = request.get_json()

    try:
        gender = data["gender"]
        weight_kg = float(data["weight_kg"])
        height_cm = float(data["height_cm"])
        age = int(data["age"])
        activity_level = data["activity_level"]
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "ข้อมูลไม่ถูกต้อง กรุณากรอกให้ครบและถูกต้อง"}), 400

    if activity_level not in ACTIVITY_FACTORS:
        return jsonify({"error": "ระดับกิจกรรมไม่ถูกต้อง"}), 400

    bmr = calculate_bmr(gender, weight_kg, height_cm, age)
    tdee = bmr * ACTIVITY_FACTORS[activity_level]

    # บันทึกผลลัพธ์ลงฐานข้อมูล
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO user_profile
           (gender, weight_kg, height_cm, age, activity_level, bmr, tdee)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (gender, weight_kg, height_cm, age, activity_level, bmr, tdee),
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "bmr": round(bmr, 2),
        "tdee": round(tdee, 2),
    })


@app.route("/api/user-profile/latest", methods=["GET"])
def get_latest_profile():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM user_profile ORDER BY created_at DESC LIMIT 1"
    )
    profile = cursor.fetchone()
    cursor.close()
    conn.close()

    if not profile:
        return jsonify(None)

    profile["weight_kg"] = float(profile["weight_kg"])
    profile["height_cm"] = float(profile["height_cm"])
    profile["bmr"] = float(profile["bmr"])
    profile["tdee"] = float(profile["tdee"])
    profile["created_at"] = str(profile["created_at"])
    return jsonify(profile)


# ==========================================================
# API: รายการอาหารทั้งหมด
# ==========================================================
@app.route("/api/foods", methods=["GET"])
def get_foods():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM foods ORDER BY name ASC")
    foods = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(foods)


@app.route("/api/foods", methods=["POST"])
def add_food():
    data = request.get_json()
    try:
        name = data["name"]
        calories_per_100g = float(data["calories_per_100g"])
        protein_g = float(data.get("protein_g", 0))
        fat_g = float(data.get("fat_g", 0))
        carb_g = float(data.get("carb_g", 0))
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "ข้อมูลอาหารไม่ถูกต้อง"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO foods (name, calories_per_100g, protein_g, fat_g, carb_g)
           VALUES (%s, %s, %s, %s, %s)""",
        (name, calories_per_100g, protein_g, fat_g, carb_g),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": new_id, "message": "เพิ่มอาหารสำเร็จ"}), 201


# ==========================================================
# API: บันทึกอาหารที่กิน (food log)
# ==========================================================
@app.route("/api/food-logs", methods=["POST"])
def add_food_log():
    data = request.get_json()
    try:
        food_id = data.get("food_id")
        food_name = data["food_name"]
        amount_g = float(data["amount_g"])
        calories_per_100g = float(data["calories_per_100g"])
        log_date = data.get("log_date", str(date.today()))
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "ข้อมูลบันทึกอาหารไม่ถูกต้อง"}), 400

    calories = (calories_per_100g * amount_g) / 100

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO food_logs (food_id, food_name, amount_g, calories, log_date)
           VALUES (%s, %s, %s, %s, %s)""",
        (food_id, food_name, amount_g, calories, log_date),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"id": new_id, "calories": round(calories, 2)}), 201


@app.route("/api/food-logs", methods=["GET"])
def get_food_logs():
    log_date = request.args.get("date", str(date.today()))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM food_logs WHERE log_date = %s ORDER BY created_at DESC",
        (log_date,),
    )
    logs = cursor.fetchall()

    cursor.execute(
        "SELECT COALESCE(SUM(calories), 0) AS total FROM food_logs WHERE log_date = %s",
        (log_date,),
    )
    total = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    # แปลง Decimal เป็น float เพื่อให้ jsonify ทำงานได้ถูกต้อง
    for log in logs:
        log["amount_g"] = float(log["amount_g"])
        log["calories"] = float(log["calories"])
        log["log_date"] = str(log["log_date"])
        log["created_at"] = str(log["created_at"])

    return jsonify({"logs": logs, "total_calories": round(float(total), 2)})


@app.route("/api/food-logs/<int:log_id>", methods=["DELETE"])
def delete_food_log(log_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food_logs WHERE id = %s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "ลบรายการสำเร็จ"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
