"""
Reference ranges and status computation for lab test results.

This module provides functionality to compute the status (LOW, NORMAL, HIGH, CRITICAL)
of test results based on reference ranges, and defines the reference range constants
for CBC, Metabolic Panel, and Lipid Panel tests.

Now supports personalized reference ranges based on patient gender and age.
"""

from typing import Optional
from app.db.models import TestType
from app.rules.personalized_ranges import get_personalized_range, get_hdl_status_modifier


def compute_status(
    test_type: TestType,
    value: float,
    patient_gender: Optional[str] = None,
    patient_age: Optional[int] = None
) -> str:
    """
    Compute status based on personalized reference ranges.
    
    Args:
        test_type: TestType object containing reference ranges (ref_low, ref_high)
        value: The test result value to evaluate
        patient_gender: Patient gender ('M' or 'F') for personalized ranges
        patient_age: Patient age in years for personalized ranges
    
    Returns:
        Status string: 'LOW', 'NORMAL', 'HIGH', 'CRITICAL_HIGH', 'CRITICAL_LOW', 
                      'PROTECTIVE' (for HDL), or 'UNKNOWN'
        
    Status determination logic:
        - UNKNOWN: When reference ranges are not defined
        - CRITICAL_LOW: Value < ref_low * 0.5
        - LOW: Value < ref_low
        - NORMAL: ref_low <= Value <= ref_high
        - HIGH: ref_high < Value <= ref_high * 1.5
        - CRITICAL_HIGH: Value > ref_high * 1.5
        - PROTECTIVE: HDL >= 60 mg/dL (special case)
    """
    # Get personalized reference ranges based on demographics
    ref_low, ref_high = get_personalized_range(
        test_key=test_type.key,
        gender=patient_gender,
        age=patient_age,
        default_low=test_type.ref_low,
        default_high=test_type.ref_high
    )
    
    # When a TestType has no defined reference ranges, assign UNKNOWN
    if ref_low is None or ref_high is None:
        return "UNKNOWN"
    
    # Special handling for HDL - check for protective status first
    if test_type.key == "HDL":
        hdl_modifier = get_hdl_status_modifier(value, patient_gender)
        if hdl_modifier == "PROTECTIVE":
            return "PROTECTIVE"  # HDL >= 60 is excellent
    
    # Critical thresholds (50% beyond normal range)
    critical_low = ref_low * 0.5
    critical_high = ref_high * 1.5
    
    # When a test value is below the reference low threshold, assign LOW
    # Also handle CRITICAL_LOW for values significantly below threshold
    if value < critical_low:
        return "CRITICAL_LOW"
    elif value < ref_low:
        return "LOW"
    # When a test value is between ref_low and ref_high (inclusive), assign NORMAL
    elif value <= ref_high:
        return "NORMAL"
    # When a test value is above the reference high threshold, assign HIGH
    # Also handle CRITICAL_HIGH for values significantly above threshold
    elif value <= critical_high:
        return "HIGH"
    else:
        return "CRITICAL_HIGH"


# Seed data for reference ranges
# These constants are used to populate the database with TestType records

CBC_REFERENCE_RANGES = {
    "WBC": {"low": 4.5, "high": 11.0, "unit": "10^3/µL"},
    "RBC": {"low": 4.5, "high": 5.9, "unit": "10^6/µL"},
    "HGB": {"low": 13.5, "high": 17.5, "unit": "g/dL"},
    "HCT": {"low": 38.8, "high": 50.0, "unit": "%"},
    "PLT": {"low": 150, "high": 400, "unit": "10^3/µL"},
    "MCV": {"low": 80, "high": 100, "unit": "fL"},
}

METABOLIC_REFERENCE_RANGES = {
    "GLUCOSE": {"low": 70, "high": 100, "unit": "mg/dL"},
    "BUN": {"low": 7, "high": 20, "unit": "mg/dL"},
    "CREATININE": {"low": 0.7, "high": 1.3, "unit": "mg/dL"},
    "SODIUM": {"low": 136, "high": 145, "unit": "mmol/L"},
    "POTASSIUM": {"low": 3.5, "high": 5.0, "unit": "mmol/L"},
    "CHLORIDE": {"low": 98, "high": 107, "unit": "mmol/L"},
    "CO2": {"low": 23, "high": 29, "unit": "mmol/L"},
    "CALCIUM": {"low": 8.5, "high": 10.5, "unit": "mg/dL"},
}

LIPID_REFERENCE_RANGES = {
    "TC": {"low": 0, "high": 200, "unit": "mg/dL"},
    "LDL": {"low": 0, "high": 100, "unit": "mg/dL"},
    "HDL": {"low": 40, "high": 999, "unit": "mg/dL"},
    "TRIG": {"low": 0, "high": 150, "unit": "mg/dL"},
}
