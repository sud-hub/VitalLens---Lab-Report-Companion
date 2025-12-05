"""
AI extraction module for text and data extraction from medical reports.

This module uses Google's Gemini AI for accurate extraction of test results
and patient demographics from lab report images and PDFs.
"""

from .gemini_engine import extract_with_gemini, GeminiEngine, ExtractionResult

__all__ = [
    'extract_with_gemini',
    'GeminiEngine',
    'ExtractionResult',
]

