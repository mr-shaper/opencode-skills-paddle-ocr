#!/usr/bin/env python3
"""Check PaddleOCR-VL environment setup."""

import subprocess
import sys


def check_ollama():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
            print(f"[OK] Ollama installed: {version}")
            return True
    except FileNotFoundError:
        pass
    print("[FAIL] Ollama not found. Install with: brew install ollama")
    return False


def check_ollama_running():
    """Check if Ollama server is running."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("[OK] Ollama server is running")
            return True
    except Exception:
        pass
    print("[FAIL] Ollama server not running. Start with: brew services start ollama")
    return False


def check_model_installed():
    """Check if PaddleOCR-VL model is installed."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        if "PaddleOCR-VL" in result.stdout or "paddleocr" in result.stdout.lower():
            # Extract model info
            for line in result.stdout.split('\n'):
                if 'PaddleOCR-VL' in line or 'paddleocr' in line.lower():
                    print(f"[OK] PaddleOCR-VL model installed: {line.strip()}")
                    return True
            print("[OK] PaddleOCR-VL model installed")
            return True
    except Exception:
        pass
    print("[WARN] PaddleOCR-VL model not found. Pull with:")
    print("       ollama pull MedAIBase/PaddleOCR-VL:0.9b")
    return False


def check_python_deps():
    """Check Python dependencies."""
    deps = {
        "paddleocr": "pip install paddleocr paddlepaddle",
        "pdf2image": "pip install pdf2image"
    }
    all_ok = True

    for dep, install_cmd in deps.items():
        try:
            __import__(dep)
            print(f"[OK] Python package: {dep}")
        except ImportError:
            print(f"[FAIL] Python package missing: {dep}")
            print(f"       Install with: {install_cmd}")
            all_ok = False

    return all_ok


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


def test_ocr():
    """Quick test of OCR functionality."""
    print("\n--- Quick OCR Test ---")
    try:
        import requests
        import base64
        import io
        from PIL import Image, ImageDraw

        # Create a simple test image with text
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Hello OCR Test", fill='black')

        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

        # Call Ollama
        payload = {
            "model": "MedAIBase/PaddleOCR-VL:0.9b",
            "messages": [{"role": "user", "content": "Extract text from this image.", "images": [img_base64]}],
            "stream": False
        }

        response = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            text = result.get("message", {}).get("content", "")
            if text:
                print(f"[OK] OCR test passed. Extracted: {text[:50]}...")
                return True
            else:
                print("[WARN] OCR returned empty result")
                return False
        else:
            print(f"[FAIL] OCR test failed: HTTP {response.status_code}")
            return False

    except ImportError as e:
        print(f"[SKIP] Cannot run OCR test: {e}")
        return None
    except Exception as e:
        print(f"[FAIL] OCR test failed: {e}")
        return False


def main():
    print("=" * 50)
    print("PaddleOCR-VL Environment Check")
    print("=" * 50)
    print()

    checks = [
        ("Ollama Installation", check_ollama),
        ("Ollama Server", check_ollama_running),
        ("PaddleOCR-VL Model", check_model_installed),
        ("Python Dependencies", check_python_deps),
        ("Poppler (PDF)", check_poppler),
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

    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")

    print()
    if failed == 0:
        print("All checks passed! PaddleOCR-VL is ready to use.")
        print()
        print("Quick start:")
        print("  python ocr.py <image.png>")
        print("  python ocr.py <document.pdf>")
        return 0
    else:
        print(f"{failed} check(s) failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
