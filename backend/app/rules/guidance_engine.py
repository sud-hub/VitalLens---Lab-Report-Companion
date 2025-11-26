"""
Guidance engine for generating educational insights about lab test results.

This module provides functionality to generate safe, non-diagnostic educational
guidance based on test results, including trend analysis and panel-specific messages.

All guidance includes prominent disclaimers that information is educational only
and not a medical diagnosis.
"""

from typing import Optional, Dict, List
from app.db.models import TestType


def generate_guidance(
    test_type: TestType,
    value: float,
    status: str,
    previous_value: Optional[float] = None
) -> Dict:
    """
    Generate educational guidance for a test result.
    
    Args:
        test_type: TestType object containing panel info and reference ranges
        value: Current test result value
        status: Current status (LOW, NORMAL, HIGH, CRITICAL_LOW, CRITICAL_HIGH, UNKNOWN)
        previous_value: Optional previous test result value for trend computation
    
    Returns:
        Dictionary containing:
        {
            "message": str,              # Educational message about the test
            "trend": str | None,         # 'improving', 'worsening', 'stable', or None
            "suggestions": list[str],    # List of general suggestions
            "disclaimer": str            # Medical disclaimer
        }
    
    Validates: Requirements 12.3, 12.4, 12.5, 13.1, 13.2, 13.3, 13.4, 13.5
    """
    # Requirement 12.4: Compute trend indicator when previous result exists
    trend = _compute_trend(test_type, value, status, previous_value)
    
    # Requirement 12.3, 13.1, 13.2, 13.3: Generate panel-specific messages
    panel_key = test_type.panel.key
    
    if panel_key == "CBC":
        message = _generate_cbc_message(test_type, status)
        suggestions = _generate_cbc_suggestions(test_type, status)
    elif panel_key == "METABOLIC":
        message = _generate_metabolic_message(test_type, status)
        suggestions = _generate_metabolic_suggestions(test_type, status)
    elif panel_key == "LIPID":
        message = _generate_lipid_message(test_type, status)
        suggestions = _generate_lipid_suggestions(test_type, status)
    else:
        message = f"This test measures {test_type.display_name}."
        suggestions = ["Consult your doctor for interpretation of this result."]
    
    # Requirement 12.5, 13.4, 13.5: Always include disclaimer
    disclaimer = (
        "This is general educational information and NOT a medical diagnosis. "
        "Please consult a qualified doctor for medical advice and clinical decisions."
    )
    
    return {
        "message": message,
        "trend": trend,
        "suggestions": suggestions,
        "disclaimer": disclaimer
    }


def _compute_trend(
    test_type: TestType,
    current_value: float,
    current_status: str,
    previous_value: Optional[float]
) -> Optional[str]:
    """
    Compute trend indicator by comparing current and previous values.
    
    Args:
        test_type: TestType object with reference ranges
        current_value: Current test result value
        current_status: Current status string
        previous_value: Previous test result value (None if no history)
    
    Returns:
        'improving', 'worsening', 'stable', or None if no previous value
        
    Trend logic:
        - stable: Change is less than 5% of reference range
        - improving: Moving toward normal range
        - worsening: Moving away from normal range
    
    Validates: Requirement 12.4
    """
    if previous_value is None:
        return None
    
    # If no reference ranges, we can't determine improvement direction
    if test_type.ref_low is None or test_type.ref_high is None:
        # Just check if values are similar
        if abs(current_value - previous_value) < abs(current_value * 0.05):
            return "stable"
        return None
    
    # Calculate 5% of reference range as threshold for "stable"
    range_width = test_type.ref_high - test_type.ref_low
    stability_threshold = range_width * 0.05
    
    # Check if change is minimal (stable)
    if abs(current_value - previous_value) < stability_threshold:
        return "stable"
    
    # Determine if improving or worsening based on movement toward/away from normal
    is_improving = _is_improving(test_type, current_value, previous_value, current_status)
    
    return "improving" if is_improving else "worsening"


def _is_improving(
    test_type: TestType,
    current_value: float,
    previous_value: float,
    current_status: str
) -> bool:
    """
    Determine if the trend is improving (moving toward normal range).
    
    Args:
        test_type: TestType with reference ranges
        current_value: Current test value
        previous_value: Previous test value
        current_status: Current status
    
    Returns:
        True if improving, False if worsening
    """
    if test_type.ref_low is None or test_type.ref_high is None:
        return False
    
    # Calculate midpoint of normal range
    normal_midpoint = (test_type.ref_low + test_type.ref_high) / 2
    
    # Calculate distances from normal midpoint
    current_distance = abs(current_value - normal_midpoint)
    previous_distance = abs(previous_value - normal_midpoint)
    
    # Improving if current value is closer to normal midpoint than previous
    return current_distance < previous_distance


def _generate_cbc_message(test_type: TestType, status: str) -> str:
    """
    Generate CBC-specific educational messages about blood cell levels.
    
    Validates: Requirement 13.1
    """
    test_key = test_type.key
    
    # General information about blood cell levels for CBC tests
    messages = {
        "WBC": {
            "NORMAL": "White blood cells (WBC) help fight infections. Your level is within the normal range.",
            "LOW": "White blood cells (WBC) help fight infections. A low count may affect your immune system's ability to fight infections.",
            "HIGH": "White blood cells (WBC) help fight infections. An elevated count may indicate your body is responding to an infection or inflammation.",
            "CRITICAL_LOW": "White blood cells (WBC) help fight infections. A very low count significantly affects immune function.",
            "CRITICAL_HIGH": "White blood cells (WBC) help fight infections. A very high count requires medical attention.",
        },
        "RBC": {
            "NORMAL": "Red blood cells (RBC) carry oxygen throughout your body. Your level is within the normal range.",
            "LOW": "Red blood cells (RBC) carry oxygen throughout your body. A low count may lead to fatigue and weakness.",
            "HIGH": "Red blood cells (RBC) carry oxygen throughout your body. An elevated count may affect blood flow.",
            "CRITICAL_LOW": "Red blood cells (RBC) carry oxygen throughout your body. A very low count can cause severe symptoms.",
            "CRITICAL_HIGH": "Red blood cells (RBC) carry oxygen throughout your body. A very high count requires medical attention.",
        },
        "HGB": {
            "NORMAL": "Hemoglobin carries oxygen in your blood. Your level is within the normal range.",
            "LOW": "Hemoglobin carries oxygen in your blood. Low levels may indicate anemia and can cause fatigue.",
            "HIGH": "Hemoglobin carries oxygen in your blood. Elevated levels may affect blood thickness.",
            "CRITICAL_LOW": "Hemoglobin carries oxygen in your blood. Very low levels require immediate attention.",
            "CRITICAL_HIGH": "Hemoglobin carries oxygen in your blood. Very high levels require medical attention.",
        },
        "HCT": {
            "NORMAL": "Hematocrit measures the proportion of blood made up of red blood cells. Your level is within the normal range.",
            "LOW": "Hematocrit measures the proportion of blood made up of red blood cells. Low levels may indicate anemia.",
            "HIGH": "Hematocrit measures the proportion of blood made up of red blood cells. High levels may affect blood flow.",
            "CRITICAL_LOW": "Hematocrit measures the proportion of blood made up of red blood cells. Very low levels require attention.",
            "CRITICAL_HIGH": "Hematocrit measures the proportion of blood made up of red blood cells. Very high levels require medical attention.",
        },
        "PLT": {
            "NORMAL": "Platelets help your blood clot. Your level is within the normal range.",
            "LOW": "Platelets help your blood clot. Low counts may increase bleeding risk.",
            "HIGH": "Platelets help your blood clot. High counts may affect blood clotting.",
            "CRITICAL_LOW": "Platelets help your blood clot. Very low counts significantly increase bleeding risk.",
            "CRITICAL_HIGH": "Platelets help your blood clot. Very high counts require medical attention.",
        },
        "MCV": {
            "NORMAL": "Mean Corpuscular Volume (MCV) measures the average size of your red blood cells. Your level is within the normal range.",
            "LOW": "Mean Corpuscular Volume (MCV) measures the average size of your red blood cells. Small cells may indicate certain types of anemia.",
            "HIGH": "Mean Corpuscular Volume (MCV) measures the average size of your red blood cells. Large cells may indicate vitamin deficiencies.",
            "CRITICAL_LOW": "Mean Corpuscular Volume (MCV) measures the average size of your red blood cells. Very small cells require evaluation.",
            "CRITICAL_HIGH": "Mean Corpuscular Volume (MCV) measures the average size of your red blood cells. Very large cells require evaluation.",
        },
    }
    
    if test_key in messages and status in messages[test_key]:
        return messages[test_key][status]
    
    # Fallback message
    return f"{test_type.display_name} is a measure of blood cell levels. Your result is {status}."


def _generate_metabolic_message(test_type: TestType, status: str) -> str:
    """
    Generate Metabolic Panel-specific educational messages about organ function.
    
    Validates: Requirement 13.2
    """
    test_key = test_type.key
    
    # General information about organ function for metabolic tests
    messages = {
        "GLUCOSE": {
            "NORMAL": "Glucose is your blood sugar level. Your level is within the normal range.",
            "LOW": "Glucose is your blood sugar level. Low levels can cause symptoms like shakiness and confusion.",
            "HIGH": "Glucose is your blood sugar level. Elevated levels may indicate prediabetes or diabetes.",
            "CRITICAL_LOW": "Glucose is your blood sugar level. Very low levels require immediate attention.",
            "CRITICAL_HIGH": "Glucose is your blood sugar level. Very high levels require medical attention.",
        },
        "BUN": {
            "NORMAL": "Blood Urea Nitrogen (BUN) reflects kidney function. Your level is within the normal range.",
            "LOW": "Blood Urea Nitrogen (BUN) reflects kidney function. Low levels are usually not concerning.",
            "HIGH": "Blood Urea Nitrogen (BUN) reflects kidney function. Elevated levels may indicate kidney stress or dehydration.",
            "CRITICAL_LOW": "Blood Urea Nitrogen (BUN) reflects kidney function. Very low levels may need evaluation.",
            "CRITICAL_HIGH": "Blood Urea Nitrogen (BUN) reflects kidney function. Very high levels require medical attention.",
        },
        "CREATININE": {
            "NORMAL": "Creatinine is a waste product filtered by your kidneys. Your level is within the normal range.",
            "LOW": "Creatinine is a waste product filtered by your kidneys. Low levels are usually not concerning.",
            "HIGH": "Creatinine is a waste product filtered by your kidneys. Elevated levels may indicate reduced kidney function.",
            "CRITICAL_LOW": "Creatinine is a waste product filtered by your kidneys. Very low levels may need evaluation.",
            "CRITICAL_HIGH": "Creatinine is a waste product filtered by your kidneys. Very high levels require medical attention.",
        },
        "SODIUM": {
            "NORMAL": "Sodium is an electrolyte that helps regulate fluid balance. Your level is within the normal range.",
            "LOW": "Sodium is an electrolyte that helps regulate fluid balance. Low levels can cause confusion and weakness.",
            "HIGH": "Sodium is an electrolyte that helps regulate fluid balance. High levels may indicate dehydration.",
            "CRITICAL_LOW": "Sodium is an electrolyte that helps regulate fluid balance. Very low levels require immediate attention.",
            "CRITICAL_HIGH": "Sodium is an electrolyte that helps regulate fluid balance. Very high levels require medical attention.",
        },
        "POTASSIUM": {
            "NORMAL": "Potassium is essential for heart and muscle function. Your level is within the normal range.",
            "LOW": "Potassium is essential for heart and muscle function. Low levels can affect heart rhythm and muscle strength.",
            "HIGH": "Potassium is essential for heart and muscle function. High levels can affect heart rhythm.",
            "CRITICAL_LOW": "Potassium is essential for heart and muscle function. Very low levels require immediate attention.",
            "CRITICAL_HIGH": "Potassium is essential for heart and muscle function. Very high levels require immediate attention.",
        },
        "CHLORIDE": {
            "NORMAL": "Chloride is an electrolyte that helps maintain fluid balance. Your level is within the normal range.",
            "LOW": "Chloride is an electrolyte that helps maintain fluid balance. Low levels may indicate fluid imbalances.",
            "HIGH": "Chloride is an electrolyte that helps maintain fluid balance. High levels may indicate dehydration.",
            "CRITICAL_LOW": "Chloride is an electrolyte that helps maintain fluid balance. Very low levels require evaluation.",
            "CRITICAL_HIGH": "Chloride is an electrolyte that helps maintain fluid balance. Very high levels require evaluation.",
        },
        "CO2": {
            "NORMAL": "CO2 (bicarbonate) helps maintain your body's pH balance. Your level is within the normal range.",
            "LOW": "CO2 (bicarbonate) helps maintain your body's pH balance. Low levels may indicate metabolic acidosis.",
            "HIGH": "CO2 (bicarbonate) helps maintain your body's pH balance. High levels may indicate metabolic alkalosis.",
            "CRITICAL_LOW": "CO2 (bicarbonate) helps maintain your body's pH balance. Very low levels require medical attention.",
            "CRITICAL_HIGH": "CO2 (bicarbonate) helps maintain your body's pH balance. Very high levels require medical attention.",
        },
        "CALCIUM": {
            "NORMAL": "Calcium is important for bone health and muscle function. Your level is within the normal range.",
            "LOW": "Calcium is important for bone health and muscle function. Low levels can affect bones and muscles.",
            "HIGH": "Calcium is important for bone health and muscle function. High levels may indicate various conditions.",
            "CRITICAL_LOW": "Calcium is important for bone health and muscle function. Very low levels require medical attention.",
            "CRITICAL_HIGH": "Calcium is important for bone health and muscle function. Very high levels require medical attention.",
        },
    }
    
    if test_key in messages and status in messages[test_key]:
        return messages[test_key][status]
    
    # Fallback message
    return f"{test_type.display_name} is a measure of organ function. Your result is {status}."


def _generate_lipid_message(test_type: TestType, status: str) -> str:
    """
    Generate Lipid Panel-specific educational messages about heart health.
    
    Validates: Requirement 13.3
    """
    test_key = test_type.key
    
    # General information about heart health risk factors for lipid tests
    messages = {
        "TC": {
            "NORMAL": "Total Cholesterol measures all cholesterol in your blood. Your level is within the desirable range.",
            "LOW": "Total Cholesterol measures all cholesterol in your blood. Low levels are generally favorable for heart health.",
            "HIGH": "Total Cholesterol measures all cholesterol in your blood. Elevated levels may increase cardiovascular risk.",
            "CRITICAL_LOW": "Total Cholesterol measures all cholesterol in your blood. Very low levels may need evaluation.",
            "CRITICAL_HIGH": "Total Cholesterol measures all cholesterol in your blood. Very high levels significantly increase cardiovascular risk.",
        },
        "LDL": {
            "NORMAL": "LDL (\"bad\" cholesterol) can build up in arteries. Your level is within the optimal range.",
            "LOW": "LDL (\"bad\" cholesterol) can build up in arteries. Low levels are favorable for heart health.",
            "HIGH": "LDL (\"bad\" cholesterol) can build up in arteries. Elevated levels increase risk of heart disease.",
            "CRITICAL_LOW": "LDL (\"bad\" cholesterol) can build up in arteries. Very low levels are generally not concerning.",
            "CRITICAL_HIGH": "LDL (\"bad\" cholesterol) can build up in arteries. Very high levels significantly increase heart disease risk.",
        },
        "HDL": {
            "NORMAL": "HDL (\"good\" cholesterol) helps remove cholesterol from arteries. Your level is within the protective range.",
            "LOW": "HDL (\"good\" cholesterol) helps remove cholesterol from arteries. Low levels may increase cardiovascular risk.",
            "HIGH": "HDL (\"good\" cholesterol) helps remove cholesterol from arteries. High levels are generally protective for heart health.",
            "CRITICAL_LOW": "HDL (\"good\" cholesterol) helps remove cholesterol from arteries. Very low levels increase heart disease risk.",
            "CRITICAL_HIGH": "HDL (\"good\" cholesterol) helps remove cholesterol from arteries. Very high levels are generally favorable.",
        },
        "TRIG": {
            "NORMAL": "Triglycerides are a type of fat in your blood. Your level is within the normal range.",
            "LOW": "Triglycerides are a type of fat in your blood. Low levels are generally not concerning.",
            "HIGH": "Triglycerides are a type of fat in your blood. Elevated levels may increase cardiovascular risk.",
            "CRITICAL_LOW": "Triglycerides are a type of fat in your blood. Very low levels are generally not concerning.",
            "CRITICAL_HIGH": "Triglycerides are a type of fat in your blood. Very high levels significantly increase cardiovascular risk.",
        },
    }
    
    if test_key in messages and status in messages[test_key]:
        return messages[test_key][status]
    
    # Fallback message
    return f"{test_type.display_name} is a measure of heart health risk factors. Your result is {status}."


def _generate_cbc_suggestions(test_type: TestType, status: str) -> List[str]:
    """Generate general suggestions for CBC test results."""
    if status in ["NORMAL"]:
        return [
            "Continue maintaining a healthy lifestyle.",
            "Regular check-ups help monitor your health over time.",
        ]
    elif status in ["LOW", "CRITICAL_LOW"]:
        return [
            "Discuss this result with your doctor.",
            "Your doctor may recommend additional tests or evaluation.",
            "Follow your doctor's guidance for any necessary treatment.",
        ]
    elif status in ["HIGH", "CRITICAL_HIGH"]:
        return [
            "Discuss this result with your doctor.",
            "Your doctor may recommend additional tests to determine the cause.",
            "Follow your doctor's guidance for any necessary treatment.",
        ]
    else:
        return ["Consult your doctor for interpretation of this result."]


def _generate_metabolic_suggestions(test_type: TestType, status: str) -> List[str]:
    """Generate general suggestions for Metabolic Panel test results."""
    if status in ["NORMAL"]:
        return [
            "Continue maintaining a healthy lifestyle.",
            "Stay hydrated and maintain a balanced diet.",
            "Regular monitoring helps track your health over time.",
        ]
    elif status in ["LOW", "CRITICAL_LOW"]:
        return [
            "Discuss this result with your doctor.",
            "Your doctor may recommend dietary changes or further evaluation.",
            "Follow your doctor's guidance for any necessary treatment.",
        ]
    elif status in ["HIGH", "CRITICAL_HIGH"]:
        return [
            "Discuss this result with your doctor.",
            "Your doctor may recommend lifestyle modifications or further testing.",
            "Follow your doctor's guidance for any necessary treatment.",
        ]
    else:
        return ["Consult your doctor for interpretation of this result."]


def _generate_lipid_suggestions(test_type: TestType, status: str) -> List[str]:
    """Generate general suggestions for Lipid Panel test results."""
    if status in ["NORMAL"]:
        return [
            "Continue maintaining heart-healthy habits.",
            "Regular exercise and a balanced diet support cardiovascular health.",
            "Regular monitoring helps track your heart health over time.",
        ]
    elif status in ["LOW", "CRITICAL_LOW"]:
        # For lipids, low is often good (except HDL)
        if test_type.key == "HDL":
            return [
                "Discuss this result with your doctor.",
                "Your doctor may recommend lifestyle changes to raise HDL levels.",
                "Regular exercise can help improve HDL cholesterol.",
            ]
        else:
            return [
                "Low levels are generally favorable for heart health.",
                "Continue maintaining healthy habits.",
            ]
    elif status in ["HIGH", "CRITICAL_HIGH"]:
        return [
            "Discuss this result with your doctor.",
            "Your doctor may recommend dietary changes, exercise, or medication.",
            "Heart-healthy lifestyle changes can help improve lipid levels.",
            "Follow your doctor's guidance for managing cardiovascular risk.",
        ]
    else:
        return ["Consult your doctor for interpretation of this result."]
