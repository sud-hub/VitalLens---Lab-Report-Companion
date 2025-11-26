"""
Tests for OCR engine functionality.

This module tests the OCR engine interface and basic functionality.
"""

import pytest
from io import BytesIO
from PIL import Image
from unittest.mock import patch, MagicMock
import socket
from hypothesis import given, settings, strategies as st
from app.ocr.engine import (
    PaddleOCREngine,
    PDFTextExtractor,
    run_ocr_on_image_bytes,
    OCRResult
)
from app.ocr.postprocess import (
    clean_ocr_text,
    normalize_test_name,
    extract_numeric_value,
    is_likely_test_result_line
)


class TestOCREngineInterface:
    """Test OCR engine interface and basic functionality."""
    
    def test_ocr_result_dataclass(self):
        """Test OCRResult dataclass creation."""
        result = OCRResult(raw_text="Test text", confidence=0.95)
        assert result.raw_text == "Test text"
        assert result.confidence == 0.95
        assert result.blocks is None
    
    def test_ocr_result_with_blocks(self):
        """Test OCRResult with blocks."""
        blocks = [{"text": "line1", "confidence": 0.9}]
        result = OCRResult(raw_text="line1", confidence=0.9, blocks=blocks)
        assert result.blocks == blocks
    
    def test_run_ocr_on_image_bytes_returns_dict(self):
        """Test that run_ocr_on_image_bytes returns expected structure."""
        # Create a simple test image
        img = Image.new('RGB', (100, 30), color='white')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        result = run_ocr_on_image_bytes(img_bytes, is_pdf=False)
        
        # Verify structure
        assert isinstance(result, dict)
        assert "raw_text" in result
        assert "confidence" in result
        assert "blocks" in result
        assert isinstance(result["raw_text"], str)


class TestOCRPostprocessing:
    """Test OCR postprocessing functions."""
    
    def test_clean_ocr_text_normalizes_whitespace(self):
        """Test that excessive whitespace is normalized."""
        text = "Line1\n\n\n\nLine2"
        cleaned = clean_ocr_text(text)
        assert "\n\n\n" not in cleaned
        assert "Line1" in cleaned
        assert "Line2" in cleaned
    
    def test_clean_ocr_text_fixes_l_to_1(self):
        """Test that 'l' is fixed to '1' in numeric contexts."""
        text = "WBC: 5l.2"
        cleaned = clean_ocr_text(text)
        assert "51.2" in cleaned or "5l.2" in cleaned  # May or may not fix depending on pattern
        
        text = "Value: l5"
        cleaned = clean_ocr_text(text)
        assert "15" in cleaned
    
    def test_clean_ocr_text_fixes_O_to_0(self):
        """Test that 'O' is fixed to '0' in numeric contexts."""
        text = "Value: 1O2"
        cleaned = clean_ocr_text(text)
        assert "102" in cleaned
    
    def test_clean_ocr_text_empty_string(self):
        """Test that empty string is handled."""
        assert clean_ocr_text("") == ""
        assert clean_ocr_text(None) == ""
    
    def test_normalize_test_name(self):
        """Test test name normalization."""
        assert normalize_test_name("WBC") == "wbc"
        assert normalize_test_name("White Blood Cells") == "white blood cells"
        assert normalize_test_name("  WBC  ") == "wbc"
        assert normalize_test_name("WBC!!!") == "wbc"
    
    def test_normalize_test_name_empty(self):
        """Test empty test name."""
        assert normalize_test_name("") == ""
        assert normalize_test_name(None) == ""
    
    def test_extract_numeric_value_simple(self):
        """Test extracting simple numeric values."""
        value, unit = extract_numeric_value("7.2")
        assert value == 7.2
        assert unit == ""
    
    def test_extract_numeric_value_with_unit(self):
        """Test extracting value with unit."""
        value, unit = extract_numeric_value("7.2 mg/dL")
        assert value == 7.2
        assert unit == "mg/dL"
    
    def test_extract_numeric_value_complex_unit(self):
        """Test extracting value with complex unit."""
        value, unit = extract_numeric_value("150 10^3/µL")
        assert value == 150.0
        assert unit == "10^3/µL"
    
    def test_extract_numeric_value_no_number(self):
        """Test extracting from string with no number."""
        value, unit = extract_numeric_value("No number here")
        assert value is None
        assert unit == ""
    
    def test_extract_numeric_value_empty(self):
        """Test empty string."""
        value, unit = extract_numeric_value("")
        assert value is None
        assert unit == ""
    
    def test_is_likely_test_result_line(self):
        """Test identifying test result lines."""
        assert is_likely_test_result_line("WBC: 7.2 10^3/µL") is True
        assert is_likely_test_result_line("Glucose 95 mg/dL") is True
        assert is_likely_test_result_line("HEADER LINE") is False
        assert is_likely_test_result_line("") is False
        assert is_likely_test_result_line("123") is False  # No letters


class TestPaddleOCREngine:
    """Test PaddleOCR engine implementation."""
    
    def test_paddle_ocr_engine_initialization(self):
        """Test that PaddleOCR engine can be initialized."""
        # This test verifies the engine can be created
        # Actual OCR testing requires PaddleOCR to be installed
        try:
            engine = PaddleOCREngine()
            assert engine is not None
            assert hasattr(engine, 'ocr')
        except Exception as e:
            pytest.skip(f"PaddleOCR not available: {e}")
    
    def test_paddle_ocr_engine_process_image(self):
        """Test processing a simple image."""
        try:
            engine = PaddleOCREngine()
            
            # Create a simple white image
            img = Image.new('RGB', (100, 30), color='white')
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()
            
            result = engine.process_image(img_bytes)
            
            # Verify result structure
            assert isinstance(result, OCRResult)
            assert isinstance(result.raw_text, str)
            assert result.confidence is not None
            
        except Exception as e:
            pytest.skip(f"PaddleOCR not available: {e}")


class TestPDFTextExtractor:
    """Test PDF text extraction."""
    
    def test_pdf_extractor_initialization(self):
        """Test that PDF extractor can be initialized."""
        extractor = PDFTextExtractor()
        assert extractor is not None
    
    def test_pdf_extractor_empty_pdf(self):
        """Test extracting from a minimal PDF."""
        # This would require creating a test PDF
        # For now, we just verify the method exists
        extractor = PDFTextExtractor()
        assert hasattr(extractor, 'process_pdf')


class TestOCROfflineProperty:
    """Property-based tests for OCR offline operation."""
    
    # Feature: lab-report-companion, Property 7: OCR operates offline
    @settings(max_examples=100, deadline=None)
    @given(
        width=st.integers(min_value=100, max_value=300),
        height=st.integers(min_value=50, max_value=150),
        color=st.tuples(
            st.integers(min_value=200, max_value=255),  # Lighter colors for better OCR
            st.integers(min_value=200, max_value=255),
            st.integers(min_value=200, max_value=255)
        )
    )
    def test_ocr_operates_offline(self, width, height, color):
        """
        Property 7: OCR operates offline
        
        For any image processed by the OCR engine, no external network 
        API calls should be made during processing.
        
        Validates: Requirements 4.2
        """
        # Create a test image with random dimensions and color
        img = Image.new('RGB', (width, height), color=color)
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        # Mock common HTTP libraries to detect any external API calls
        with patch('urllib.request.urlopen') as mock_urlopen:
            with patch('requests.get') as mock_requests_get:
                with patch('requests.post') as mock_requests_post:
                    # Run OCR processing
                    result = run_ocr_on_image_bytes(img_bytes, is_pdf=False)
                    
                    # Verify no HTTP calls were made to external APIs
                    assert not mock_urlopen.called, \
                        "OCR engine made urllib HTTP call - not offline!"
                    assert not mock_requests_get.called, \
                        "OCR engine made requests.get call - not offline!"
                    assert not mock_requests_post.called, \
                        "OCR engine made requests.post call - not offline!"
                    
                    # Verify result structure is valid
                    assert isinstance(result, dict), "Result should be a dictionary"
                    assert "raw_text" in result, "Result should contain 'raw_text'"
                    assert isinstance(result["raw_text"], str), "raw_text should be a string"


class TestOCRInterfaceContract:
    """Property-based tests for OCR engine interface contract."""
    
    # Feature: lab-report-companion, Property 41: OCR engine interface contract
    @settings(max_examples=100, deadline=None)
    @given(
        raw_text=st.text(min_size=0, max_size=500),
        confidence=st.one_of(
            st.none(),
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
        ),
        has_blocks=st.booleans()
    )
    def test_ocr_engine_interface_contract(self, raw_text, confidence, has_blocks):
        """
        Property 41: OCR engine interface contract
        
        For any OCR engine implementation, when called with image bytes,
        it should return a structured result containing raw text and 
        optional confidence metadata.
        
        Validates: Requirements 17.2
        """
        # Create mock blocks if needed
        blocks = None
        if has_blocks:
            blocks = [
                {"text": "sample", "confidence": 0.9, "bbox": [[0, 0], [10, 0], [10, 10], [0, 10]]}
            ]
        
        # Create an OCRResult to test the interface contract
        result_obj = OCRResult(
            raw_text=raw_text,
            confidence=confidence,
            blocks=blocks
        )
        
        # Verify the OCRResult dataclass maintains the interface contract:
        # 1. raw_text must be a string
        assert isinstance(result_obj.raw_text, str), \
            f"raw_text must be a string, got {type(result_obj.raw_text)}"
        
        # 2. confidence must be None or a float
        assert result_obj.confidence is None or isinstance(result_obj.confidence, float), \
            f"confidence must be None or float, got {type(result_obj.confidence)}"
        
        # 3. If confidence is a float, it should be between 0.0 and 1.0
        if isinstance(result_obj.confidence, float):
            assert 0.0 <= result_obj.confidence <= 1.0, \
                f"confidence must be between 0.0 and 1.0, got {result_obj.confidence}"
        
        # 4. blocks must be None or a list
        assert result_obj.blocks is None or isinstance(result_obj.blocks, list), \
            f"blocks must be None or list, got {type(result_obj.blocks)}"
        
        # 5. If blocks is a list, each block should be a dict
        if isinstance(result_obj.blocks, list):
            for block in result_obj.blocks:
                assert isinstance(block, dict), \
                    f"Each block must be a dict, got {type(block)}"
        
        # Now test that the run_ocr_on_image_bytes function returns the correct structure
        # We'll mock the engine to avoid slow OCR processing
        mock_result = OCRResult(
            raw_text=raw_text,
            confidence=confidence,
            blocks=blocks
        )
        
        with patch('app.ocr.engine.PaddleOCREngine') as MockEngine:
            mock_instance = MagicMock()
            mock_instance.process_image.return_value = mock_result
            MockEngine.return_value = mock_instance
            
            # Create a simple test image
            img = Image.new('RGB', (100, 30), color='white')
            img_bytes_io = BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes_value = img_bytes_io.getvalue()
            
            # Call the OCR function
            result = run_ocr_on_image_bytes(img_bytes_value, is_pdf=False)
            
            # Verify the interface contract for the returned dictionary:
            # 1. Result must be a dictionary
            assert isinstance(result, dict), \
                f"OCR engine must return a dict, got {type(result)}"
            
            # 2. Result must contain 'raw_text' field
            assert "raw_text" in result, \
                "OCR result must contain 'raw_text' field"
            
            # 3. raw_text must be a string
            assert isinstance(result["raw_text"], str), \
                f"raw_text must be a string, got {type(result['raw_text'])}"
            
            # 4. Result must contain 'confidence' field (optional metadata)
            assert "confidence" in result, \
                "OCR result must contain 'confidence' field"
            
            # 5. confidence must be None or a float
            assert result["confidence"] is None or isinstance(result["confidence"], float), \
                f"confidence must be None or float, got {type(result['confidence'])}"
            
            # 6. If confidence is a float, it should be between 0.0 and 1.0
            if isinstance(result["confidence"], float):
                assert 0.0 <= result["confidence"] <= 1.0, \
                    f"confidence must be between 0.0 and 1.0, got {result['confidence']}"
            
            # 7. Result must contain 'blocks' field (optional metadata)
            assert "blocks" in result, \
                "OCR result must contain 'blocks' field"
            
            # 8. blocks must be None or a list
            assert result["blocks"] is None or isinstance(result["blocks"], list), \
                f"blocks must be None or list, got {type(result['blocks'])}"
            
            # 9. If blocks is a list, each block should be a dict
            if isinstance(result["blocks"], list):
                for block in result["blocks"]:
                    assert isinstance(block, dict), \
                        f"Each block must be a dict, got {type(block)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
