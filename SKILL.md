---
name: ocr
description: OCR skill using DeepSeek-OCR (VLM) for intelligent text extraction with custom prompts, plus PaddleOCR for fast pure OCR. Supports 100+ languages, tables, formulas, and charts. Use when Claude needs to extract text from images, scan documents, recognize text in screenshots, or parse PDF content.
---

# OCR Skill (DeepSeek-OCR + PaddleOCR)

## How to Use (For AI)

When you need to extract text from an image or PDF, run this command:

```bash
python3 "/Users/mrshaper/Library/Application Support/com.differentai.openwork/workspaces/starter/.opencode/skills/paddle-ocr/scripts/ocr.py" "/path/to/image.png"
```

### Options
- `--prompt "custom prompt"` - Custom instruction for DeepSeek-OCR
- `--fast` or `-f` - Use PaddleOCR for faster pure text extraction
- `--json` - Output as JSON format
- `--output result.txt` - Save to file

## Overview

This skill provides dual-mode OCR capabilities:

| Mode | Engine | Use Case |
|------|--------|----------|
| **Default** | DeepSeek-OCR 3B | Smart extraction, custom prompts, understanding content |
| **Fast** (`--fast`) | PaddleOCR PP-OCRv5 | Pure text extraction, faster |

### Features
- **100+ languages** including Chinese, English, Japanese, Korean, etc.
- **Complex elements**: Tables, mathematical formulas, charts
- **Multiple formats**: PNG, JPG, PDF, BMP, GIF, WEBP, TIFF
- **Custom prompts**: Ask specific questions about image content

## Quick Start

### Basic OCR (DeepSeek-OCR)
```bash
python3 scripts/ocr.py image.png
```

### Custom Prompt
```bash
python3 scripts/ocr.py table.png --prompt "Extract this table as markdown format"
python3 scripts/ocr.py chart.png --prompt "What are the values in this chart?"
```

### Fast Mode (PaddleOCR)
```bash
python3 scripts/ocr.py image.png --fast
```

### PDF OCR
```bash
python3 scripts/ocr.py document.pdf
python3 scripts/ocr.py document.pdf --fast  # Faster but no prompts
```

### JSON Output
```bash
python3 scripts/ocr.py image.png --json > result.json
```

## Integration with Non-Vision Models

This skill gives image analysis capabilities to models that cannot process images directly (like GLM-4.7, text-only models).

### Workflow
```
Image/PDF → DeepSeek-OCR (Ollama) → Extracted Text → Main Model Analysis
```

### Example Integration
```python
import subprocess
import json

# Step 1: Extract text with custom prompt
result = subprocess.run(
    ["python3", "scripts/ocr.py", "chart.png", "--json",
     "--prompt", "Extract all data points from this chart"],
    capture_output=True, text=True,
    cwd="/path/to/paddle-ocr"
)
ocr_result = json.loads(result.stdout)
extracted_text = ocr_result["text"]

# Step 2: Pass to main model for analysis
prompt = f"""
Based on the following extracted content:

{extracted_text}

Please analyze the data and provide insights.
"""
```

## Common Use Cases

### 1. Document Digitization
```bash
python3 scripts/ocr.py scanned_document.pdf --output document.txt
```

### 2. Table Data Extraction
```bash
python3 scripts/ocr.py spreadsheet.png --prompt "Extract this table as CSV format"
```

### 3. Formula Recognition
```bash
python3 scripts/ocr.py math_problem.jpg --prompt "Extract mathematical formulas in LaTeX format"
```

### 4. Chart Analysis
```bash
python3 scripts/ocr.py bar_chart.png --prompt "List all values and labels from this chart"
```

### 5. Multi-language Document
```bash
python3 scripts/ocr.py chinese_document.png  # Auto-detects language
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |

## First-Time Setup

### 1. Install Ollama
```bash
brew install ollama
brew services start ollama
```

### 2. Download DeepSeek-OCR Model
```bash
ollama pull deepseek-ocr
```

### 3. Install Python Dependencies
```bash
pip install requests pdf2image
brew install poppler  # For PDF support
```

### 4. (Optional) Install PaddleOCR for Fast Mode
```bash
pip install paddleocr paddlepaddle
```

### 5. Verify Setup
```bash
python scripts/setup_check.py
```

## Troubleshooting

### "Cannot connect to Ollama"
```bash
brew services start ollama
```

### "DeepSeek-OCR model not found"
```bash
ollama pull deepseek-ocr
```

### "pdf2image error"
```bash
brew install poppler
pip install pdf2image
```

## Model Information

| Mode | Engine | Size | Speed |
|------|--------|------|-------|
| Default | DeepSeek-OCR 3B | 6.7 GB | ~10-30s per image |
| Fast | PaddleOCR PP-OCRv5 | ~200 MB | ~1-3s per image |

## Service Management

```bash
# Start Ollama
brew services start ollama

# Stop Ollama (free memory)
brew services stop ollama

# Check loaded models
ollama ps

# Unload model to free memory
ollama stop deepseek-ocr
```

## See Also

- [PDF Skill](../pdf/SKILL.md) - For PDF manipulation (merge, split, etc.)
- [DOCX Skill](../docx/SKILL.md) - For Word document operations
