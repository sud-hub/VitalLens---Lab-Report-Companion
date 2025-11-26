"""OCR module for text extraction from images and PDFs."""

from .engine import run_ocr_on_image_bytes, OCRResult, OCREngine
from .postprocess import clean_ocr_text, normalize_test_name, extract_numeric_value
from .gemini_engine import extract_with_gemini, GeminiEngine, ExtractionResult

__all__ = [
    'run_ocr_on_image_bytes',
    'OCRResult',
    'OCREngine',
    'clean_ocr_text',
    'normalize_test_name',
    'extract_numeric_value',
    'extract_with_gemini',
    'GeminiEngine',
    'ExtractionResult',
]

