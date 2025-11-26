"""
Tests for the guidance engine module.

This module tests the generation of educational insights and guidance
for lab test results, including trend computation and panel-specific messages.
"""

import pytest
from app.rules.guidance_engine import generate_guidance, _compute_trend, _is_improving
from app.db.models import TestType, Panel


class MockPanel:
    """Mock Panel object for testing."""
    def __init__(self, key: str, display_name: str):
        self.key = key
        self.display_name = display_name


class MockTestType:
    """Mock TestType object for testing."""
    def __init__(self, key: str, display_name: str, panel_key: str, ref_low: float = None, ref_high: float = None, unit: str = "mg/dL"):
        self.key = key
        self.display_name = display_name
        self.panel = MockPanel(panel_key, f"{panel_key} Panel")
        self.ref_low = ref_low
        self.ref_high = ref_high
        self.unit = unit


class TestGenerateGuidance:
    """Test suite for generate_guidance function."""
    
    def test_guidance_includes_all_required_fields(self):
        """Test that guidance includes message, trend, suggestions, and disclaimer."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        
        result = generate_guidance(test_type, 7.0, "NORMAL")
        
        assert "message" in result
        assert "trend" in result
        assert "suggestions" in result
        assert "disclaimer" in result
        assert isinstance(result["message"], str)
        assert isinstance(result["suggestions"], list)
        assert isinstance(result["disclaimer"], str)
    
    def test_guidance_always_includes_disclaimer(self):
        """Test that disclaimer is always present (Requirement 12.5, 13.4, 13.5)."""
        test_type = MockTestType("GLUCOSE", "Glucose", "METABOLIC", 70, 100)
        
        result = generate_guidance(test_type, 85, "NORMAL")
        
        assert "disclaimer" in result
        assert len(result["disclaimer"]) > 0
        assert "NOT a medical diagnosis" in result["disclaimer"]
        assert "consult" in result["disclaimer"].lower()
    
    def test_cbc_guidance_mentions_blood_cells(self):
        """Test that CBC guidance mentions blood cell levels (Requirement 13.1)."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        
        result = generate_guidance(test_type, 7.0, "NORMAL")
        
        # Should mention blood cells or related terms
        message_lower = result["message"].lower()
        assert any(term in message_lower for term in ["blood", "cell", "wbc", "white blood"])
    
    def test_metabolic_guidance_mentions_organ_function(self):
        """Test that Metabolic guidance mentions organ function (Requirement 13.2)."""
        test_type = MockTestType("CREATININE", "Creatinine", "METABOLIC", 0.7, 1.3)
        
        result = generate_guidance(test_type, 1.0, "NORMAL")
        
        # Should mention kidney or organ function
        message_lower = result["message"].lower()
        assert any(term in message_lower for term in ["kidney", "organ", "function", "filter"])
    
    def test_lipid_guidance_mentions_heart_health(self):
        """Test that Lipid guidance mentions heart health (Requirement 13.3)."""
        test_type = MockTestType("LDL", "LDL Cholesterol", "LIPID", 0, 100)
        
        result = generate_guidance(test_type, 80, "NORMAL")
        
        # Should mention heart, cardiovascular, or cholesterol
        message_lower = result["message"].lower()
        assert any(term in message_lower for term in ["heart", "cardiovascular", "cholesterol", "arteries"])
    
    def test_trend_is_none_without_previous_value(self):
        """Test that trend is None when no previous value provided."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        
        result = generate_guidance(test_type, 7.0, "NORMAL", previous_value=None)
        
        assert result["trend"] is None
    
    def test_trend_computed_with_previous_value(self):
        """Test that trend is computed when previous value provided (Requirement 12.4)."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        
        result = generate_guidance(test_type, 7.0, "NORMAL", previous_value=6.0)
        
        assert result["trend"] is not None
        assert result["trend"] in ["improving", "worsening", "stable"]


class TestComputeTrend:
    """Test suite for _compute_trend function."""
    
    def test_trend_is_none_without_previous_value(self):
        """Test that trend returns None when no previous value."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        
        trend = _compute_trend(test_type, 7.0, "NORMAL", None)
        
        assert trend is None
    
    def test_trend_stable_for_small_changes(self):
        """Test that small changes result in 'stable' trend."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        # Range is 6.5, 5% is 0.325
        
        trend = _compute_trend(test_type, 7.0, "NORMAL", 7.1)
        
        assert trend == "stable"
    
    def test_trend_improving_when_moving_toward_normal(self):
        """Test that moving toward normal range is 'improving'."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        # Normal midpoint is 7.75
        
        # Moving from 12.0 (high) to 10.0 (closer to normal)
        trend = _compute_trend(test_type, 10.0, "HIGH", 12.0)
        
        assert trend == "improving"
    
    def test_trend_worsening_when_moving_away_from_normal(self):
        """Test that moving away from normal range is 'worsening'."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        # Normal midpoint is 7.75
        
        # Moving from 10.0 to 12.0 (further from normal)
        trend = _compute_trend(test_type, 12.0, "HIGH", 10.0)
        
        assert trend == "worsening"
    
    def test_trend_with_no_reference_ranges(self):
        """Test trend computation when reference ranges are not defined."""
        test_type = MockTestType("UNKNOWN", "Unknown Test", "CBC", None, None)
        
        # Should return stable for similar values
        trend = _compute_trend(test_type, 100.0, "UNKNOWN", 100.5)
        
        assert trend == "stable"


class TestIsImproving:
    """Test suite for _is_improving helper function."""
    
    def test_improving_when_closer_to_midpoint(self):
        """Test that values closer to normal midpoint are improving."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        # Midpoint is 7.75
        
        # Current 8.0 is closer to 7.75 than previous 10.0
        is_improving = _is_improving(test_type, 8.0, 10.0, "NORMAL")
        
        assert is_improving is True
    
    def test_not_improving_when_further_from_midpoint(self):
        """Test that values further from normal midpoint are not improving."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        # Midpoint is 7.75
        
        # Current 10.0 is further from 7.75 than previous 8.0
        is_improving = _is_improving(test_type, 10.0, 8.0, "NORMAL")
        
        assert is_improving is False
    
    def test_improving_from_low_to_normal(self):
        """Test that moving from low to normal is improving."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        # Midpoint is 7.75
        
        # Moving from 3.0 (low) to 5.0 (closer to normal)
        is_improving = _is_improving(test_type, 5.0, 3.0, "LOW")
        
        assert is_improving is True


class TestPanelSpecificMessages:
    """Test that each panel generates appropriate messages."""
    
    def test_all_cbc_tests_generate_messages(self):
        """Test that all CBC tests generate appropriate messages."""
        cbc_tests = ["WBC", "RBC", "HGB", "HCT", "PLT", "MCV"]
        
        for test_key in cbc_tests:
            test_type = MockTestType(test_key, f"Test {test_key}", "CBC", 1.0, 10.0)
            result = generate_guidance(test_type, 5.0, "NORMAL")
            
            assert len(result["message"]) > 0
            assert len(result["suggestions"]) > 0
    
    def test_all_metabolic_tests_generate_messages(self):
        """Test that all Metabolic tests generate appropriate messages."""
        metabolic_tests = ["GLUCOSE", "BUN", "CREATININE", "SODIUM", "POTASSIUM", "CHLORIDE", "CO2", "CALCIUM"]
        
        for test_key in metabolic_tests:
            test_type = MockTestType(test_key, f"Test {test_key}", "METABOLIC", 1.0, 10.0)
            result = generate_guidance(test_type, 5.0, "NORMAL")
            
            assert len(result["message"]) > 0
            assert len(result["suggestions"]) > 0
    
    def test_all_lipid_tests_generate_messages(self):
        """Test that all Lipid tests generate appropriate messages."""
        lipid_tests = ["TC", "LDL", "HDL", "TRIG"]
        
        for test_key in lipid_tests:
            test_type = MockTestType(test_key, f"Test {test_key}", "LIPID", 0, 200)
            result = generate_guidance(test_type, 100, "NORMAL")
            
            assert len(result["message"]) > 0
            assert len(result["suggestions"]) > 0
    
    def test_different_statuses_generate_different_messages(self):
        """Test that different statuses generate different messages."""
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        
        normal_result = generate_guidance(test_type, 7.0, "NORMAL")
        low_result = generate_guidance(test_type, 3.0, "LOW")
        high_result = generate_guidance(test_type, 13.0, "HIGH")
        
        # Messages should be different for different statuses
        assert normal_result["message"] != low_result["message"]
        assert normal_result["message"] != high_result["message"]
        assert low_result["message"] != high_result["message"]


# Property-Based Tests using Hypothesis
from hypothesis import given, strategies as st, assume


class TestTrendComputationProperty:
    """
    Property-based tests for trend computation.
    
    Feature: lab-report-companion, Property 32: Trend computation compares values
    Validates: Requirements 12.4
    """
    
    @given(
        ref_low=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False),
        ref_high=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False),
        current_value=st.floats(min_value=0.1, max_value=200.0, allow_nan=False, allow_infinity=False),
        previous_value=st.floats(min_value=0.1, max_value=200.0, allow_nan=False, allow_infinity=False),
    )
    def test_trend_computation_returns_valid_values(self, ref_low, ref_high, current_value, previous_value):
        """
        Property: For any pair of test results (latest and previous), the system should 
        compute a trend indicator (improving, worsening, or stable) based on the value change.
        
        Feature: lab-report-companion, Property 32: Trend computation compares values
        Validates: Requirements 12.4
        """
        # Ensure ref_low < ref_high
        assume(ref_low < ref_high)
        
        # Create test type with reference ranges
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", ref_low, ref_high)
        
        # Compute status for current value
        if current_value < ref_low:
            status = "LOW"
        elif current_value <= ref_high:
            status = "NORMAL"
        else:
            status = "HIGH"
        
        # Compute trend
        trend = _compute_trend(test_type, current_value, status, previous_value)
        
        # Property: Trend must be one of the valid values
        assert trend in ["improving", "worsening", "stable"], \
            f"Trend must be 'improving', 'worsening', or 'stable', got: {trend}"
    
    @given(
        ref_low=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False),
        ref_high=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False),
        base_value=st.floats(min_value=0.1, max_value=200.0, allow_nan=False, allow_infinity=False),
    )
    def test_trend_stable_for_identical_values(self, ref_low, ref_high, base_value):
        """
        Property: For any test result, when the current and previous values are identical,
        the trend should be 'stable'.
        
        Feature: lab-report-companion, Property 32: Trend computation compares values
        Validates: Requirements 12.4
        """
        # Ensure ref_low < ref_high
        assume(ref_low < ref_high)
        
        # Create test type with reference ranges
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", ref_low, ref_high)
        
        # Compute status
        if base_value < ref_low:
            status = "LOW"
        elif base_value <= ref_high:
            status = "NORMAL"
        else:
            status = "HIGH"
        
        # Compute trend with identical values
        trend = _compute_trend(test_type, base_value, status, base_value)
        
        # Property: Identical values should always result in 'stable' trend
        assert trend == "stable", \
            f"Identical values should result in 'stable' trend, got: {trend}"
    
    @given(
        ref_low=st.floats(min_value=1.0, max_value=50.0, allow_nan=False, allow_infinity=False),
        ref_high=st.floats(min_value=51.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    )
    def test_trend_improving_when_moving_toward_normal_range(self, ref_low, ref_high):
        """
        Property: For any test result outside the normal range, when the value moves
        closer to the normal range midpoint, the trend should be 'improving'.
        
        Feature: lab-report-companion, Property 32: Trend computation compares values
        Validates: Requirements 12.4
        """
        # Create test type with reference ranges
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", ref_low, ref_high)
        
        # Calculate midpoint
        midpoint = (ref_low + ref_high) / 2
        
        # Test case 1: Moving from high toward normal
        high_previous = ref_high + 20.0
        high_current = ref_high + 10.0  # Closer to midpoint
        
        trend_high = _compute_trend(test_type, high_current, "HIGH", high_previous)
        
        # Property: Moving closer to normal should be improving
        assert trend_high == "improving", \
            f"Moving from {high_previous} to {high_current} (toward midpoint {midpoint}) should be 'improving', got: {trend_high}"
        
        # Test case 2: Moving from low toward normal
        low_previous = ref_low - 20.0
        low_current = ref_low - 10.0  # Closer to midpoint
        
        trend_low = _compute_trend(test_type, low_current, "LOW", low_previous)
        
        # Property: Moving closer to normal should be improving
        assert trend_low == "improving", \
            f"Moving from {low_previous} to {low_current} (toward midpoint {midpoint}) should be 'improving', got: {trend_low}"
    
    @given(
        ref_low=st.floats(min_value=1.0, max_value=50.0, allow_nan=False, allow_infinity=False),
        ref_high=st.floats(min_value=51.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    )
    def test_trend_worsening_when_moving_away_from_normal_range(self, ref_low, ref_high):
        """
        Property: For any test result, when the value moves further from the normal 
        range midpoint, the trend should be 'worsening'.
        
        Feature: lab-report-companion, Property 32: Trend computation compares values
        Validates: Requirements 12.4
        """
        # Create test type with reference ranges
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", ref_low, ref_high)
        
        # Calculate midpoint
        midpoint = (ref_low + ref_high) / 2
        
        # Test case 1: Moving from high further away
        high_previous = ref_high + 10.0
        high_current = ref_high + 20.0  # Further from midpoint
        
        trend_high = _compute_trend(test_type, high_current, "HIGH", high_previous)
        
        # Property: Moving further from normal should be worsening
        assert trend_high == "worsening", \
            f"Moving from {high_previous} to {high_current} (away from midpoint {midpoint}) should be 'worsening', got: {trend_high}"
        
        # Test case 2: Moving from low further away
        low_previous = ref_low - 10.0
        low_current = ref_low - 20.0  # Further from midpoint
        
        trend_low = _compute_trend(test_type, low_current, "LOW", low_previous)
        
        # Property: Moving further from normal should be worsening
        assert trend_low == "worsening", \
            f"Moving from {low_previous} to {low_current} (away from midpoint {midpoint}) should be 'worsening', got: {trend_low}"
    
    @given(
        ref_low=st.floats(min_value=1.0, max_value=50.0, allow_nan=False, allow_infinity=False),
        ref_high=st.floats(min_value=51.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        value=st.floats(min_value=0.1, max_value=200.0, allow_nan=False, allow_infinity=False),
    )
    def test_trend_stable_for_small_changes(self, ref_low, ref_high, value):
        """
        Property: For any test result, when the change between current and previous 
        values is less than 5% of the reference range, the trend should be 'stable'.
        
        Feature: lab-report-companion, Property 32: Trend computation compares values
        Validates: Requirements 12.4
        """
        # Create test type with reference ranges
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", ref_low, ref_high)
        
        # Calculate 5% of range
        range_width = ref_high - ref_low
        small_change = range_width * 0.04  # Less than 5%
        
        # Create previous value with small change
        previous_value = value + small_change
        
        # Compute status
        if value < ref_low:
            status = "LOW"
        elif value <= ref_high:
            status = "NORMAL"
        else:
            status = "HIGH"
        
        # Compute trend
        trend = _compute_trend(test_type, value, status, previous_value)
        
        # Property: Small changes should result in 'stable' trend
        assert trend == "stable", \
            f"Change of {abs(value - previous_value)} (less than 5% of range {range_width}) should be 'stable', got: {trend}"
    
    @given(
        current_value=st.floats(min_value=0.1, max_value=200.0, allow_nan=False, allow_infinity=False),
    )
    def test_trend_none_without_previous_value(self, current_value):
        """
        Property: For any test result, when there is no previous value, the trend 
        should be None.
        
        Feature: lab-report-companion, Property 32: Trend computation compares values
        Validates: Requirements 12.4
        """
        # Create test type with reference ranges
        test_type = MockTestType("WBC", "White Blood Cells", "CBC", 4.5, 11.0)
        
        # Compute status
        if current_value < 4.5:
            status = "LOW"
        elif current_value <= 11.0:
            status = "NORMAL"
        else:
            status = "HIGH"
        
        # Compute trend without previous value
        trend = _compute_trend(test_type, current_value, status, None)
        
        # Property: No previous value should result in None trend
        assert trend is None, \
            f"Trend without previous value should be None, got: {trend}"
