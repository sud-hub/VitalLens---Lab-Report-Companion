"""
Gemini LLM Engine for extracting structured data from medical reports.

This module uses Google's Gemini Vision API to analyze medical report images
and PDFs, extracting test results in a structured format.
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
import io
from PIL import Image
from google import genai
from google.genai import types
from PyPDF2 import PdfReader

from app.core.config import settings


@dataclass
class ExtractionResult:
    """Result from Gemini extraction."""
    test_results: List[Dict]
    raw_response: str
    success: bool
    patient_gender: Optional[str] = None  # 'M', 'F', or None
    patient_age: Optional[int] = None  # Age in years
    error_message: Optional[str] = None


class GeminiEngine:
    """Gemini-based medical report extraction engine."""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        """Singleton pattern to reuse the Gemini client."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Gemini engine with API key."""
        # Only initialize once (singleton pattern)
        if GeminiEngine._client is None:
            if not settings.GEMINI_API_KEY:
                raise ValueError(
                    "GEMINI_API_KEY not found in environment variables. "
                    "Please set it in your .env file."
                )
            
            # Configure Gemini client with the new SDK
            GeminiEngine._client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    def _create_prompt(self) -> str:
        """
        Create the prompt for Gemini to extract medical test results.
        
        Returns:
            Detailed prompt with instructions and JSON schema
        """
        return """You are a medical report analyzer. Extract ALL test results AND patient demographics from this medical lab report image.

**Instructions:**
1. Identify patient information: gender (M/F) and age (in years)
2. Identify all test names, their numeric values, and units
3. Focus on these test panels: CBC (Complete Blood Count), Metabolic Panel, and Lipid Panel
4. Return results in valid JSON format only
5. If a test doesn't have a unit, use an empty string
6. Be precise with numeric values (include decimals)
7. Normalize test names to common medical abbreviations when possible

**Supported Tests:**
- CBC: WBC, RBC, Hemoglobin, Hematocrit, Platelets, MCV
- Metabolic: Glucose, BUN, Creatinine, Sodium, Potassium, Chloride, CO2, Calcium
- Lipid: Total Cholesterol, LDL, HDL, Triglycerides

**Output Format (JSON only, no markdown):**
{
  "patient_info": {
    "gender": "M",
    "age": 45
  },
  "test_results": [
    {
      "test_name": "WBC",
      "value": 7.2,
      "unit": "10^3/µL"
    },
    {
      "test_name": "Glucose",
      "value": 95.0,
      "unit": "mg/dL"
    }
  ]
}

**Important:**
- Return ONLY valid JSON, no additional text or markdown formatting
- If gender is not found, use null for gender
- If age is not found, use null for age
- If no tests are found, return: {"patient_info": {"gender": null, "age": null}, "test_results": []}
- Ensure all numeric values are numbers, not strings
- Gender should be "M" for male, "F" for female, or null if not specified
- Age should be a number (integer) or null if not specified
"""
    
    def process_image(self, image_bytes: bytes) -> ExtractionResult:
        """
        Process an image using Gemini Vision API.
        
        Args:
            image_bytes: Raw bytes of the image
            
        Returns:
            ExtractionResult with extracted test results
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Create prompt
            prompt = self._create_prompt()
            
            # Generate content with Gemini using new SDK
            # Use Gemini 2.5 Flash for stable performance with better free tier quotas
            response = GeminiEngine._client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt, image]
            )
            
            # Parse response
            return self._parse_response(response.text)
            
        except Exception as e:
            return ExtractionResult(
                test_results=[],
                raw_response="",
                success=False,
                error_message=f"Image processing error: {str(e)}"
            )
    
    def process_pdf(self, pdf_bytes: bytes) -> ExtractionResult:
        """
        Process a PDF using Gemini Vision API.
        
        For PDFs, we extract text and send it to Gemini.
        For multi-page PDFs, we process each page and combine results.
        
        Args:
            pdf_bytes: Raw bytes of the PDF file
            
        Returns:
            ExtractionResult with extracted test results
        """
        try:
            # Read PDF
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            
            all_test_results = []
            all_responses = []
            
            # Process each page (limit to first 5 pages for cost control)
            max_pages = min(len(pdf_reader.pages), 5)
            
            for page_num in range(max_pages):
                page = pdf_reader.pages[page_num]
                
                # Extract text from PDF page
                text = page.extract_text()
                
                if text.strip():
                    # Process text-based PDF
                    result = self._process_text(text)
                    if result.success and result.test_results:
                        all_test_results.extend(result.test_results)
                        all_responses.append(result.raw_response)
            
            # Combine results
            return ExtractionResult(
                test_results=all_test_results,
                raw_response="\n".join(all_responses),
                success=len(all_test_results) > 0,
                error_message=None if all_test_results else "No test results found in PDF"
            )
            
        except Exception as e:
            return ExtractionResult(
                test_results=[],
                raw_response="",
                success=False,
                error_message=f"PDF processing error: {str(e)}"
            )
    
    def _process_text(self, text: str) -> ExtractionResult:
        """
        Process extracted text using Gemini.
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            ExtractionResult with extracted test results
        """
        try:
            # Create prompt for text-based extraction
            prompt = self._create_prompt()
            full_prompt = f"{prompt}\n\n**Medical Report Text:**\n{text}"
            
            # Generate content with Gemini using new SDK
            response = GeminiEngine._client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt
            )
            
            # Parse response
            return self._parse_response(response.text)
            
        except Exception as e:
            return ExtractionResult(
                test_results=[],
                raw_response="",
                success=False,
                error_message=f"Text processing error: {str(e)}"
            )
    
    def _parse_response(self, response_text: str) -> ExtractionResult:
        """
        Parse Gemini's response and extract structured data.
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            ExtractionResult with parsed test results
        """
        import json
        
        try:
            # Clean response - remove markdown code blocks if present
            cleaned_text = response_text.strip()
            
            # Remove markdown JSON code blocks
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            data = json.loads(cleaned_text)
            
            # Extract patient demographics
            patient_info = data.get("patient_info", {})
            patient_gender = patient_info.get("gender") if patient_info else None
            patient_age = patient_info.get("age") if patient_info else None
            
            # Validate and normalize gender
            if patient_gender and isinstance(patient_gender, str):
                patient_gender = patient_gender.upper()
                if patient_gender not in ['M', 'F']:
                    patient_gender = None
            else:
                patient_gender = None
            
            # Validate age
            if patient_age is not None:
                try:
                    patient_age = int(patient_age)
                    if patient_age < 0 or patient_age > 150:
                        patient_age = None
                except (ValueError, TypeError):
                    patient_age = None
            
            # Extract test results
            test_results = data.get("test_results", [])
            
            # Validate each test result
            validated_results = []
            for test in test_results:
                if all(key in test for key in ["test_name", "value", "unit"]):
                    # Ensure value is numeric
                    try:
                        value = float(test["value"])
                        validated_results.append({
                            "test_name_raw": test["test_name"],
                            "value": value,
                            "unit": test["unit"]
                        })
                    except (ValueError, TypeError):
                        continue
            
            return ExtractionResult(
                test_results=validated_results,
                raw_response=response_text,
                success=len(validated_results) > 0,
                patient_gender=patient_gender,
                patient_age=patient_age,
                error_message=None
            )
            
        except json.JSONDecodeError as e:
            return ExtractionResult(
                test_results=[],
                raw_response=response_text,
                success=False,
                error_message=f"JSON parsing error: {str(e)}"
            )
        except Exception as e:
            return ExtractionResult(
                test_results=[],
                raw_response=response_text,
                success=False,
                error_message=f"Response parsing error: {str(e)}"
            )


def extract_with_gemini(file_bytes: bytes, is_pdf: bool = False) -> dict:
    """
    Main entry point for Gemini-based extraction.
    
    This function replaces the OCR-based extraction with Gemini LLM.
    
    Args:
        file_bytes: Raw bytes of the image or PDF file
        is_pdf: Whether the file is a PDF (True) or image (False)
        
    Returns:
        Dictionary containing:
            - test_results: List of extracted test results
            - raw_response: Raw response from Gemini
            - success: Whether extraction was successful
            - patient_gender: Patient gender ('M', 'F', or None)
            - patient_age: Patient age in years (or None)
            - error_message: Error message if extraction failed
    """
    engine = GeminiEngine()
    
    if is_pdf:
        result = engine.process_pdf(file_bytes)
    else:
        result = engine.process_image(file_bytes)
    
    return {
        "test_results": result.test_results,
        "raw_response": result.raw_response,
        "success": result.success,
        "patient_gender": result.patient_gender,
        "patient_age": result.patient_age,
        "error_message": result.error_message
    }
