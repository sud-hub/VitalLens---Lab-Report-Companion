"""
OCR postprocessing functions for cleaning and normalizing extracted text.

This module provides utilities to clean OCR output and fix common OCR errors.
"""

import re


def clean_ocr_text(raw_text: str) -> str:
    """
    Clean OCR output to improve parsing accuracy.
    
    This function:
    - Normalizes whitespace
    - Removes excessive line breaks
    - Fixes common OCR errors (l vs 1, O vs 0, etc.)
    - Removes special characters that interfere with parsing
    
    Args:
        raw_text: Raw text from OCR engine
        
    Returns:
        Cleaned text ready for parsing
    """
    if not raw_text:
        return ""
    
    text = raw_text
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove excessive blank lines (more than 2 consecutive newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Normalize whitespace within lines (multiple spaces to single space)
    lines = text.split('\n')
    lines = [re.sub(r'[ \t]+', ' ', line) for line in lines]
    text = '\n'.join(lines)
    
    # Fix common OCR errors in numeric contexts
    # These patterns look for likely numeric values and fix common mistakes
    
    # Fix 'l' (lowercase L) that should be '1' in numeric contexts
    # Pattern: letter 'l' surrounded by digits or at start of number
    text = re.sub(r'(\d)l(\d)', r'\g<1>1\g<2>', text)  # 5l2 -> 512
    text = re.sub(r'\bl(\d)', r'1\g<1>', text)  # l5 -> 15
    text = re.sub(r'(\d)l\b', r'\g<1>1', text)  # 5l -> 51
    
    # Fix 'O' (capital O) that should be '0' in numeric contexts
    text = re.sub(r'(\d)O(\d)', r'\g<1>0\g<2>', text)  # 5O2 -> 502
    text = re.sub(r'\bO(\d)', r'0\g<1>', text)  # O5 -> 05
    text = re.sub(r'(\d)O\b', r'\g<1>0', text)  # 5O -> 50
    
    # Fix 'I' (capital I) that should be '1' in numeric contexts
    text = re.sub(r'(\d)I(\d)', r'\g<1>1\g<2>', text)  # 5I2 -> 512
    text = re.sub(r'\bI(\d)', r'1\g<1>', text)  # I5 -> 15
    text = re.sub(r'(\d)I\b', r'\g<1>1', text)  # 5I -> 51
    
    # Fix 'S' that should be '5' in numeric contexts
    text = re.sub(r'(\d)S(\d)', r'\g<1>5\g<2>', text)  # 1S2 -> 152
    text = re.sub(r'(\d)S\b', r'\g<1>5', text)  # 9S -> 95
    
    # Fix 'B' that should be '8' in numeric contexts
    text = re.sub(r'(\d)B(\d)', r'\g<1>8\g<2>', text)  # 1B2 -> 182
    
    # Remove zero-width spaces and other invisible characters
    text = re.sub(r'[\u200b-\u200f\ufeff]', '', text)
    
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove empty lines at start and end
    text = text.strip()
    
    return text


def normalize_test_name(test_name: str) -> str:
    """
    Normalize a test name for consistent matching.
    
    This function:
    - Converts to lowercase
    - Removes extra whitespace
    - Removes special characters
    - Standardizes common abbreviations
    
    Args:
        test_name: Raw test name from OCR
        
    Returns:
        Normalized test name
    """
    if not test_name:
        return ""
    
    # Convert to lowercase
    name = test_name.lower()
    
    # Remove special characters except spaces, hyphens, and parentheses
    name = re.sub(r'[^\w\s\-()]', '', name)
    
    # Normalize whitespace
    name = re.sub(r'\s+', ' ', name)
    
    # Strip leading/trailing whitespace
    name = name.strip()
    
    return name


def extract_numeric_value(value_str: str) -> tuple[float | None, str]:
    """
    Extract numeric value and unit from a string.
    
    Args:
        value_str: String containing a numeric value and possibly a unit
        
    Returns:
        Tuple of (numeric_value, unit) or (None, "") if no value found
        
    Examples:
        "7.2" -> (7.2, "")
        "7.2 mg/dL" -> (7.2, "mg/dL")
        "150 10^3/µL" -> (150.0, "10^3/µL")
    """
    if not value_str:
        return None, ""
    
    # Pattern to match numeric values (including decimals)
    # Matches: 7.2, 150, 0.5, etc.
    numeric_pattern = r'(\d+\.?\d*)'
    
    match = re.search(numeric_pattern, value_str)
    if not match:
        return None, ""
    
    try:
        value = float(match.group(1))
    except ValueError:
        return None, ""
    
    # Extract unit (everything after the number, stripped)
    unit_start = match.end()
    unit = value_str[unit_start:].strip()
    
    return value, unit


def is_likely_test_result_line(line: str) -> bool:
    """
    Determine if a line likely contains a test result.
    
    A line is likely a test result if it contains:
    - A test name (alphabetic characters)
    - A numeric value
    - Optionally a unit
    
    Args:
        line: Single line of text
        
    Returns:
        True if line likely contains a test result
    """
    if not line or len(line.strip()) < 3:
        return False
    
    # Must contain at least one letter (for test name)
    if not re.search(r'[a-zA-Z]', line):
        return False
    
    # Must contain at least one digit (for value)
    if not re.search(r'\d', line):
        return False
    
    # Should not be a header line (all caps, no numbers at start)
    if line.isupper() and not re.match(r'^\d', line):
        return False
    
    return True
