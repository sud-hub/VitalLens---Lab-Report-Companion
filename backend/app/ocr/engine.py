"""
OCR Engine module for extracting text from images and PDFs.

This module provides an interface for OCR operations and implements
offline OCR using PaddleOCR for images and PyMuPDF for PDFs.
"""

from typing import Protocol, Optional
from dataclasses import dataclass
import io
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from paddleocr import PaddleOCR


@dataclass
class OCRResult:
    """Result from OCR processing."""
    raw_text: str
    confidence: Optional[float] = None
    blocks: Optional[list] = None


class OCREngine(Protocol):
    """Interface for OCR engines - allows swapping implementations."""
    
    def process_image(self, image_bytes: bytes) -> OCRResult:
        """
        Process an image and extract text.
        
        Args:
            image_bytes: Raw bytes of the image
            
        Returns:
            OCRResult containing extracted text and metadata
        """
        ...


class PaddleOCREngine:
    """PaddleOCR-based offline OCR implementation."""
    
    _instance = None
    _ocr = None
    
    def __new__(cls):
        """Singleton pattern to reuse the OCR model."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize PaddleOCR engine with English language support."""
        # Only initialize once (singleton pattern)
        if PaddleOCREngine._ocr is None:
            # Initialize PaddleOCR with offline mode
            # use_angle_cls=True helps with rotated text
            # lang='en' for English text
            PaddleOCREngine._ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en'
            )
    
    def process_image(self, image_bytes: bytes) -> OCRResult:
        """
        Process an image using PaddleOCR.
        
        Args:
            image_bytes: Raw bytes of the image
            
        Returns:
            OCRResult with extracted text and confidence scores
        """
        # Convert bytes to PIL Image, then to numpy array
        # PaddleOCR requires numpy array or file path, not PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL Image to numpy array for PaddleOCR
        image_array = np.array(image)
        
        # Run PaddleOCR
        # Result format: [[[bbox], (text, confidence)], ...]
        result = PaddleOCREngine._ocr.ocr(image_array)
        
        if not result or not result[0]:
            return OCRResult(raw_text="", confidence=0.0, blocks=[])
        
        # Extract text and confidence scores
        text_lines = []
        confidences = []
        blocks = []
        
        for line in result[0]:
            if line:
                # PaddleOCR result format: [bbox, (text, confidence)]
                # Handle different result formats
                if len(line) == 2:
                    bbox, text_info = line
                    if isinstance(text_info, tuple) and len(text_info) == 2:
                        text, confidence = text_info
                    else:
                        # Fallback if format is different
                        text = str(text_info)
                        confidence = 1.0
                else:
                    # Unexpected format, skip
                    continue
                    
                text_lines.append(text)
                confidences.append(confidence)
                blocks.append({
                    'bbox': bbox,
                    'text': text,
                    'confidence': confidence
                })
        
        # Combine all text lines
        raw_text = '\n'.join(text_lines)
        
        # Calculate average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return OCRResult(
            raw_text=raw_text,
            confidence=avg_confidence,
            blocks=blocks
        )


class PDFTextExtractor:
    """Extract text from PDF files using PyMuPDF."""
    
    def process_pdf(self, pdf_bytes: bytes) -> OCRResult:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_bytes: Raw bytes of the PDF file
            
        Returns:
            OCRResult with extracted text
        """
        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        text_lines = []
        is_scanned = True
        
        # First pass: try to extract text directly
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text = page.get_text()
            if text.strip():
                text_lines.append(text)
                is_scanned = False
        
        # If no text was extracted (or very little), it might be a scanned PDF
        # In this case, we need to convert pages to images and run OCR
        if is_scanned:
            # Clear any partial text
            text_lines = []
            
            # Use PaddleOCR for scanned PDFs
            engine = PaddleOCREngine()
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Render page to image (pixmap)
                # zoom=2 to increase resolution for better OCR
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                
                # Get image bytes
                img_bytes = pix.tobytes("png")
                
                # Run OCR on the page image
                ocr_result = engine.process_image(img_bytes)
                
                if ocr_result.raw_text.strip():
                    text_lines.append(ocr_result.raw_text)

        pdf_document.close()
        
        # Combine all pages
        raw_text = '\n'.join(text_lines)
        
        return OCRResult(
            raw_text=raw_text,
            confidence=1.0 if not is_scanned else 0.8,  # Lower confidence for OCR
            blocks=None
        )


def run_ocr_on_image_bytes(image_bytes: bytes, is_pdf: bool = False) -> dict:
    """
    Main entry point for OCR processing.
    
    This function determines whether to use PaddleOCR for images
    or PyMuPDF for PDFs, then processes the file accordingly.
    
    Args:
        image_bytes: Raw bytes of the image or PDF file
        is_pdf: Whether the file is a PDF (True) or image (False)
        
    Returns:
        Dictionary containing:
            - raw_text: Extracted text
            - confidence: Confidence score (0.0 to 1.0)
            - blocks: Optional list of text blocks with bounding boxes
    """
    if is_pdf:
        extractor = PDFTextExtractor()
        result = extractor.process_pdf(image_bytes)
    else:
        engine = PaddleOCREngine()
        result = engine.process_image(image_bytes)
    
    return {
        "raw_text": result.raw_text,
        "confidence": result.confidence,
        "blocks": result.blocks
    }
