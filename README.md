# OpenCode OCR Skill

> 让无视觉能力的大模型也能"看"图片 — OpenCode/OpenWork AI OCR Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenCode](https://img.shields.io/badge/OpenCode-Skill-blue)](https://opencode.ai)
[![DeepSeek-OCR](https://img.shields.io/badge/DeepSeek--OCR-3B-green)](https://github.com/deepseek-ai/DeepSeek-OCR)

## 简介

这是一个 **OpenCode/OpenWork** 的 OCR Skill，使用 **DeepSeek-OCR 3B** (通过 Ollama) 为无视觉能力的大模型（如 GLM-4.7）提供图像识别能力。

### 双模式设计

| 模式 | 引擎 | 用途 |
|------|------|------|
| **默认** | DeepSeek-OCR 3B | 智能提取，支持自定义 prompt |
| **快速** (`--fast`) | PaddleOCR PP-OCRv5 | 纯文字提取，更快速 |

### 特性

- **超强 OCR**: DeepSeek-OCR 在 OCRBench 上得分 834（超越 GPT-4o 的 736）
- **多语言**: 支持 100+ 种语言
- **多格式**: 图片 (PNG/JPG/BMP/GIF/WEBP/TIFF) + PDF
- **自定义 prompt**: 可以问图片内容相关的问题
- **自动压缩**: 大图片自动缩放到 1536px，避免超时
- **本地运行**: 完全离线，数据安全

## 工作原理

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ 图片/PDF    │────▶│ DeepSeek-OCR     │────▶│ 主模型分析      │
│             │     │ (本地 Ollama)    │     │ (GLM-4.7 等)    │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

## 快速开始

### 1. 安装环境

```bash
# 安装 Ollama
brew install ollama
brew services start ollama

# 下载 DeepSeek-OCR 模型 (约 6.7GB)
ollama pull deepseek-ocr

# 安装 Python 依赖
pip install requests pdf2image
brew install poppler

# (可选) 安装 PaddleOCR 快速模式
pip install paddleocr paddlepaddle
```

### 2. 安装 Skill

```bash
# 克隆到 OpenWork Skills 目录
cd ~/Library/Application\ Support/com.differentai.openwork/workspaces/starter/.opencode/skills
git clone https://github.com/mr-shaper/opencode-skill-hybrid-ocr.git paddle-ocr
```

### 3. 使用

```bash
cd paddle-ocr

# 默认模式 (DeepSeek-OCR)
python3 scripts/ocr.py image.png

# 自定义 prompt
python3 scripts/ocr.py table.png --prompt "提取表格为 markdown 格式"
python3 scripts/ocr.py chart.png --prompt "这个图表的数据是什么？"

# 快速模式 (PaddleOCR)
python3 scripts/ocr.py image.png --fast

# PDF OCR
python3 scripts/ocr.py document.pdf

# JSON 输出
python3 scripts/ocr.py image.png --json

# 保存到文件
python3 scripts/ocr.py doc.pdf --output result.txt
```

## 目录结构

```
paddle-ocr/
├── SKILL.md              # OpenCode Skill 主文档
├── README.md             # GitHub 说明
├── 部署说明.md            # 详细部署指南
├── .gitignore
├── .env.example
└── scripts/
    ├── ocr.py            # 核心 OCR 脚本 (双模式)
    ├── setup_check.py    # 环境检查
    └── requirements.txt
```

## 环境检查

```bash
python3 scripts/setup_check.py
```

预期输出:
```
--- Core Requirements (DeepSeek-OCR) ---
[OK] Ollama installed
[OK] Ollama server is running
[OK] DeepSeek-OCR model installed
[OK] requests installed

--- Optional: Fast Mode (PaddleOCR) ---
[OK] PaddleOCR installed

--- Quick DeepSeek-OCR Test ---
[OK] DeepSeek-OCR test passed

All core checks passed!
```

## 资源占用

| 状态 | Ollama 服务 | DeepSeek-OCR |
|------|-------------|--------------|
| 空闲 | ~30MB | 未加载 |
| 首次调用 | ~30MB | 加载模型 ~6GB |
| 推理中 | ~30MB | ~6-8GB |
| 推理完成 | ~30MB | 保持加载 |

### 服务管理

```bash
# 启动 Ollama
brew services start ollama

# 停止 Ollama（释放内存）
brew services stop ollama

# 查看已加载模型
ollama ps

# 卸载模型释放内存
ollama stop deepseek-ocr
```

## 代码集成示例

```python
import subprocess
import json

# 调用 OCR（支持自定义 prompt）
result = subprocess.run(
    ["python3", "scripts/ocr.py", "chart.png", "--json",
     "--prompt", "提取图表中的所有数据"],
    capture_output=True, text=True,
    cwd="/path/to/paddle-ocr"
)

# 解析结果
ocr_data = json.loads(result.stdout)
extracted_text = ocr_data["text"]

# 传给主模型
prompt = f"分析以下从图片提取的内容:\n{extracted_text}"
```

## 模型对比

| 对比项 | DeepSeek-OCR 3B | PaddleOCR PP-OCRv5 |
|--------|-----------------|-------------------|
| 类型 | VLM (视觉语言模型) | 传统 OCR |
| 大小 | 6.7 GB | ~200 MB |
| 速度 | 10-30秒/图 | 1-3秒/图 |
| 自定义 prompt | ✅ 支持 | ❌ 不支持 |
| OCRBench | 834 | - |
| 使用场景 | 需要理解内容 | 纯文字提取 |

## 自动图片压缩

大图片（超过 1536px）会自动缩放以避免处理超时：

```
原图: 6144x3429
自动缩放: 1536x857
```

- 保持宽高比
- JPEG 质量 90%
- 处理完自动删除临时文件

## 常见问题

### Ollama 无法连接？
```bash
brew services start ollama
```

### 模型未找到？
```bash
ollama pull deepseek-ocr
```

### PDF 处理失败？
```bash
brew install poppler
pip install pdf2image
```

### 想释放内存？
```bash
brew services stop ollama
# 或只卸载模型
ollama stop deepseek-ocr
```

## 相关链接

- [DeepSeek-OCR GitHub](https://github.com/deepseek-ai/DeepSeek-OCR)
- [DeepSeek-OCR HuggingFace](https://huggingface.co/deepseek-ai/DeepSeek-OCR)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [Ollama](https://ollama.ai)
- [OpenCode](https://opencode.ai)

## License

MIT License

---

Made with ❤️ for OpenCode/OpenWork community
