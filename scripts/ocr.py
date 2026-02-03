#!/usr/bin/env python3
"""
PaddleOCR Script - Native Python Implementation
Supports: Images (PNG, JPG, JPEG, BMP, GIF, WEBP, TIFF) and PDFs
Uses PaddlePaddle's PaddleOCR library directly
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings('ignore')

try:
    from paddleocr import PaddleOCR
except ImportError:
    print("Error: paddleocr not found. Install with: pip install paddleocr paddlepaddle", file=sys.stderr)
    sys.exit(1)

# Supported file extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff", ".tif"}
PDF_EXTENSION = ".pdf"

# Global OCR instance (lazy loaded)
_ocr_instance = None


def get_ocr_instance(lang='ch'):
    """Get or create PaddleOCR instance."""
    global _ocr_instance
    if _ocr_instance is None:
        print("Initializing PaddleOCR (first run may download models)...", file=sys.stderr)
        # Suppress connectivity check
        os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
        _ocr_instance = PaddleOCR(lang=lang)
    return _ocr_instance


def ocr_image(image_path: str, lang: str = 'ch') -> str:
    """Perform OCR on a single image."""
    ocr = get_ocr_instance(lang)
    result = ocr.ocr(image_path)

    if result is None or len(result) == 0:
        return ""

    # Extract text from results (PaddleOCR 3.x format)
    lines = []
    for page_result in result:
        if page_result is None:
            continue
        # New format: page_result is a dict with 'rec_texts' key
        if isinstance(page_result, dict):
            rec_texts = page_result.get('rec_texts', [])
            lines.extend(rec_texts)
        # Old format: page_result is a list of [box, (text, confidence)]
        elif isinstance(page_result, list):
            for line in page_result:
                if line and len(line) >= 2:
                    text = line[1][0] if isinstance(line[1], tuple) else line[1]
                    lines.append(text)

    return '\n'.join(lines)


def pdf_to_images(pdf_path: str) -> list:
    """Convert PDF pages to temporary image files."""
    try:
        from pdf2image import convert_from_path
    except ImportError:
        print("Error: pdf2image not found. Install with: pip install pdf2image", file=sys.stderr)
        print("Also ensure poppler is installed: brew install poppler", file=sys.stderr)
        sys.exit(1)

    try:
        images = convert_from_path(pdf_path, dpi=200)
    except Exception as e:
        print(f"Error converting PDF: {e}", file=sys.stderr)
        print("Ensure poppler is installed: brew install poppler", file=sys.stderr)
        sys.exit(1)

    temp_paths = []
    for i, image in enumerate(images):
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".png", delete=False, prefix=f"page_{i+1}_"
        )
        image.save(temp_file.name, "PNG")
        temp_paths.append(temp_file.name)
        print(f"Converted page {i+1}/{len(images)}", file=sys.stderr)

    return temp_paths


def process_image(image_path: str, lang: str = 'ch') -> dict:
    """Process a single image and return OCR result."""
    print(f"Processing: {image_path}", file=sys.stderr)
    text = ocr_image(image_path, lang)

    return {
        "source": str(image_path),
        "type": "image",
        "text": text
    }


def process_pdf(pdf_path: str, lang: str = 'ch') -> dict:
    """Process a PDF file by converting to images and OCR each page."""
    print(f"Processing PDF: {pdf_path}", file=sys.stderr)
    temp_images = pdf_to_images(pdf_path)

    pages = []
    try:
        for i, image_path in enumerate(temp_images):
            print(f"OCR page {i+1}/{len(temp_images)}...", file=sys.stderr)
            text = ocr_image(image_path, lang)
            pages.append({
                "page": i + 1,
                "text": text
            })
    finally:
        # Cleanup temporary files
        for temp_path in temp_images:
            try:
                os.unlink(temp_path)
            except Exception:
                pass

    return {
        "source": str(pdf_path),
        "type": "pdf",
        "total_pages": len(pages),
        "pages": pages
    }


def format_output(result: dict, as_json: bool = False) -> str:
    """Format the OCR result for output."""
    if as_json:
        return json.dumps(result, indent=2, ensure_ascii=False)

    if result.get("type") == "pdf":
        parts = []
        for page in result.get("pages", []):
            parts.append(f"=== Page {page['page']} ===\n{page['text']}")
        return "\n\n".join(parts)
    else:
        return result.get("text", "")


def main():
    parser = argparse.ArgumentParser(
        description="OCR using PaddleOCR (Native Python)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ocr.py image.png                    # OCR a single image
  python ocr.py document.pdf                 # OCR all pages of a PDF
  python ocr.py image.png --json             # Output as JSON
  python ocr.py image.png --lang en          # English OCR
  python ocr.py doc.pdf -o result.txt        # Save to file

Supported formats:
  Images: PNG, JPG, JPEG, BMP, GIF, WEBP, TIFF
  Documents: PDF

Languages:
  ch (Chinese+English, default), en (English), japan, korean, french, german, etc.
        """
    )
    parser.add_argument("input_file", help="Image or PDF file to process")
    parser.add_argument("--lang", "-l", default="ch", help="Language (default: ch for Chinese+English)")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    suffix = input_path.suffix.lower()

    if suffix == PDF_EXTENSION:
        result = process_pdf(str(input_path), args.lang)
    elif suffix in IMAGE_EXTENSIONS:
        result = process_image(str(input_path), args.lang)
    else:
        print(f"Error: Unsupported file type: {suffix}", file=sys.stderr)
        print(f"Supported: PDF, {', '.join(sorted(IMAGE_EXTENSIONS))}", file=sys.stderr)
        sys.exit(1)

    output_text = format_output(result, args.json)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Output saved to: {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
