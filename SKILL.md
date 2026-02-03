---
name: paddle-ocr
description: OCR skill using PaddleOCR (Native Python) for text extraction from images and PDFs. Supports 100+ languages, tables, formulas, and charts. Use when Claude needs to extract text from images, scan documents, recognize text in screenshots, or parse PDF content that requires OCR.
---

# PaddleOCR-VL OCR Skill

## How to Use (For AI)

When you need to extract text from an image or PDF, run this command:

```bash
python3 ~/.opencode/skills/paddle-ocr/scripts/ocr.py "/absolute/path/to/image.png"
```

Or with the full path:
```bash
python3 "/Users/mrshaper/Library/Application Support/com.differentai.openwork/workspaces/starter/.opencode/skills/paddle-ocr/scripts/ocr.py" "/path/to/image.png"
```

### Options
- `--json` - Output as JSON format
- `--prompt "custom prompt"` - Custom OCR instruction
- `--output result.txt` - Save to file

## Overview

This skill provides OCR (Optical Character Recognition) capabilities using native PaddleOCR (PP-OCRv5). It enables text extraction from images and PDFs, with support for:

- **100+ languages** including Chinese, English, Japanese, Korean, etc.
- **Complex elements**: Tables, mathematical formulas, charts
- **Multiple formats**: PNG, JPG, PDF, BMP, GIF, WEBP, TIFF
- **No external service**: Runs entirely locally via Python

## Quick Start

### Single Image OCR
```bash
python3 scripts/ocr.py image.png
```

### PDF Document OCR
```bash
python scripts/ocr.py document.pdf
```

### Custom Prompt (Table Extraction)
```bash
python scripts/ocr.py table.png --prompt "Extract the table data and format as markdown"
```

### JSON Output
```bash
python scripts/ocr.py image.png --json > result.json
```

### Save to File
```bash
python scripts/ocr.py document.pdf --output extracted_text.txt
```

## Integration with Non-Vision Models

This skill is designed to give image analysis capabilities to models that cannot process images directly (like GLM-4.7, text-only models, etc.).

### Workflow
```
Image/PDF → PaddleOCR (Native Python) → Extracted Text → Main Model Analysis
```

### Example Integration
```python
import subprocess
import json

# Step 1: Extract text from image
result = subprocess.run(
    ["python3", "scripts/ocr.py", "chart.png", "--json"],
    capture_output=True, text=True
)
ocr_result = json.loads(result.stdout)
extracted_text = ocr_result["text"]

# Step 2: Pass to main model for analysis
prompt = f"""
Based on the following OCR-extracted content:

{extracted_text}

Please analyze the data and provide insights.
"""
```

## Common Use Cases

### 1. Document Digitization
```bash
python scripts/ocr.py scanned_document.pdf --output document.txt
```

### 2. Table Data Extraction
```bash
python scripts/ocr.py spreadsheet.png --prompt "Extract the table as CSV format"
```

### 3. Formula Recognition
```bash
python scripts/ocr.py math_problem.jpg --prompt "Extract mathematical formulas in LaTeX format"
```

### 4. Chart Data Extraction
```bash
python scripts/ocr.py bar_chart.png --prompt "Extract the data values from this chart"
```

### 5. Multi-language Document
```bash
python scripts/ocr.py chinese_document.png  # Automatically detects language
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK` | `True` | Skip connectivity check (use cached models) |

## First-Time Setup

### 1. Install Python Dependencies
```bash
pip install paddleocr paddlepaddle
```

### 2. Install PDF Support
```bash
pip install pdf2image
brew install poppler
```

### 3. Verify Setup
```bash
python scripts/setup_check.py
```

> **Note**: First run will automatically download models (~200MB) from HuggingFace.

## Troubleshooting

### "paddleocr not found"
```bash
pip install paddleocr paddlepaddle
```

### "pdf2image error"
```bash
brew install poppler
pip install pdf2image
```

### First run is slow
First run downloads models (~200MB) from HuggingFace. Subsequent runs use cached models.

### Network issues downloading models
```bash
# Use cached models, skip connectivity check
export PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
python scripts/ocr.py image.png
```

## Model Information

| Property | Value |
|----------|-------|
| Engine | PaddleOCR PP-OCRv5 |
| Total Size | ~200 MB |
| Languages | 100+ |
| Runtime | CPU (no GPU required) |
| Source | [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR) |

## See Also

- [PDF Skill](../pdf/SKILL.md) - For PDF manipulation (merge, split, etc.)
- [DOCX Skill](../docx/SKILL.md) - For Word document operations
