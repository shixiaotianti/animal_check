# 🐾 智能动物识别系统

基于 YOLOv8 深度学习模型的动物识别 Web 应用，支持实时图片上传和识别，自动保存识别历史到 MySQL 数据库。

## ✨ 功能特性

- 🖼️ **图片上传识别**：支持拖拽或点击上传图片
- 🎯 **精准识别**：使用 YOLOv8m 模型，支持 80 种常见动物识别
- 📊 **可视化结果**：在图片上标注检测到的动物及置信度
- 💾 **历史记录**：自动保存所有识别记录到 MySQL 数据库
- 🇨🇳 **中文界面**：完全中文化的用户界面
- 📱 **响应式设计**：支持桌面和移动设备访问

## 🛠️ 技术栈

- **前端界面**: Gradio
- **AI 模型**: YOLOv8 (Ultralytics)
- **数据库**: MySQL
- **编程语言**: Python 3.8+

## 📦 安装步骤

### 1. 克隆项目
```bash
git clone <你的仓库地址> 
cd 动物识别
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

#### 3.1 创建数据库和表

在 MySQL 中执行 `database.sql` 文件：


```bash
mysql -u root -p < database.sql
```

或者手动执行 SQL 语句。

#### 3.2 修改数据库配置

编辑 `config.py` 文件，修改数据库连接信息：

```python
DB_CONFIG = { 
'host': 'localhost', 
'port': 3306, 
'user': 'root', 
'password': '你的MySQL密码', # 修改这里 
'database': 'animal_recognition', 
'charset': 'utf8mb4' 
}
```

### 4. 运行应用

```bash
python app.py
```

### 5. 访问应用

打开浏览器访问：`http://127.0.0.1:7860`

## 🎮 使用说明

1. **上传图片**：点击上传区域或拖拽图片
2. **开始识别**：点击"开始识别"按钮
3. **查看结果**：
   - 左侧显示标注后的图片
   - 右侧显示识别详情（动物名称、置信度）
4. **查看历史**：页面下方显示最近的识别记录

## 🌐 部署到 Hugging Face Spaces

### 方法一：通过 GitHub 自动部署

1. 在 [Hugging Face](https://huggingface.co/) 创建账号
2. 创建新的 Space（选择 Gradio 类型）
3. 关联你的 GitHub 仓库
4. 添加 Secrets（数据库配置）
5. 自动部署完成

### 方法二：手动上传

1. 创建 Space 时选择 "Import from GitHub"
2. 或使用 Git 推送到 Space 仓库

### ⚠️ Hugging Face 部署注意事项

由于需要 MySQL 数据库，建议使用以下方案之一：

**方案 A：使用远程 MySQL 服务器**
- 将数据库部署到云服务器
- 修改 `config.py` 中的 `host` 为远程服务器地址

**方案 B：改用 SQLite（简单但性能较低）**
- 修改代码使用 SQLite 代替 MySQL
- 适合小型应用

**方案 C：使用 Hugging Face 的 PostgreSQL**
- Hugging Face Spaces 提供免费的 PostgreSQL
- 需要修改代码适配 PostgreSQL

## 📝 支持的动物类别

COCO 数据集包含以下 10 种主要动物：

| 动物 | 英文名 |
|------|--------|
| 鸟 | bird |
| 猫 | cat |
| 狗 | dog |
| 马 | horse |
| 羊 | sheep |
| 牛 | cow |
| 大象 | elephant |
| 熊 | bear |
| 斑马 | zebra |
| 长颈鹿 | giraffe |

> 注：完整 COCO 数据集包含 80 个类别，其中还包括一些动物相关物品。

## 🔧 自定义配置

### 修改模型

编辑 `config.py`：

```python
MODEL_CONFIG = { 
'model_name': 'yolov8l.pt', # 可选: n, s, m, l, x 
'confidence_threshold': 0.5, # 置信度阈值 (0-1) 
}
```

模型大小对比：
- `yolov8n`: 最快，精度最低
- `yolov8s`: 快速
- `yolov8m`: 平衡（推荐）
- `yolov8l`: 较慢，精度高
- `yolov8x`: 最慢，精度最高

### 修改端口

编辑 `app.py` 最后一行：

```python
demo.launch(server_port=8080) # 改为你想要的端口
```

## 📊 数据库表结构

**表名**: `animal_check`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| image_path | VARCHAR(500) | 图片存储路径 |
| image_name | VARCHAR(255) | 图片文件名 |
| detected_animals | TEXT | 检测结果（JSON格式） |
| top_animal | VARCHAR(100) | 主要识别结果 |
| confidence | DECIMAL(5,2) | 置信度（0-100） |
| detection_count | INT | 检测到的动物数量 |
| created_at | TIMESTAMP | 识别时间 |
| ip_address | VARCHAR(45) | 访问IP（可选） |

## ❓ 常见问题

### Q: 首次运行很慢？
A: 首次运行会自动下载 YOLOv8 模型（约 50MB），请耐心等待。

### Q: 识别不准确？
A: 可以尝试更换更大的模型（如 yolov8l 或 yolov8x）。

### Q: 数据库连接失败？
A: 检查 MySQL 服务是否启动，以及 `config.py` 中的配置是否正确。

### Q: 如何支持更多动物种类？
A: 可以使用在更大数据集（如 iNaturalist）上训练的模型。

## 📄 许可证

MIT License

## 🙏 致谢

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Gradio](https://gradio.app/)
- [COCO Dataset](https://cocodataset.org/)

---

**祝你使用愉快！** 🎉












