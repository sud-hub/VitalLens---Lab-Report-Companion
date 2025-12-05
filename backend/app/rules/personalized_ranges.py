"""
Personalized reference ranges for Indian adults based on gender and age.

This module provides gender and age-specific reference ranges for lab tests,
particularly for CBC, Metabolic, and Lipid panels. These ranges are tailored
for adult Indian populations with considerations for:
- Sex-specific differences (RBC, HGB, HCT, HDL)
- Age-related variations
- Lab-specific overrides (when available)

References are based on standard Indian clinical practice and international guidelines
adapted for Indian demographics.
"""

from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class ReferenceRange:
    """Reference range with low and high thresholds."""
    low: float
    high: float
    unit: str


def get_personalized_range(
    test_key: str,
    gender: Optional[str] = None,
    age: Optional[int] = None,
    default_low: Optional[float] = None,
    default_high: Optional[float] = None
) -> Tuple[Optional[float], Optional[float]]:
    """
    Get personalized reference range based on patient demographics.
    
    Args:
        test_key: Test identifier (e.g., 'RBC', 'HGB', 'HDL')
        gender: Patient gender ('M' or 'F')
        age: Patient age in years
        default_low: Default lower limit from database
        default_high: Default upper limit from database
    
    Returns:
        Tuple of (ref_low, ref_high) adjusted for demographics
        Returns (default_low, default_high) if no personalization applies
    """
    # If no demographics available, use defaults
    if gender is None and age is None:
        return (default_low, default_high)
    
    # Apply gender-specific ranges for CBC tests
    if test_key == "RBC":
        return _get_rbc_range(gender, age, default_low, default_high)
    elif test_key == "HGB":
        return _get_hgb_range(gender, age, default_low, default_high)
    elif test_key == "HCT":
        return _get_hct_range(gender, age, default_low, default_high)
    elif test_key == "HDL":
        return _get_hdl_range(gender, age, default_low, default_high)
    
    # For other tests, use defaults (can be extended in future)
    return (default_low, default_high)


def _get_rbc_range(
    gender: Optional[str],
    age: Optional[int],
    default_low: Optional[float],
    default_high: Optional[float]
) -> Tuple[Optional[float], Optional[float]]:
    """
    Get RBC reference range based on gender and age.
    
    RBC ranges for Indian adults (10^6/µL):
    - Males: 4.5 - 5.9
    - Females: 4.0 - 5.2
    - Age adjustments: Slight decrease after 60 years
    """
    if gender == "M":
        low, high = 4.5, 5.9
    elif gender == "F":
        low, high = 4.0, 5.2
    else:
        # Use defaults if gender not specified
        return (default_low, default_high)
    
    # Age adjustment for elderly (>60 years)
    if age and age > 60:
        low = max(low - 0.2, 3.5)  # Slight decrease, but not below 3.5
        high = high - 0.2
    
    return (low, high)


def _get_hgb_range(
    gender: Optional[str],
    age: Optional[int],
    default_low: Optional[float],
    default_high: Optional[float]
) -> Tuple[Optional[float], Optional[float]]:
    """
    Get Hemoglobin reference range based on gender and age.
    
    Hemoglobin ranges for Indian adults (g/dL):
    - Males: 13.5 - 17.5
    - Females: 12.0 - 15.5
    - Age adjustments: Slight decrease after 60 years
    """
    if gender == "M":
        low, high = 13.5, 17.5
    elif gender == "F":
        low, high = 12.0, 15.5
    else:
        return (default_low, default_high)
    
    # Age adjustment for elderly (>60 years)
    if age and age > 60:
        low = max(low - 0.5, 11.0)  # Slight decrease
        high = high - 0.5
    
    return (low, high)


def _get_hct_range(
    gender: Optional[str],
    age: Optional[int],
    default_low: Optional[float],
    default_high: Optional[float]
) -> Tuple[Optional[float], Optional[float]]:
    """
    Get Hematocrit reference range based on gender and age.
    
    Hematocrit ranges for Indian adults (%):
    - Males: 40.0 - 54.0
    - Females: 36.0 - 46.0
    - Age adjustments: Slight decrease after 60 years
    """
    if gender == "M":
        low, high = 40.0, 54.0
    elif gender == "F":
        low, high = 36.0, 46.0
    else:
        return (default_low, default_high)
    
    # Age adjustment for elderly (>60 years)
    if age and age > 60:
        low = max(low - 2.0, 33.0)
        high = high - 2.0
    
    return (low, high)


def _get_hdl_range(
    gender: Optional[str],
    age: Optional[int],
    default_low: Optional[float],
    default_high: Optional[float]
) -> Tuple[Optional[float], Optional[float]]:
    """
    Get HDL Cholesterol reference range based on gender and age.
    
    HDL ranges for Indian adults (mg/dL):
    - Males: 40 - 999 (protective if ≥60)
    - Females: 50 - 999 (protective if ≥60)
    
    Note: High HDL is generally protective, so upper limit is set very high.
    The guidance engine should flag HDL ≥60 as "protective/excellent".
    """
    if gender == "M":
        low = 40.0
    elif gender == "F":
        low = 50.0
    else:
        # Use default if gender not specified
        return (default_low, default_high)
    
    # Upper limit remains very high (HDL is "good cholesterol")
    high = 999.0
    
    return (low, high)


def get_hdl_status_modifier(value: float, gender: Optional[str]) -> Optional[str]:
    """
    Get special status modifier for HDL values.
    
    Args:
        value: HDL value in mg/dL
        gender: Patient gender
    
    Returns:
        Status modifier: 'PROTECTIVE' if HDL ≥60, None otherwise
    """
    if value >= 60.0:
        return "PROTECTIVE"
    return None


def get_age_category(age: Optional[int]) -> str:
    """
    Categorize age into groups for reference.
    
    Args:
        age: Age in years
    
    Returns:
        Age category string
    """
    if age is None:
        return "UNKNOWN"
    elif age < 18:
        return "PEDIATRIC"  # Not supported in current implementation
    elif age < 40:
        return "YOUNG_ADULT"
    elif age < 60:
        return "MIDDLE_AGED"
    else:
        return "ELDERLY"
