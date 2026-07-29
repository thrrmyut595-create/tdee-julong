-- ==========================================================
-- schema.sql
-- ฐานข้อมูลสำหรับเว็บไซต์คำนวณแคลอรี่
-- นำไฟล์นี้ไปรันใน phpMyAdmin (XAMPP) เพื่อสร้างฐานข้อมูลและตาราง
-- ==========================================================

CREATE DATABASE IF NOT EXISTS calorie_app
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE calorie_app;

-- ----------------------------------------------------------
-- ตาราง foods : เก็บรายการอาหารและแคลอรี่ต่อ 100 กรัม
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS foods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    calories_per_100g DECIMAL(7,2) NOT NULL,   -- แคลอรี่ต่อ 100 กรัม
    protein_g DECIMAL(6,2) DEFAULT 0,          -- โปรตีน (กรัม) ต่อ 100 กรัม
    fat_g DECIMAL(6,2) DEFAULT 0,              -- ไขมัน (กรัม) ต่อ 100 กรัม
    carb_g DECIMAL(6,2) DEFAULT 0,             -- คาร์โบไฮเดรต (กรัม) ต่อ 100 กรัม
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------
-- ตาราง user_profile : เก็บข้อมูลร่างกายล่าสุดที่ใช้คำนวณ BMR/TDEE
-- (โปรเจคนี้เป็นแบบผู้ใช้คนเดียว ไม่มีระบบ login)
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gender ENUM('male','female') NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    height_cm DECIMAL(5,2) NOT NULL,
    age INT NOT NULL,
    activity_level VARCHAR(30) NOT NULL,   -- sedentary, light, moderate, active, very_active
    bmr DECIMAL(7,2) NOT NULL,
    tdee DECIMAL(7,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------
-- ตาราง food_logs : บันทึกรายการอาหารที่กินในแต่ละวัน
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS food_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_id INT NULL,
    food_name VARCHAR(150) NOT NULL,
    amount_g DECIMAL(7,2) NOT NULL,
    calories DECIMAL(8,2) NOT NULL,
    log_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ----------------------------------------------------------
-- ข้อมูลตัวอย่าง: รายการอาหารเริ่มต้น
-- ----------------------------------------------------------
INSERT INTO foods (name, calories_per_100g, protein_g, fat_g, carb_g) VALUES
('ข้าวสวย', 130.00, 2.70, 0.30, 28.00),
('ข้าวเหนียว', 160.00, 3.50, 0.60, 35.00),
('ไข่ไก่ต้ม', 155.00, 13.00, 11.00, 1.10),
('อกไก่ย่าง', 165.00, 31.00, 3.60, 0.00),
('หมูสามชั้นทอด', 500.00, 14.00, 49.00, 0.00),
('ผัดผักบุ้งไฟแดง', 90.00, 3.00, 6.00, 5.00),
('ส้มตำ', 65.00, 2.00, 0.50, 12.00),
('ต้มยำกุ้ง', 55.00, 6.00, 2.00, 3.00),
('กล้วยน้ำว้า', 89.00, 1.10, 0.30, 22.80),
('น้ำอัดลม', 42.00, 0.00, 0.00, 10.60);
