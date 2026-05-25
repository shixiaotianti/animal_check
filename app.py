"""
动物识别系统 - 基于 YOLOv8 和 Gradio
支持图片上传、动物识别、历史记录保存
"""

import os
import json
from datetime import datetime
from pathlib import Path

import gradio as gr
from PIL import Image
from ultralytics import YOLO
import pymysql
from config import DB_CONFIG, MODEL_CONFIG, ANIMAL_CLASSES_CN, PURE_ANIMALS

# ==================== 初始化 ====================

# 创建上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 加载 YOLO 模型
print("正在加载 YOLOv8 模型...")
model = YOLO(MODEL_CONFIG['model_name'])
print("模型加载完成！")


# ==================== 数据库操作 ====================

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


def save_to_database(image_path, image_name, detections):
    """
    保存识别结果到数据库

    Args:
        image_path: 图片路径
        image_name: 图片名称
        detections: 检测结果列表

    Returns:
        bool: 是否保存成功
    """
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # 提取主要识别结果（置信度最高的）
        if detections:
            top_detection = max(detections, key=lambda x: x['confidence'])
            top_animal = top_detection['class_cn']
            confidence = top_detection['confidence']
            detection_count = len(detections)
        else:
            top_animal = "未检测到动物"
            confidence = 0.0
            detection_count = 0

        # 将检测结果转为 JSON 字符串
        detections_json = json.dumps(detections, ensure_ascii=False)

        # 插入数据库
        sql = """
            INSERT INTO animal_check 
            (image_path, image_name, detected_animals, top_animal, confidence, detection_count)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            str(image_path),
            image_name,
            detections_json,
            top_animal,
            confidence,
            detection_count
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"保存数据库失败: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


def get_history(limit=20):
    """
    获取识别历史记录

    Args:
        limit: 返回记录数量

    Returns:
        list: 历史记录列表
    """
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM animal_check ORDER BY created_at DESC LIMIT %s"
        cursor.execute(sql, (limit,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print(f"查询历史记录失败: {e}")
        if conn:
            conn.close()
        return []


# ==================== 动物识别核心功能 ====================

# ... existing code ...
def detect_animals(image):
    """
    识别图片中的动物

    Args:
        image: PIL Image 对象或 numpy 数组

    Returns:
        tuple: (标注后的图片, 识别结果文本, 检测结果列表)
    """
    if image is None:
        return None, "请上传图片", []

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = f"animal_{timestamp}.jpg"
    image_path = UPLOAD_DIR / image_name

    if isinstance(image, Image.Image):
        image_rgb = image.convert('RGB')
        image_rgb.save(image_path)
    else:
        image_pil = Image.fromarray(image)
        image_pil.save(image_path)

    results = model(
        image_path,
        conf=MODEL_CONFIG['confidence_threshold'],
        imgsz=1280,
        augment=True,
        half=False
    )

# ... existing code ...


    # 解析结果
    detections = []
    result_text = ""

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # 获取类别信息
            class_id = int(box.cls[0])
            class_name_en = r.names[class_id]

            # 只处理动物类别
            if class_name_en in PURE_ANIMALS:
                confidence = float(box.conf[0]) * 100
                class_name_cn = ANIMAL_CLASSES_CN.get(class_name_en, class_name_en)

                detections.append({
                    'class_en': class_name_en,
                    'class_cn': class_name_cn,
                    'confidence': round(confidence, 2)
                })

    # 生成结果文本
    if detections:
        result_text = f"✅ 检测到 {len(detections)} 个动物：\n\n"
        for i, det in enumerate(detections, 1):
            result_text += f"{i}. {det['class_cn']} ({det['class_en']}) - 置信度: {det['confidence']}%\n"
    else:
        result_text = "❌ 未检测到动物（可能图片中没有动物，或动物不在 COCO 数据集的 80 种常见动物中）"

    # 在图片上绘制检测结果
    annotated_image = results[0].plot()
    annotated_image = Image.fromarray(annotated_image)

    # 保存到数据库
    save_to_database(image_path, image_name, detections)

    return annotated_image, result_text, detections


def clear_history():
    """清空识别结果"""
    return None, "请上传图片开始识别", []


# ==================== Gradio 界面 ====================

def create_interface():
    """创建 Gradio 界面"""

    with gr.Blocks(title="🐾 动物识别系统", theme=gr.themes.Soft()) as demo:

        gr.Markdown("""
        # 🐾 智能动物识别系统

        基于 YOLOv8 深度学习模型，支持识别 80 种常见动物。

        **使用方法：**
        1. 点击"上传图片"或拖拽图片到上传区域
        2. 点击"开始识别"按钮
        3. 查看识别结果和标注图片
        """)

        with gr.Row():
            # 左侧：图片上传和显示
            with gr.Column(scale=1):
                gr.Markdown("### 📷 上传图片")
                input_image = gr.Image(
                    type="pil",
                    label="选择或拖拽图片",
                    height=400
                )

                with gr.Row():
                    detect_btn = gr.Button("🔍 开始识别", variant="primary", size="lg")
                    clear_btn = gr.Button("🗑️ 清空", size="lg")

            # 右侧：识别结果
            with gr.Column(scale=1):
                gr.Markdown("### 🎯 识别结果")
                output_image = gr.Image(
                    label="标注后的图片",
                    height=400
                )
                result_text = gr.Textbox(
                    label="详细信息",
                    lines=10,
                    interactive=False
                )

        # 历史记录区域
        gr.Markdown("---")
        gr.Markdown("### 📋 最近识别记录")

        history_table = gr.DataFrame(
            headers=["时间", "图片", "识别结果", "置信度", "数量"],
            datatype=["str", "str", "str", "str", "str"],
            row_count=20,
            col_count=5,
            interactive=False,
            label="识别历史"
        )

        refresh_btn = gr.Button("🔄 刷新历史记录")

        # 事件绑定
        detect_btn.click(
            fn=detect_animals,
            inputs=input_image,
            outputs=[output_image, result_text]
        )

        clear_btn.click(
            fn=clear_history,
            outputs=[output_image, result_text]
        )

        def update_history():
            """更新历史记录表格"""
            history = get_history(limit=20)
            if not history:
                return [["暂无记录", "-", "-", "-", "-"]]

            table_data = []
            for record in history:
                time_str = record['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                table_data.append([
                    time_str,
                    record['image_name'],
                    record['top_animal'],
                    f"{record['confidence']:.2f}%",
                    str(record['detection_count'])
                ])

            return table_data

        refresh_btn.click(
            fn=update_history,
            outputs=history_table
        )

        # 页面加载时自动刷新历史记录
        demo.load(fn=update_history, outputs=history_table)

    return demo


# ==================== 启动应用 ====================

if __name__ == "__main__":
    # 检查数据库连接
    print("正在检查数据库连接...")
    test_conn = get_db_connection()
    if test_conn:
        print("✅ 数据库连接成功")
        test_conn.close()
    else:
        print("❌ 数据库连接失败，请检查 config.py 中的配置")
        print("提示：确保 MySQL 服务已启动，并已执行 database.sql 创建数据库和表")

    # 创建并启动界面
    demo = create_interface()

    print("\n" + "=" * 50)
    print("🚀 动物识别系统启动中...")
    print("=" * 50)
    print("\n请在浏览器中打开以下地址访问应用：")
    print("http://127.0.0.1:7860")
    print("\n按 Ctrl+C 可停止服务\n")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # 设为 True 可生成临时公网链接
    )
