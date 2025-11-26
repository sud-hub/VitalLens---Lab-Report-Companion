"""
Unit tests for lab report parser.

These tests verify that the parser correctly extracts test names, values,
and units from OCR text for the three supported lab panels.
"""

import pytest
from hypothesis import given, strategies as st, settings
from app.parsing.lab_parser import (
    parse_lab_report,
    _parse_line,
    _is_supported_test,
    get_supported_test_keywords
)


class TestParseLabReport:
    """Test the main parse_lab_report function"""
    
    def test_parse_empty_ocr_result(self):
        """Test parsing empty OCR result"""
        result = parse_lab_report({"raw_text": ""})
        assert result == []
    
    def test_parse_missing_raw_text(self):
        """Test parsing OCR result without raw_text key"""
        result = parse_lab_report({})
        assert result == []
    
    def test_parse_cbc_tests(self):
        """Test parsing CBC test results"""
        ocr_text = """
        Complete Blood Count (CBC)
        
        WBC 7.2 10^3/µL
        RBC 4.8 10^6/µL
        Hemoglobin 14.5 g/dL
        Hematocrit 42.0 %
        Platelets 250 10^3/µL
        MCV 88 fL
        """
        
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Should extract all 6 CBC tests
        assert len(result) >= 6
        
        # Check that WBC was extracted
        wbc_results = [r for r in result if 'wbc' in r['test_name_raw'].lower()]
        assert len(wbc_results) == 1
        assert wbc_results[0]['value'] == 7.2
        assert '10^3' in wbc_results[0]['unit'] or 'µL' in wbc_results[0]['unit']
    
    def test_parse_metabolic_tests(self):
        """Test parsing Metabolic Panel test results"""
        ocr_text = """
        Metabolic Panel
        
        Glucose: 95 mg/dL
        BUN: 15 mg/dL
        Creatinine: 1.0 mg/dL
        Sodium: 140 mmol/L
        Potassium: 4.2 mmol/L
        Chloride: 102 mmol/L
        CO2: 25 mmol/L
        Calcium: 9.5 mg/dL
        """
        
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Should extract all 8 metabolic tests
        assert len(result) >= 8
        
        # Check that Glucose was extracted
        glucose_results = [r for r in result if 'glucose' in r['test_name_raw'].lower()]
        assert len(glucose_results) == 1
        assert glucose_results[0]['value'] == 95.0
        assert 'mg/dL' in glucose_results[0]['unit']
    
    def test_parse_lipid_tests(self):
        """Test parsing Lipid Panel test results"""
        ocr_text = """
        Lipid Panel
        
        Total Cholesterol 180 mg/dL
        LDL Cholesterol 100 mg/dL
        HDL Cholesterol 55 mg/dL
        Triglycerides 120 mg/dL
        """
        
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Should extract all 4 lipid tests
        assert len(result) >= 4
        
        # Check that cholesterol was extracted
        chol_results = [r for r in result if 'cholesterol' in r['test_name_raw'].lower()]
        assert len(chol_results) >= 1
    
    def test_parse_mixed_panels(self):
        """Test parsing report with tests from multiple panels"""
        ocr_text = """
        Lab Results
        
        WBC 7.2 10^3/µL
        Glucose: 95 mg/dL
        Total Cholesterol 180 mg/dL
        """
        
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Should extract tests from all three panels
        assert len(result) == 3
    
    def test_parse_filters_unsupported_tests(self):
        """Test that unsupported tests are filtered out"""
        ocr_text = """
        Lab Results
        
        WBC 7.2 10^3/µL
        Vitamin D 30 ng/mL
        Glucose: 95 mg/dL
        TSH 2.5 mIU/L
        """
        
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Should only extract WBC and Glucose (supported tests)
        # Vitamin D and TSH should be filtered out
        assert len(result) == 2
        test_names = [r['test_name_raw'].lower() for r in result]
        assert any('wbc' in name for name in test_names)
        assert any('glucose' in name for name in test_names)
        assert not any('vitamin' in name for name in test_names)
        assert not any('tsh' in name for name in test_names)


class TestParseLine:
    """Test the _parse_line function"""
    
    def test_parse_line_pattern1(self):
        """Test parsing: <name> <value> <unit>"""
        result = _parse_line("WBC 7.2 10^3/µL")
        assert result is not None
        assert result['test_name_raw'] == "WBC"
        assert result['value'] == 7.2
        assert '10^3' in result['unit']
    
    def test_parse_line_pattern2(self):
        """Test parsing: <name>: <value> <unit>"""
        result = _parse_line("Glucose: 95 mg/dL")
        assert result is not None
        assert 'Glucose' in result['test_name_raw']
        assert result['value'] == 95.0
        assert 'mg/dL' in result['unit']
    
    def test_parse_line_pattern3(self):
        """Test parsing: <name> <value><unit> (no space)"""
        result = _parse_line("Hemoglobin 14.5g/dL")
        assert result is not None
        assert 'Hemoglobin' in result['test_name_raw']
        assert result['value'] == 14.5
    
    def test_parse_line_with_long_name(self):
        """Test parsing test with multi-word name"""
        result = _parse_line("White Blood Cells 7.2 10^3/µL")
        assert result is not None
        assert 'White Blood Cells' in result['test_name_raw']
        assert result['value'] == 7.2
    
    def test_parse_line_empty(self):
        """Test parsing empty line"""
        result = _parse_line("")
        assert result is None
    
    def test_parse_line_header(self):
        """Test that header lines are skipped"""
        result = _parse_line("COMPLETE BLOOD COUNT")
        assert result is None
    
    def test_parse_line_no_numbers(self):
        """Test that lines without numbers are skipped"""
        result = _parse_line("Patient Name: John Doe")
        assert result is None
    
    def test_parse_line_unsupported_test(self):
        """Test that unsupported tests return None"""
        result = _parse_line("Vitamin D 30 ng/mL")
        assert result is None


class TestIsSupportedTest:
    """Test the _is_supported_test function"""
    
    def test_cbc_keywords(self):
        """Test CBC test keywords are recognized"""
        assert _is_supported_test("wbc") is True
        assert _is_supported_test("white blood cells") is True
        assert _is_supported_test("hemoglobin") is True
        assert _is_supported_test("platelets") is True
    
    def test_metabolic_keywords(self):
        """Test Metabolic Panel keywords are recognized"""
        assert _is_supported_test("glucose") is True
        assert _is_supported_test("bun") is True
        assert _is_supported_test("creatinine") is True
        assert _is_supported_test("sodium") is True
    
    def test_lipid_keywords(self):
        """Test Lipid Panel keywords are recognized"""
        assert _is_supported_test("cholesterol") is True
        assert _is_supported_test("ldl") is True
        assert _is_supported_test("hdl") is True
        assert _is_supported_test("triglycerides") is True
    
    def test_unsupported_keywords(self):
        """Test unsupported test keywords are rejected"""
        assert _is_supported_test("vitamin d") is False
        assert _is_supported_test("tsh") is False
        assert _is_supported_test("thyroid") is False
        assert _is_supported_test("") is False
    
    def test_partial_matches(self):
        """Test that partial keyword matches work"""
        assert _is_supported_test("total cholesterol") is True
        assert _is_supported_test("fasting glucose") is True
        assert _is_supported_test("white blood cell count") is True


class TestGetSupportedTestKeywords:
    """Test the get_supported_test_keywords function"""
    
    def test_returns_dict(self):
        """Test that function returns a dictionary"""
        result = get_supported_test_keywords()
        assert isinstance(result, dict)
    
    def test_has_all_panels(self):
        """Test that all three panels are included"""
        result = get_supported_test_keywords()
        assert "CBC" in result
        assert "METABOLIC" in result
        assert "LIPID" in result
    
    def test_keywords_are_lists(self):
        """Test that each panel has a list of keywords"""
        result = get_supported_test_keywords()
        assert isinstance(result["CBC"], list)
        assert isinstance(result["METABOLIC"], list)
        assert isinstance(result["LIPID"], list)
    
    def test_keywords_not_empty(self):
        """Test that each panel has keywords"""
        result = get_supported_test_keywords()
        assert len(result["CBC"]) > 0
        assert len(result["METABOLIC"]) > 0
        assert len(result["LIPID"]) > 0


class TestParserEdgeCases:
    """Test edge cases and error handling"""
    
    def test_parse_with_ocr_errors(self):
        """Test parsing text with common OCR errors"""
        ocr_text = """
        WBC 7.2 lO^3/µL
        Glucose: 9S mg/dL
        """
        
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Should still extract tests despite OCR errors
        # (postprocessing should fix l->1, O->0, S->5)
        assert len(result) >= 2
    
    def test_parse_with_extra_whitespace(self):
        """Test parsing text with excessive whitespace"""
        ocr_text = """
        
        
        WBC    7.2    10^3/µL
        
        
        Glucose:   95   mg/dL
        
        
        """
        
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Should handle extra whitespace gracefully
        assert len(result) >= 2
    
    def test_parse_with_tabs(self):
        """Test parsing text with tab separators"""
        ocr_text = "WBC\t7.2\t10^3/µL\nGlucose\t95\tmg/dL"
        
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Should handle tab-separated values
        assert len(result) >= 2
    
    def test_parse_decimal_values(self):
        """Test parsing decimal values"""
        ocr_text = """
        Creatinine: 1.05 mg/dL
        Hemoglobin 14.5 g/dL
        """
        
        result = parse_lab_report({"raw_text": ocr_text})
        
        assert len(result) == 2
        # Check decimal values are preserved
        creat = [r for r in result if 'creat' in r['test_name_raw'].lower()][0]
        assert creat['value'] == 1.05
    
    def test_parse_integer_values(self):
        """Test parsing integer values"""
        ocr_text = """
        Platelets 250 10^3/µL
        Glucose: 95 mg/dL
        """
        
        result = parse_lab_report({"raw_text": ocr_text})
        
        assert len(result) == 2
        glucose = [r for r in result if 'glucose' in r['test_name_raw'].lower()][0]
        assert glucose['value'] == 95.0



class TestPropertyBasedCBCParsing:
    """Property-based tests for CBC parsing"""
    
    # Feature: lab-report-companion, Property 8: Parser extracts CBC tests only
    @settings(max_examples=100)
    @given(
        wbc_value=st.floats(min_value=0.1, max_value=50.0, allow_nan=False, allow_infinity=False),
        rbc_value=st.floats(min_value=1.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        hgb_value=st.floats(min_value=5.0, max_value=25.0, allow_nan=False, allow_infinity=False),
        hct_value=st.floats(min_value=10.0, max_value=70.0, allow_nan=False, allow_infinity=False),
        plt_value=st.floats(min_value=50.0, max_value=800.0, allow_nan=False, allow_infinity=False),
        mcv_value=st.floats(min_value=50.0, max_value=120.0, allow_nan=False, allow_infinity=False),
        non_cbc_test=st.sampled_from([
            "Vitamin D 30 ng/mL",
            "TSH 2.5 mIU/L",
            "T4 1.2 ng/dL",
            "Ferritin 100 ng/mL",
            "B12 500 pg/mL",
            "Folate 10 ng/mL",
            "PSA 1.5 ng/mL",
            "CRP 2.0 mg/L"
        ])
    )
    def test_property_parser_extracts_cbc_tests_only(
        self, wbc_value, rbc_value, hgb_value, hct_value, plt_value, mcv_value, non_cbc_test
    ):
        """
        Property 8: Parser extracts CBC tests only
        
        For any OCR text containing CBC test names (WBC, RBC, Hemoglobin, Hematocrit, 
        Platelets, MCV), the parser should extract those tests and ignore non-CBC tests.
        
        Validates: Requirements 5.1
        """
        # Create OCR text with CBC tests and non-CBC tests
        ocr_text = f"""
        Complete Blood Count (CBC)
        
        WBC {wbc_value:.1f} 10^3/µL
        RBC {rbc_value:.1f} 10^6/µL
        Hemoglobin {hgb_value:.1f} g/dL
        Hematocrit {hct_value:.1f} %
        Platelets {plt_value:.0f} 10^3/µL
        MCV {mcv_value:.0f} fL
        
        {non_cbc_test}
        """
        
        # Parse the OCR text
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Extract test names from results
        test_names_lower = [r['test_name_raw'].lower() for r in result]
        
        # Define CBC test keywords
        cbc_keywords = ['wbc', 'rbc', 'hemoglobin', 'hematocrit', 'platelet', 'mcv']
        
        # Define non-CBC test keywords from our sample
        non_cbc_keywords = ['vitamin', 'tsh', 't4', 'ferritin', 'b12', 'folate', 'psa', 'crp']
        
        # Property: All extracted tests should be CBC tests
        for test_name in test_names_lower:
            # Check if this test name contains any CBC keyword
            is_cbc = any(keyword in test_name for keyword in cbc_keywords)
            
            # Check if this test name contains any non-CBC keyword
            is_non_cbc = any(keyword in test_name for keyword in non_cbc_keywords)
            
            # Assert: If a test is extracted, it should be a CBC test, not a non-CBC test
            assert is_cbc or not is_non_cbc, \
                f"Parser extracted non-CBC test: {test_name}"
        
        # Property: All CBC tests should be extracted (at least the 6 we provided)
        # Count how many CBC tests were extracted
        cbc_count = sum(1 for name in test_names_lower 
                       if any(keyword in name for keyword in cbc_keywords))
        
        # We should extract all 6 CBC tests
        assert cbc_count == 6, \
            f"Expected 6 CBC tests, but extracted {cbc_count}. Tests: {test_names_lower}"
        
        # Property: Non-CBC tests should NOT be extracted
        non_cbc_count = sum(1 for name in test_names_lower 
                           if any(keyword in name for keyword in non_cbc_keywords))
        
        assert non_cbc_count == 0, \
            f"Parser should not extract non-CBC tests, but found {non_cbc_count}"
        
        # Property: Extracted values should match the input values (within floating point tolerance)
        wbc_results = [r for r in result if 'wbc' in r['test_name_raw'].lower()]
        if wbc_results:
            assert abs(wbc_results[0]['value'] - wbc_value) < 0.2, \
                f"WBC value mismatch: expected {wbc_value}, got {wbc_results[0]['value']}"


class TestPropertyBasedMetabolicParsing:
    """Property-based tests for Metabolic Panel parsing"""
    
    # Feature: lab-report-companion, Property 9: Parser extracts Metabolic Panel tests only
    @settings(max_examples=100)
    @given(
        glucose_value=st.floats(min_value=50.0, max_value=300.0, allow_nan=False, allow_infinity=False),
        bun_value=st.floats(min_value=5.0, max_value=50.0, allow_nan=False, allow_infinity=False),
        creatinine_value=st.floats(min_value=0.3, max_value=5.0, allow_nan=False, allow_infinity=False),
        sodium_value=st.floats(min_value=120.0, max_value=160.0, allow_nan=False, allow_infinity=False),
        potassium_value=st.floats(min_value=2.5, max_value=7.0, allow_nan=False, allow_infinity=False),
        chloride_value=st.floats(min_value=85.0, max_value=120.0, allow_nan=False, allow_infinity=False),
        co2_value=st.floats(min_value=15.0, max_value=40.0, allow_nan=False, allow_infinity=False),
        calcium_value=st.floats(min_value=7.0, max_value=12.0, allow_nan=False, allow_infinity=False),
        unsupported_test=st.sampled_from([
            "Vitamin D 30 ng/mL",
            "TSH 2.5 mIU/L",
            "T4 1.2 ng/dL",
            "Ferritin 100 ng/mL",
            "B12 500 pg/mL",
            "Folate 10 ng/mL",
            "PSA 1.5 ng/mL",
            "CRP 2.0 mg/L"
        ])
    )
    def test_property_parser_extracts_metabolic_tests_only(
        self, glucose_value, bun_value, creatinine_value, sodium_value, 
        potassium_value, chloride_value, co2_value, calcium_value, unsupported_test
    ):
        """
        Property 9: Parser extracts Metabolic Panel tests only
        
        For any OCR text containing Metabolic Panel test names (Glucose, BUN, Creatinine, 
        Sodium, Potassium, Chloride, CO2, Calcium), the parser should extract those tests 
        and ignore unsupported tests (tests not in CBC, Metabolic, or Lipid panels).
        
        Validates: Requirements 5.2
        """
        # Create OCR text with Metabolic Panel tests and unsupported tests
        ocr_text = f"""
        Metabolic Panel (CMP/BMP)
        
        Glucose: {glucose_value:.1f} mg/dL
        BUN: {bun_value:.1f} mg/dL
        Creatinine: {creatinine_value:.2f} mg/dL
        Sodium: {sodium_value:.1f} mmol/L
        Potassium: {potassium_value:.1f} mmol/L
        Chloride: {chloride_value:.1f} mmol/L
        CO2: {co2_value:.1f} mmol/L
        Calcium: {calcium_value:.1f} mg/dL
        
        {unsupported_test}
        """
        
        # Parse the OCR text
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Extract test names from results
        test_names_lower = [r['test_name_raw'].lower() for r in result]
        
        # Define Metabolic Panel test keywords
        metabolic_keywords = [
            'glucose', 'glu', 'blood sugar',
            'bun', 'urea',
            'creatinine', 'creat',
            'sodium', 'na',
            'potassium', 'k',
            'chloride', 'cl',
            'co2', 'carbon dioxide', 'bicarbonate',
            'calcium', 'ca'
        ]
        
        # Define unsupported test keywords (not in any of the three panels)
        unsupported_keywords = [
            'vitamin', 'tsh', 't4', 'ferritin', 'b12', 'folate', 'psa', 'crp'
        ]
        
        # Property 1: All Metabolic Panel tests should be extracted (all 8 we provided)
        metabolic_count = sum(1 for name in test_names_lower 
                             if any(keyword in name for keyword in metabolic_keywords))
        
        assert metabolic_count == 8, \
            f"Expected 8 Metabolic Panel tests, but extracted {metabolic_count}. Tests: {test_names_lower}"
        
        # Property 2: Unsupported tests should NOT be extracted
        unsupported_count = sum(1 for name in test_names_lower 
                               if any(keyword in name for keyword in unsupported_keywords))
        
        assert unsupported_count == 0, \
            f"Parser should not extract unsupported tests, but found {unsupported_count}. Tests: {test_names_lower}"
        
        # Property 3: All extracted tests should be from supported panels (CBC, Metabolic, or Lipid)
        # Define all supported keywords
        cbc_keywords = ['wbc', 'rbc', 'hemoglobin', 'hematocrit', 'platelet', 'mcv']
        lipid_keywords = ['cholesterol', 'ldl', 'hdl', 'triglyceride']
        all_supported_keywords = metabolic_keywords + cbc_keywords + lipid_keywords
        
        for test_name in test_names_lower:
            is_supported = any(keyword in test_name for keyword in all_supported_keywords)
            assert is_supported, \
                f"Parser extracted unsupported test: {test_name}"
        
        # Property 4: Extracted values should match the input values (within floating point tolerance)
        glucose_results = [r for r in result if 'glucose' in r['test_name_raw'].lower()]
        if glucose_results:
            assert abs(glucose_results[0]['value'] - glucose_value) < 0.2, \
                f"Glucose value mismatch: expected {glucose_value}, got {glucose_results[0]['value']}"
        
        bun_results = [r for r in result if 'bun' in r['test_name_raw'].lower()]
        if bun_results:
            assert abs(bun_results[0]['value'] - bun_value) < 0.2, \
                f"BUN value mismatch: expected {bun_value}, got {bun_results[0]['value']}"


class TestPropertyBasedLipidParsing:
    """Property-based tests for Lipid Panel parsing"""
    
    # Feature: lab-report-companion, Property 10: Parser extracts Lipid Panel tests only
    @settings(max_examples=100)
    @given(
        total_chol_value=st.floats(min_value=100.0, max_value=400.0, allow_nan=False, allow_infinity=False),
        ldl_value=st.floats(min_value=50.0, max_value=300.0, allow_nan=False, allow_infinity=False),
        hdl_value=st.floats(min_value=20.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        trig_value=st.floats(min_value=50.0, max_value=500.0, allow_nan=False, allow_infinity=False),
        unsupported_test=st.sampled_from([
            "Vitamin D 30 ng/mL",
            "TSH 2.5 mIU/L",
            "T4 1.2 ng/dL",
            "Ferritin 100 ng/mL",
            "B12 500 pg/mL",
            "Folate 10 ng/mL",
            "PSA 1.5 ng/mL",
            "CRP 2.0 mg/L",
            "HbA1c 5.5 %",
            "Albumin 4.0 g/dL"
        ])
    )
    def test_property_parser_extracts_lipid_tests_only(
        self, total_chol_value, ldl_value, hdl_value, trig_value, unsupported_test
    ):
        """
        Property 10: Parser extracts Lipid Panel tests only
        
        For any OCR text containing Lipid Panel test names (Total Cholesterol, LDL, HDL, 
        Triglycerides), the parser should extract those tests and ignore unsupported tests 
        (tests not in CBC, Metabolic, or Lipid panels).
        
        Validates: Requirements 5.3
        """
        # Create OCR text with Lipid Panel tests and unsupported tests
        ocr_text = f"""
        Lipid Panel
        
        Total Cholesterol {total_chol_value:.1f} mg/dL
        LDL Cholesterol {ldl_value:.1f} mg/dL
        HDL Cholesterol {hdl_value:.1f} mg/dL
        Triglycerides {trig_value:.1f} mg/dL
        
        {unsupported_test}
        """
        
        # Parse the OCR text
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Extract test names from results
        test_names_lower = [r['test_name_raw'].lower() for r in result]
        
        # Define Lipid Panel test keywords
        lipid_keywords = [
            'cholesterol', 'chol',
            'ldl', 'low density',
            'hdl', 'high density',
            'triglyceride', 'trig', 'tg'
        ]
        
        # Define unsupported test keywords (not in any of the three panels)
        unsupported_keywords = [
            'vitamin', 'tsh', 't4', 'ferritin', 'b12', 'folate', 'psa', 'crp', 'hba1c', 'albumin'
        ]
        
        # Property 1: All Lipid Panel tests should be extracted (all 4 we provided)
        lipid_count = sum(1 for name in test_names_lower 
                         if any(keyword in name for keyword in lipid_keywords))
        
        assert lipid_count == 4, \
            f"Expected 4 Lipid Panel tests, but extracted {lipid_count}. Tests: {test_names_lower}"
        
        # Property 2: Unsupported tests should NOT be extracted
        unsupported_count = sum(1 for name in test_names_lower 
                               if any(keyword in name for keyword in unsupported_keywords))
        
        assert unsupported_count == 0, \
            f"Parser should not extract unsupported tests, but found {unsupported_count}. Tests: {test_names_lower}"
        
        # Property 3: All extracted tests should be from supported panels (CBC, Metabolic, or Lipid)
        # Define all supported keywords
        cbc_keywords = ['wbc', 'rbc', 'hemoglobin', 'hematocrit', 'platelet', 'mcv']
        metabolic_keywords = [
            'glucose', 'glu', 'blood sugar',
            'bun', 'urea',
            'creatinine', 'creat',
            'sodium', 'na',
            'potassium', 'k',
            'chloride', 'cl',
            'co2', 'carbon dioxide', 'bicarbonate',
            'calcium', 'ca'
        ]
        all_supported_keywords = lipid_keywords + cbc_keywords + metabolic_keywords
        
        for test_name in test_names_lower:
            is_supported = any(keyword in test_name for keyword in all_supported_keywords)
            assert is_supported, \
                f"Parser extracted unsupported test: {test_name}"
        
        # Property 4: Extracted values should match the input values (within floating point tolerance)
        # Check Total Cholesterol
        total_chol_results = [r for r in result if 'cholesterol' in r['test_name_raw'].lower() 
                             and 'ldl' not in r['test_name_raw'].lower() 
                             and 'hdl' not in r['test_name_raw'].lower()]
        if total_chol_results:
            assert abs(total_chol_results[0]['value'] - total_chol_value) < 0.2, \
                f"Total Cholesterol value mismatch: expected {total_chol_value}, got {total_chol_results[0]['value']}"
        
        # Check LDL
        ldl_results = [r for r in result if 'ldl' in r['test_name_raw'].lower()]
        if ldl_results:
            assert abs(ldl_results[0]['value'] - ldl_value) < 0.2, \
                f"LDL value mismatch: expected {ldl_value}, got {ldl_results[0]['value']}"
        
        # Check HDL
        hdl_results = [r for r in result if 'hdl' in r['test_name_raw'].lower()]
        if hdl_results:
            assert abs(hdl_results[0]['value'] - hdl_value) < 0.2, \
                f"HDL value mismatch: expected {hdl_value}, got {hdl_results[0]['value']}"
        
        # Check Triglycerides
        trig_results = [r for r in result if 'triglyceride' in r['test_name_raw'].lower()]
        if trig_results:
            assert abs(trig_results[0]['value'] - trig_value) < 0.2, \
                f"Triglycerides value mismatch: expected {trig_value}, got {trig_results[0]['value']}"


class TestPropertyBasedUnsupportedFiltering:
    """Property-based tests for unsupported test filtering"""
    
    # Feature: lab-report-companion, Property 11: Unsupported tests are filtered out
    @settings(max_examples=100)
    @given(
        # Generate a list of supported test entries with values
        num_cbc_tests=st.integers(min_value=0, max_value=3),
        num_metabolic_tests=st.integers(min_value=0, max_value=3),
        num_lipid_tests=st.integers(min_value=0, max_value=3),
        wbc_value=st.floats(min_value=0.1, max_value=50.0, allow_nan=False, allow_infinity=False),
        rbc_value=st.floats(min_value=1.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        hemoglobin_value=st.floats(min_value=5.0, max_value=25.0, allow_nan=False, allow_infinity=False),
        glucose_value=st.floats(min_value=50.0, max_value=300.0, allow_nan=False, allow_infinity=False),
        bun_value=st.floats(min_value=5.0, max_value=50.0, allow_nan=False, allow_infinity=False),
        sodium_value=st.floats(min_value=120.0, max_value=160.0, allow_nan=False, allow_infinity=False),
        total_chol_value=st.floats(min_value=100.0, max_value=400.0, allow_nan=False, allow_infinity=False),
        ldl_value=st.floats(min_value=50.0, max_value=300.0, allow_nan=False, allow_infinity=False),
        hdl_value=st.floats(min_value=20.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        # Generate random unsupported tests
        unsupported_tests=st.lists(
            st.sampled_from([
                "Vitamin D 30 ng/mL",
                "TSH 2.5 mIU/L",
                "T4 1.2 ng/dL",
                "T3 100 ng/dL",
                "Ferritin 100 ng/mL",
                "B12 500 pg/mL",
                "Folate 10 ng/mL",
                "PSA 1.5 ng/mL",
                "CRP 2.0 mg/L",
                "HbA1c 5.5 %",
                "Albumin 4.0 g/dL",
                "Bilirubin 1.0 mg/dL",
                "ALT 25 U/L",
                "AST 30 U/L",
                "ALP 70 U/L",
                "GGT 20 U/L",
                "Magnesium 2.0 mg/dL",
                "Phosphorus 3.5 mg/dL",
                "Protein 7.0 g/dL",
                "Thyroid Peroxidase 10 IU/mL",
            ]),
            min_size=1,
            max_size=10
        )
    )
    def test_property_unsupported_tests_filtered_out(
        self, num_cbc_tests, num_metabolic_tests, num_lipid_tests,
        wbc_value, rbc_value, hemoglobin_value,
        glucose_value, bun_value, sodium_value,
        total_chol_value, ldl_value, hdl_value,
        unsupported_tests
    ):
        """
        Property 11: Unsupported tests are filtered out
        
        For any OCR text containing a mix of supported and unsupported test names, 
        the parser should only extract tests belonging to the three supported panels 
        (CBC, Metabolic, Lipid) and filter out all unsupported tests.
        
        Validates: Requirements 5.4
        """
        # Ensure we have at least one supported test
        if num_cbc_tests == 0 and num_metabolic_tests == 0 and num_lipid_tests == 0:
            num_cbc_tests = 1
        
        # Build OCR text with both supported and unsupported tests
        ocr_lines = ["Lab Results\n"]
        
        # Track expected supported test count
        expected_supported_count = 0
        
        # Add CBC tests
        cbc_tests = [
            ("WBC", wbc_value, "10^3/µL"),
            ("RBC", rbc_value, "10^6/µL"),
            ("Hemoglobin", hemoglobin_value, "g/dL"),
        ]
        for i in range(min(num_cbc_tests, len(cbc_tests))):
            test_name, value, unit = cbc_tests[i]
            ocr_lines.append(f"{test_name} {value:.1f} {unit}\n")
            expected_supported_count += 1
        
        # Add Metabolic tests
        metabolic_tests = [
            ("Glucose", glucose_value, "mg/dL"),
            ("BUN", bun_value, "mg/dL"),
            ("Sodium", sodium_value, "mmol/L"),
        ]
        for i in range(min(num_metabolic_tests, len(metabolic_tests))):
            test_name, value, unit = metabolic_tests[i]
            ocr_lines.append(f"{test_name}: {value:.1f} {unit}\n")
            expected_supported_count += 1
        
        # Add Lipid tests
        lipid_tests = [
            ("Total Cholesterol", total_chol_value, "mg/dL"),
            ("LDL Cholesterol", ldl_value, "mg/dL"),
            ("HDL Cholesterol", hdl_value, "mg/dL"),
        ]
        for i in range(min(num_lipid_tests, len(lipid_tests))):
            test_name, value, unit = lipid_tests[i]
            ocr_lines.append(f"{test_name} {value:.1f} {unit}\n")
            expected_supported_count += 1
        
        # Add unsupported tests (these should be filtered out)
        for unsupported_test in unsupported_tests:
            ocr_lines.append(f"{unsupported_test}\n")
        
        ocr_text = "".join(ocr_lines)
        
        # Parse the OCR text
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Extract test names from results
        test_names_lower = [r['test_name_raw'].lower() for r in result]
        
        # Define all supported keywords
        cbc_keywords = ['wbc', 'rbc', 'hemoglobin', 'hematocrit', 'platelet', 'mcv']
        metabolic_keywords = [
            'glucose', 'glu', 'blood sugar',
            'bun', 'urea',
            'creatinine', 'creat',
            'sodium', 'na',
            'potassium', 'k',
            'chloride', 'cl',
            'co2', 'carbon dioxide', 'bicarbonate',
            'calcium', 'ca'
        ]
        lipid_keywords = [
            'cholesterol', 'chol',
            'ldl', 'low density',
            'hdl', 'high density',
            'triglyceride', 'trig', 'tg'
        ]
        all_supported_keywords = cbc_keywords + metabolic_keywords + lipid_keywords
        
        # Define unsupported keywords
        unsupported_keywords = [
            'vitamin', 'tsh', 't3', 't4', 'ferritin', 'b12', 'folate', 
            'psa', 'crp', 'hba1c', 'albumin', 'bilirubin', 'alt', 'ast', 
            'alp', 'ggt', 'magnesium', 'phosphorus', 'protein', 'thyroid', 'peroxidase'
        ]
        
        # Property 1: All extracted tests should be from supported panels
        for test_name in test_names_lower:
            is_supported = any(keyword in test_name for keyword in all_supported_keywords)
            is_unsupported = any(keyword in test_name for keyword in unsupported_keywords)
            
            # If a test is extracted, it must be supported and not unsupported
            assert is_supported, \
                f"Parser extracted test '{test_name}' which doesn't match any supported keywords"
            assert not is_unsupported, \
                f"Parser extracted unsupported test: {test_name}"
        
        # Property 2: No unsupported tests should be extracted
        unsupported_count = sum(1 for name in test_names_lower 
                               if any(keyword in name for keyword in unsupported_keywords))
        
        assert unsupported_count == 0, \
            f"Parser should not extract unsupported tests, but found {unsupported_count}. Tests: {test_names_lower}"
        
        # Property 3: All supported tests should be extracted
        assert len(result) == expected_supported_count, \
            f"Expected {expected_supported_count} supported tests, but extracted {len(result)}. Tests: {test_names_lower}"


class TestPropertyBasedValueAndUnitExtraction:
    """Property-based tests for value and unit extraction"""
    
    # Feature: lab-report-companion, Property 12: Test value extraction includes units
    @settings(max_examples=100)
    @given(
        # Generate test data with various formats
        test_data=st.lists(
            st.tuples(
                # Test name from supported panels
                st.sampled_from([
                    "WBC", "RBC", "Hemoglobin", "Hematocrit", "Platelets", "MCV",
                    "Glucose", "BUN", "Creatinine", "Sodium", "Potassium", "Chloride", "CO2", "Calcium",
                    "Total Cholesterol", "LDL Cholesterol", "HDL Cholesterol", "Triglycerides"
                ]),
                # Value
                st.floats(min_value=0.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
                # Unit
                st.sampled_from([
                    "10^3/µL", "10^6/µL", "g/dL", "%", "fL",
                    "mg/dL", "mmol/L", "mEq/L", "ng/mL", "pg/mL",
                    "U/L", "IU/L", "µg/dL", "ng/dL"
                ])
            ),
            min_size=1,
            max_size=10
        ),
        # Format style
        format_style=st.sampled_from([
            "space",      # "WBC 7.2 10^3/µL"
            "colon",      # "Glucose: 95 mg/dL"
            "no_space",   # "Hemoglobin 14.5g/dL"
            "tab",        # "WBC\t7.2\t10^3/µL"
            "multi_space" # "WBC    7.2    10^3/µL"
        ])
    )
    def test_property_value_extraction_includes_units(self, test_data, format_style):
        """
        Property 12: Test value extraction includes units
        
        For any parsed test result, the extracted data should include both the 
        numeric value and the associated unit.
        
        Validates: Requirements 5.5
        """
        # Build OCR text based on format style
        ocr_lines = ["Lab Results\n"]
        
        for test_name, value, unit in test_data:
            if format_style == "space":
                ocr_lines.append(f"{test_name} {value:.2f} {unit}\n")
            elif format_style == "colon":
                ocr_lines.append(f"{test_name}: {value:.2f} {unit}\n")
            elif format_style == "no_space":
                ocr_lines.append(f"{test_name} {value:.2f}{unit}\n")
            elif format_style == "tab":
                ocr_lines.append(f"{test_name}\t{value:.2f}\t{unit}\n")
            elif format_style == "multi_space":
                ocr_lines.append(f"{test_name}    {value:.2f}    {unit}\n")
        
        ocr_text = "".join(ocr_lines)
        
        # Parse the OCR text
        result = parse_lab_report({"raw_text": ocr_text})
        
        # Property 1: All parsed results should have a 'unit' field
        for parsed_test in result:
            assert 'unit' in parsed_test, \
                f"Parsed test result missing 'unit' field: {parsed_test}"
        
        # Property 2: All parsed results should have a 'value' field
        for parsed_test in result:
            assert 'value' in parsed_test, \
                f"Parsed test result missing 'value' field: {parsed_test}"
        
        # Property 3: The unit field should be a string (even if empty)
        for parsed_test in result:
            assert isinstance(parsed_test['unit'], str), \
                f"Unit field should be a string, got {type(parsed_test['unit'])}: {parsed_test}"
        
        # Property 4: The value field should be a number (int or float)
        for parsed_test in result:
            assert isinstance(parsed_test['value'], (int, float)), \
                f"Value field should be numeric, got {type(parsed_test['value'])}: {parsed_test}"
        
        # Property 5: For tests with units in the input, the unit should be extracted
        # We expect all our test data to have units, so all results should have non-empty units
        for parsed_test in result:
            assert parsed_test['unit'] != "", \
                f"Unit should be extracted for test: {parsed_test['test_name_raw']}, but got empty unit"
        
        # Property 6: The extracted unit should match one of the units we provided
        expected_units = [unit for _, _, unit in test_data]
        for parsed_test in result:
            # The unit might be extracted exactly or with slight variations
            # Check if the extracted unit contains or is contained in one of the expected units
            unit_found = any(
                expected_unit in parsed_test['unit'] or parsed_test['unit'] in expected_unit
                for expected_unit in expected_units
            )
            assert unit_found, \
                f"Extracted unit '{parsed_test['unit']}' doesn't match any expected units: {expected_units}"
        
        # Property 7: The extracted value should be close to one of the values we provided
        # (within floating point tolerance)
        expected_values = [value for _, value, _ in test_data]
        for parsed_test in result:
            value_found = any(
                abs(parsed_test['value'] - expected_value) < 0.1
                for expected_value in expected_values
            )
            assert value_found, \
                f"Extracted value {parsed_test['value']} doesn't match any expected values: {expected_values}"
        
        # Property 8: The number of extracted tests should match the number of input tests
        # (assuming all tests are from supported panels, which they are in our test data)
        assert len(result) == len(test_data), \
            f"Expected {len(test_data)} tests to be extracted, but got {len(result)}"
