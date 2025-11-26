"""
Lab Report Parser module for extracting test results from OCR text.

This module parses OCR-extracted text to identify test names, values, and units
for the three supported lab panels: CBC, Metabolic Panel, and Lipid Panel.
"""

import re
from typing import List, Dict, Optional
from app.ocr.postprocess import clean_ocr_text, normalize_test_name, extract_numeric_value


def parse_lab_report(ocr_result: dict) -> List[Dict]:
    """
    Parse OCR text to extract test results.
    
    This function extracts test results from OCR output by:
    1. Cleaning the OCR text
    2. Splitting into lines
    3. Applying regex patterns to extract test names, values, and units
    4. Filtering to only include tests from supported panels (CBC, Metabolic, Lipid)
    
    Args:
        ocr_result: Dictionary containing 'raw_text' from OCR engine
        
    Returns:
        List of dictionaries, each containing:
            - test_name_raw: The raw test name as extracted
            - value: Numeric test value
            - unit: Unit of measurement
            
    Example:
        [
            {
                "test_name_raw": "WBC",
                "value": 7.2,
                "unit": "10^3/µL"
            },
            {
                "test_name_raw": "Glucose",
                "value": 95.0,
                "unit": "mg/dL"
            }
        ]
    """
    raw_text = ocr_result.get("raw_text", "")
    if not raw_text:
        return []
    
    # Clean the OCR text
    cleaned_text = clean_ocr_text(raw_text)
    
    # Split into lines
    lines = cleaned_text.split('\n')
    
    # Parse each line for test results
    results = []
    for line in lines:
        parsed = _parse_line(line)
        if parsed:
            results.append(parsed)
    
    return results


def _parse_line(line: str) -> Optional[Dict]:
    """
    Parse a single line to extract test name, value, and unit.
    
    This function tries multiple regex patterns to handle various lab report formats:
    - Pattern 1: <name> <value> <unit> (e.g., "WBC 7.2 10^3/µL")
    - Pattern 2: <name>: <value> <unit> (e.g., "Glucose: 95 mg/dL")
    - Pattern 3: <name> <value><unit> (e.g., "Hemoglobin 14.5g/dL")
    - Pattern 4: Table format with tabs/spaces (e.g., "WBC    7.2    10^3/µL")
    
    Args:
        line: Single line of text from OCR output
        
    Returns:
        Dictionary with test_name_raw, value, and unit, or None if no match
    """
    if not line or len(line.strip()) < 3:
        return None
    
    line = line.strip()
    
    # Skip header lines (all caps, no numbers)
    if line.isupper() and not re.search(r'\d', line):
        return None
    
    # Skip lines that are clearly not test results
    if not re.search(r'[a-zA-Z]', line) or not re.search(r'\d', line):
        return None
    
    # Define regex patterns for different lab report formats
    patterns = [
        # Pattern 1: <name> <value> <unit>
        # Example: "WBC 7.2 10^3/µL" or "White Blood Cells 7.2 10^3/µL" or "CO2 25 mmol/L"
        r'^([A-Za-z0-9][A-Za-z0-9\s\-]*?)\s+([\d.]+)\s+([A-Za-z0-9/^µ%°\-\+]+)$',
        
        # Pattern 2: <name>: <value> <unit>
        # Example: "Glucose: 95 mg/dL" or "CO2: 25 mmol/L"
        r'^([A-Za-z0-9][A-Za-z0-9\s\-]*?):\s*([\d.]+)\s+([A-Za-z0-9/^µ%°\-\+]+)$',
        
        # Pattern 3: <name> <value><unit> (no space between value and unit)
        # Example: "Hemoglobin 14.5g/dL"
        r'^([A-Za-z0-9][A-Za-z0-9\s\-]*?)\s+([\d.]+)([A-Za-z0-9/^µ%°\-\+]+)$',
        
        # Pattern 4: <name>: <value> (no unit)
        # Example: "Hematocrit: 42.5" or "CO2: 25"
        r'^([A-Za-z0-9][A-Za-z0-9\s\-]*?):\s*([\d.]+)\s*$',
        
        # Pattern 5: <name> <value> (no unit, space separated)
        # Example: "Platelets 250" or "CO2 25"
        r'^([A-Za-z0-9][A-Za-z0-9\s\-]*?)\s+([\d.]+)\s*$',
        
        # Pattern 6: Table format with multiple spaces/tabs
        # Example: "WBC    7.2    10^3/µL"
        r'^([A-Za-z0-9][A-Za-z0-9\s\-]*?)\s{2,}([\d.]+)\s{2,}([A-Za-z0-9/^µ%°\-\+]+)$',
        
        # Pattern 7: Table format with tabs
        # Example: "WBC\t7.2\t10^3/µL"
        r'^([A-Za-z0-9][A-Za-z0-9\s\-]*?)\t+([\d.]+)\t+([A-Za-z0-9/^µ%°\-\+]+)$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            groups = match.groups()
            test_name_raw = groups[0].strip()
            
            # Extract value
            try:
                value = float(groups[1])
            except (ValueError, IndexError):
                continue
            
            # Extract unit (if present)
            unit = ""
            if len(groups) > 2 and groups[2]:
                unit = groups[2].strip()
            
            # Normalize test name for filtering
            normalized_name = normalize_test_name(test_name_raw)
            
            # Only return if this looks like a supported test
            if _is_supported_test(normalized_name):
                return {
                    "test_name_raw": test_name_raw,
                    "value": value,
                    "unit": unit
                }
    
    return None


def _is_supported_test(normalized_name: str) -> bool:
    """
    Check if a normalized test name belongs to one of the supported panels.
    
    This function performs a preliminary check to filter out obviously unsupported
    tests before database lookup. It checks for common keywords associated with
    CBC, Metabolic Panel, and Lipid Panel tests.
    
    Args:
        normalized_name: Normalized test name (lowercase, no special chars)
        
    Returns:
        True if the test name contains keywords from supported panels
    """
    if not normalized_name:
        return False
    
    # Ensure the name is normalized (lowercase)
    normalized_name = normalized_name.lower().strip()
    
    # Keywords for CBC tests
    cbc_keywords = [
        'wbc', 'white blood', 'leukocyte',
        'rbc', 'red blood', 'erythrocyte',
        'hemoglobin', 'haemoglobin', 'hgb', 'hb',
        'hematocrit', 'haematocrit', 'hct',
        'platelet', 'plt', 'thrombocyte',
        'mcv', 'mean corpuscular', 'mean cell volume'
    ]
    
    # Keywords for Metabolic Panel tests
    metabolic_keywords = [
        'glucose', 'glu', 'blood sugar', 'fasting glucose',
        'bun', 'urea nitrogen', 'urea',
        'creatinine', 'creat',
        'sodium', 'na',
        'potassium', 'k',
        'chloride', 'cl',
        'co2', 'carbon dioxide', 'bicarbonate', 'hco3',
        'calcium'  # Removed 'ca' to avoid false positives with 'hba1c'
    ]
    
    # Keywords for Lipid Panel tests
    lipid_keywords = [
        'cholesterol', 'chol',
        'ldl', 'low density',
        'hdl', 'high density',
        'triglyceride', 'trig', 'tg'
    ]
    
    # Combine all keywords
    all_keywords = cbc_keywords + metabolic_keywords + lipid_keywords
    
    # Check if any keyword is in the normalized name
    for keyword in all_keywords:
        if keyword in normalized_name:
            # Found a match, but need to check for explicitly unsupported tests
            # that might contain the same substring
            # These are common tests that might partially match supported keywords
            unsupported_tests = [
                'hba1c', 'a1c', 'hemoglobin a1c',  # Diabetes test (contains 'hb')
                'vitamin', 'vit',
                'tsh', 'thyroid',
                't3', 't4',
                'ferritin',
                'b12', 'cobalamin',
                'folate', 'folic acid',
                'psa', 'prostate',
                'crp', 'c-reactive',
                'albumin',
                'bilirubin',
                'alt', 'ast', 'alp',  # Liver enzymes
                'ggt',
                'protein',
                'magnesium', 'mg',
                'phosphorus', 'phosphate'
            ]
            
            # Check if this is an explicitly unsupported test
            # Use word boundaries for short abbreviations to avoid false matches
            is_unsupported = False
            
            # Short abbreviations that need word boundary checks
            short_abbrevs = ['alt', 'ast', 'alp', 'mg', 'na', 'k']
            
            for unsupported in unsupported_tests:
                # For short abbreviations, use word boundaries
                if unsupported in short_abbrevs:
                    import re
                    if re.search(r'\b' + re.escape(unsupported) + r'\b', normalized_name):
                        is_unsupported = True
                        break
                else:
                    # For longer terms, simple substring match is fine
                    if unsupported in normalized_name:
                        is_unsupported = True
                        break
            
            if not is_unsupported:
                return True
    
    return False


def get_supported_test_keywords() -> Dict[str, List[str]]:
    """
    Get a dictionary of supported test keywords organized by panel.
    
    This is useful for documentation and testing purposes.
    
    Returns:
        Dictionary mapping panel names to lists of keywords
    """
    return {
        "CBC": [
            'wbc', 'white blood', 'leukocyte',
            'rbc', 'red blood', 'erythrocyte',
            'hemoglobin', 'haemoglobin', 'hgb', 'hb',
            'hematocrit', 'haematocrit', 'hct',
            'platelet', 'plt', 'thrombocyte',
            'mcv', 'mean corpuscular', 'mean cell volume'
        ],
        "METABOLIC": [
            'glucose', 'glu', 'blood sugar',
            'bun', 'urea nitrogen', 'urea',
            'creatinine', 'creat',
            'sodium', 'na',
            'potassium', 'k',
            'chloride', 'cl',
            'co2', 'carbon dioxide', 'bicarbonate', 'hco3',
            'calcium', 'ca'
        ],
        "LIPID": [
            'cholesterol', 'chol',
            'ldl', 'low density',
            'hdl', 'high density',
            'triglyceride', 'trig', 'tg'
        ]
    }
