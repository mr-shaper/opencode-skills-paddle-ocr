#!/usr/bin/env python3
"""Check PaddleOCR environment setup."""

import subprocess
import sys


def check_paddleocr():
    """Check if PaddleOCR is installed."""
    try:
        import paddleocr
        version = getattr(paddleocr, '__version__', 'installed')
        print(f"[OK] PaddleOCR installed: {version}")
        return True
    except ImportError:
        print("[FAIL] PaddleOCR not found. Install with: pip install paddleocr paddlepaddle")
        return False


def check_paddlepaddle():
    """Check if PaddlePaddle is installed."""
    try:
        import paddle
        version = paddle.__version__
        print(f"[OK] PaddlePaddle installed: {version}")
        return True
    except ImportError:
        print("[FAIL] PaddlePaddle not found. Install with: pip install paddlepaddle")
        return False


def check_pdf2image():
    """Check if pdf2image is installed."""
    try:
        import pdf2image
        version = getattr(pdf2image, '__version__', 'installed')
        print(f"[OK] pdf2image installed: {version}")
        return True
    except ImportError:
        print("[FAIL] pdf2image not found. Install with: pip install pdf2image")
        return False


def check_pillow():
    """Check if Pillow is installed."""
    try:
        from PIL import Image
        import PIL
        version = PIL.__version__
        print(f"[OK] Pillow installed: {version}")
        return True
    except ImportError:
        print("[FAIL] Pillow not found. Install with: pip install Pillow")
        return False


def check_poppler():
    """Check if poppler is installed for PDF support."""
    try:
        result = subprocess.run(
            ["pdftoppm", "-v"],
            capture_output=True,
            text=True
        )
        # pdftoppm outputs version to stderr
        version = result.stderr.strip() if result.stderr else "installed"
        print(f"[OK] Poppler installed (for PDF support): {version}")
        return True
    except FileNotFoundError:
        print("[WARN] Poppler not found. PDF support requires:")
        print("       brew install poppler")
        return False


def check_model_cache():
    """Check if PaddleOCR models are cached."""
    import os
    from pathlib import Path

    cache_dir = Path.home() / ".paddlex" / "official_models"
    if cache_dir.exists():
        models = list(cache_dir.iterdir())
        if models:
            print(f"[OK] Model cache found: {cache_dir}")
            print(f"     {len(models)} model(s) cached")
            return True

    print("[INFO] No cached models found. Will download on first run (~200MB)")
    return None  # Not a failure, just info


def test_ocr():
    """Quick test of OCR functionality."""
    print("\n--- Quick OCR Test ---")
    try:
        import os
        import io
        from PIL import Image, ImageDraw

        # Create a simple test image with text
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Hello OCR Test", fill='black')

        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name, 'PNG')
            temp_path = f.name

        try:
            # Suppress warnings for clean output
            os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

            from paddleocr import PaddleOCR
            print("Loading PaddleOCR model (may take a moment)...", end=" ", flush=True)
            ocr = PaddleOCR(lang='en')
            print("done")

            result = ocr.ocr(temp_path)

            if result and len(result) > 0:
                # Extract text from result
                texts = []
                for page_result in result:
                    if page_result is None:
                        continue
                    if isinstance(page_result, dict):
                        texts.extend(page_result.get('rec_texts', []))
                    elif isinstance(page_result, list):
                        for line in page_result:
                            if line and len(line) >= 2:
                                text = line[1][0] if isinstance(line[1], tuple) else line[1]
                                texts.append(text)

                extracted = ' '.join(texts)
                print(f"[OK] OCR test passed. Extracted: {extracted[:50]}")
                return True
            else:
                print("[WARN] OCR returned empty result")
                return False

        finally:
            os.unlink(temp_path)

    except ImportError as e:
        print(f"[SKIP] Cannot run OCR test: {e}")
        return None
    except Exception as e:
        print(f"[FAIL] OCR test failed: {e}")
        return False


def main():
    print("=" * 50)
    print("PaddleOCR Environment Check")
    print("=" * 50)
    print()

    checks = [
        ("PaddlePaddle", check_paddlepaddle),
        ("PaddleOCR", check_paddleocr),
        ("pdf2image", check_pdf2image),
        ("Pillow", check_pillow),
        ("Poppler (PDF)", check_poppler),
        ("Model Cache", check_model_cache),
    ]

    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results.append((name, False))
        print()

    # Summary
    print("=" * 50)
    print("Summary")
    print("=" * 50)

    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    info = sum(1 for _, r in results if r is None)

    for name, result in results:
        if result is True:
            status = "PASS"
        elif result is False:
            status = "FAIL"
        else:
            status = "INFO"
        print(f"  {name}: {status}")

    print()
    if failed == 0:
        print("All checks passed! PaddleOCR is ready to use.")
        print()
        print("Quick start:")
        print("  python scripts/ocr.py <image.png>")
        print("  python scripts/ocr.py <document.pdf>")
        return 0
    else:
        print(f"{failed} check(s) failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
