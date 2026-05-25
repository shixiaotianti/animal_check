-- 动物识别系统数据库初始化脚本
-- Animal Recognition System - Database Schema

CREATE TABLE IF NOT EXISTS animal_check (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_path VARCHAR(255) NOT NULL,
    image_name VARCHAR(255) NOT NULL,
    detected_animals JSON,
    top_animal VARCHAR(100),
    confidence FLOAT,
    detection_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
