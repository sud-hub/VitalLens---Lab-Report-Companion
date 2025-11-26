"""OCR module for text extraction from images and PDFs."""

from .engine import run_ocr_on_image_bytes, OCRResult, OCREngine
from .postprocess import clean_ocr_text, normalize_test_name, extract_numeric_value

__all__ = [
    'run_ocr_on_image_bytes',
    'OCRResult',
    'OCREngine',
    'clean_ocr_text',
    'normalize_test_name',
    'extract_numeric_value',
]
