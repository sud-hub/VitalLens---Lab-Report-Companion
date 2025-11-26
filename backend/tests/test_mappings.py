"""
Unit tests for test name mapping functionality.

These tests verify that the map_test_name_to_type function correctly
maps raw test names to canonical TestType records using the TestAlias table.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import Panel, TestType, TestAlias
from app.parsing.mappings import map_test_name_to_type


# Create an in-memory SQLite database for testing
@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Seed test data
    # Create panels
    cbc_panel = Panel(key="CBC", display_name="Complete Blood Count")
    metabolic_panel = Panel(key="METABOLIC", display_name="Metabolic Panel")
    lipid_panel = Panel(key="LIPID", display_name="Lipid Panel")
    
    session.add_all([cbc_panel, metabolic_panel, lipid_panel])
    session.flush()
    
    # Create test types
    wbc_test = TestType(
        panel_id=cbc_panel.id,
        key="WBC",
        display_name="White Blood Cells",
        unit="10^3/µL",
        ref_low=4.5,
        ref_high=11.0
    )
    
    glucose_test = TestType(
        panel_id=metabolic_panel.id,
        key="GLUCOSE",
        display_name="Glucose",
        unit="mg/dL",
        ref_low=70.0,
        ref_high=100.0
    )
    
    ldl_test = TestType(
        panel_id=lipid_panel.id,
        key="LDL",
        display_name="LDL Cholesterol",
        unit="mg/dL",
        ref_low=0.0,
        ref_high=100.0
    )
    
    session.add_all([wbc_test, glucose_test, ldl_test])
    session.flush()
    
    # Create test aliases
    wbc_aliases = [
        TestAlias(alias="wbc", test_type_id=wbc_test.id),
        TestAlias(alias="white blood cells", test_type_id=wbc_test.id),
        TestAlias(alias="white blood cell", test_type_id=wbc_test.id),
        TestAlias(alias="leukocytes", test_type_id=wbc_test.id),
    ]
    
    glucose_aliases = [
        TestAlias(alias="glucose", test_type_id=glucose_test.id),
        TestAlias(alias="glu", test_type_id=glucose_test.id),
        TestAlias(alias="blood glucose", test_type_id=glucose_test.id),
        TestAlias(alias="blood sugar", test_type_id=glucose_test.id),
    ]
    
    ldl_aliases = [
        TestAlias(alias="ldl", test_type_id=ldl_test.id),
        TestAlias(alias="ldl cholesterol", test_type_id=ldl_test.id),
        TestAlias(alias="ldl-c", test_type_id=ldl_test.id),
        TestAlias(alias="low density lipoprotein", test_type_id=ldl_test.id),
    ]
    
    session.add_all(wbc_aliases + glucose_aliases + ldl_aliases)
    session.commit()
    
    yield session
    
    session.close()


class TestMapTestNameToType:
    """Test the map_test_name_to_type function"""
    
    def test_exact_match_lowercase(self, db_session):
        """Test exact match with lowercase alias"""
        result = map_test_name_to_type(db_session, "wbc")
        assert result is not None
        assert result.key == "WBC"
        assert result.display_name == "White Blood Cells"
    
    def test_exact_match_uppercase(self, db_session):
        """Test exact match with uppercase input (should be normalized)"""
        result = map_test_name_to_type(db_session, "WBC")
        assert result is not None
        assert result.key == "WBC"
    
    def test_exact_match_mixed_case(self, db_session):
        """Test exact match with mixed case input"""
        result = map_test_name_to_type(db_session, "Wbc")
        assert result is not None
        assert result.key == "WBC"
    
    def test_multi_word_alias(self, db_session):
        """Test matching multi-word alias"""
        result = map_test_name_to_type(db_session, "white blood cells")
        assert result is not None
        assert result.key == "WBC"
    
    def test_multi_word_alias_mixed_case(self, db_session):
        """Test matching multi-word alias with mixed case"""
        result = map_test_name_to_type(db_session, "White Blood Cells")
        assert result is not None
        assert result.key == "WBC"
    
    def test_alias_with_whitespace(self, db_session):
        """Test that leading/trailing whitespace is handled"""
        result = map_test_name_to_type(db_session, "  wbc  ")
        assert result is not None
        assert result.key == "WBC"
    
    def test_unknown_test_name(self, db_session):
        """Test that unknown test names return None"""
        result = map_test_name_to_type(db_session, "unknown_test")
        assert result is None
    
    def test_empty_string(self, db_session):
        """Test that empty string returns None"""
        result = map_test_name_to_type(db_session, "")
        assert result is None
    
    def test_whitespace_only(self, db_session):
        """Test that whitespace-only string returns None"""
        result = map_test_name_to_type(db_session, "   ")
        assert result is None
    
    def test_multiple_aliases_same_test(self, db_session):
        """Test that multiple aliases map to the same TestType"""
        result1 = map_test_name_to_type(db_session, "glucose")
        result2 = map_test_name_to_type(db_session, "glu")
        result3 = map_test_name_to_type(db_session, "blood glucose")
        result4 = map_test_name_to_type(db_session, "blood sugar")
        
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
        assert result4 is not None
        
        # All should map to the same TestType
        assert result1.key == result2.key == result3.key == result4.key == "GLUCOSE"
        assert result1.id == result2.id == result3.id == result4.id
    
    def test_returns_test_type_with_panel(self, db_session):
        """Test that returned TestType includes panel relationship"""
        result = map_test_name_to_type(db_session, "wbc")
        assert result is not None
        assert result.panel is not None
        assert result.panel.key == "CBC"
        assert result.panel.display_name == "Complete Blood Count"
    
    def test_returns_test_type_with_reference_ranges(self, db_session):
        """Test that returned TestType includes reference ranges"""
        result = map_test_name_to_type(db_session, "glucose")
        assert result is not None
        assert result.ref_low == 70.0
        assert result.ref_high == 100.0
    
    def test_lipid_panel_test(self, db_session):
        """Test mapping for Lipid Panel test"""
        result = map_test_name_to_type(db_session, "ldl cholesterol")
        assert result is not None
        assert result.key == "LDL"
        assert result.panel.key == "LIPID"
    
    def test_case_insensitive_lookup(self, db_session):
        """Test that lookup is truly case-insensitive"""
        test_cases = [
            "LEUKOCYTES",
            "Leukocytes",
            "leukocytes",
            "LeUkOcYtEs",
        ]
        
        for test_case in test_cases:
            result = map_test_name_to_type(db_session, test_case)
            assert result is not None, f"Failed for: {test_case}"
            assert result.key == "WBC", f"Wrong key for: {test_case}"
