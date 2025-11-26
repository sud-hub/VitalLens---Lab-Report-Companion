"""
Property-based tests for referential integrity.

Feature: lab-report-companion, Property 20: TestResult creation maintains referential integrity
Validates: Requirements 8.5
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from hypothesis import given, settings, strategies as st, assume, HealthCheck

from app.db.base import Base
from app.db.models import User, Panel, TestType, Report, TestResult
from app.crud.tests import create_test_result
from app.core.security import get_password_hash


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Enable foreign key constraints in SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def setup_base_data(db):
    """Set up base data: user, panel, test type, and report"""
    # Create user
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create panel
    panel = Panel(
        key="CBC",
        display_name="Complete Blood Count"
    )
    db.add(panel)
    db.commit()
    db.refresh(panel)
    
    # Create test type
    test_type = TestType(
        panel_id=panel.id,
        key="WBC",
        display_name="White Blood Cell Count",
        unit="10^3/µL",
        ref_low=4.5,
        ref_high=11.0
    )
    db.add(test_type)
    db.commit()
    db.refresh(test_type)
    
    # Create report
    report = Report(
        user_id=user.id,
        original_filename="test_report.pdf",
        parsed_success=True
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {
        "user": user,
        "panel": panel,
        "test_type": test_type,
        "report": report
    }


class TestReferentialIntegrityProperty:
    """Property-based tests for referential integrity."""
    
    # Feature: lab-report-companion, Property 20: TestResult creation maintains referential integrity
    @settings(
        max_examples=100, 
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        value=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False),
        status=st.sampled_from(["LOW", "NORMAL", "HIGH", "CRITICAL_LOW", "CRITICAL_HIGH", "UNKNOWN"]),
        confidence=st.one_of(
            st.none(),
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
        )
    )
    def test_test_result_maintains_referential_integrity(self, db, setup_base_data, value, status, confidence):
        """
        Property 20: TestResult creation maintains referential integrity
        
        For any TestResult, it should have valid foreign keys to both 
        Report and TestType tables.
        
        This property verifies that:
        1. TestResult can be created with valid foreign keys
        2. The foreign keys correctly reference existing records
        3. The relationships can be traversed (report and test_type)
        4. The referenced records can be accessed through the relationships
        
        Validates: Requirements 8.5
        """
        data = setup_base_data
        
        # Create a test result with the generated values
        test_result = create_test_result(
            db=db,
            report_id=data["report"].id,
            test_type_id=data["test_type"].id,
            value=value,
            unit="10^3/µL",
            status=status,
            confidence=confidence
        )
        
        # Property: TestResult should have valid foreign keys
        assert test_result.report_id is not None, \
            "TestResult should have a report_id"
        assert test_result.test_type_id is not None, \
            "TestResult should have a test_type_id"
        
        # Property: Foreign keys should reference existing records
        assert test_result.report_id == data["report"].id, \
            f"TestResult report_id should match the created report id"
        assert test_result.test_type_id == data["test_type"].id, \
            f"TestResult test_type_id should match the created test_type id"
        
        # Property: Relationships should be traversable
        assert test_result.report is not None, \
            "TestResult should have a valid report relationship"
        assert test_result.test_type is not None, \
            "TestResult should have a valid test_type relationship"
        
        # Property: Referenced records should be accessible through relationships
        assert test_result.report.id == data["report"].id, \
            "TestResult.report should reference the correct Report record"
        assert test_result.report.user_id == data["user"].id, \
            "TestResult.report should be linked to the correct user"
        assert test_result.report.original_filename == "test_report.pdf", \
            "TestResult.report should have the correct filename"
        
        assert test_result.test_type.id == data["test_type"].id, \
            "TestResult.test_type should reference the correct TestType record"
        assert test_result.test_type.key == "WBC", \
            "TestResult.test_type should have the correct key"
        assert test_result.test_type.panel_id == data["panel"].id, \
            "TestResult.test_type should be linked to the correct panel"
        
        # Property: The reverse relationships should also work
        # Report should have this test result in its test_results collection
        db.refresh(data["report"])
        assert test_result in data["report"].test_results, \
            "Report.test_results should include the created TestResult"
        
        # TestType should have this test result in its test_results collection
        db.refresh(data["test_type"])
        assert test_result in data["test_type"].test_results, \
            "TestType.test_results should include the created TestResult"
        
        # Property: The data should be persisted correctly
        # Query the database to verify the record exists
        queried_result = db.query(TestResult).filter(TestResult.id == test_result.id).first()
        assert queried_result is not None, \
            "TestResult should be persisted in the database"
        assert queried_result.report_id == data["report"].id, \
            "Persisted TestResult should have correct report_id"
        assert queried_result.test_type_id == data["test_type"].id, \
            "Persisted TestResult should have correct test_type_id"
    
    def test_multiple_test_results_maintain_referential_integrity(self, db, setup_base_data):
        """
        Property 20 (Extended): Multiple TestResults maintain referential integrity
        
        For any set of TestResults created for the same report, all should 
        maintain valid foreign keys and relationships.
        
        Validates: Requirements 8.5
        """
        data = setup_base_data
        
        # Create multiple test results with different values
        values = [7.5, 8.0, 6.5, 9.2, 5.8]
        created_results = []
        
        for value in values:
            test_result = create_test_result(
                db=db,
                report_id=data["report"].id,
                test_type_id=data["test_type"].id,
                value=value,
                unit="10^3/µL",
                status="NORMAL"
            )
            created_results.append(test_result)
        
        # Property: All test results should have valid foreign keys
        for result in created_results:
            assert result.report_id == data["report"].id, \
                "All TestResults should reference the same report"
            assert result.test_type_id == data["test_type"].id, \
                "All TestResults should reference the same test_type"
        
        # Property: All test results should be in the report's collection
        db.refresh(data["report"])
        report_result_ids = {r.id for r in data["report"].test_results}
        for result in created_results:
            assert result.id in report_result_ids, \
                f"TestResult {result.id} should be in Report.test_results"
        
        # Property: All test results should be in the test_type's collection
        db.refresh(data["test_type"])
        test_type_result_ids = {r.id for r in data["test_type"].test_results}
        for result in created_results:
            assert result.id in test_type_result_ids, \
                f"TestResult {result.id} should be in TestType.test_results"
        
        # Property: The count should match
        assert len(data["report"].test_results) == len(values), \
            f"Report should have exactly {len(values)} test results"
        assert len(data["test_type"].test_results) == len(values), \
            f"TestType should have exactly {len(values)} test results"
    
    def test_test_result_with_invalid_report_id_fails(self, db, setup_base_data):
        """
        Test that creating a TestResult with an invalid report_id fails.
        
        This verifies that the database enforces referential integrity constraints.
        """
        data = setup_base_data
        
        # Try to create a test result with a non-existent report_id
        from sqlalchemy.exc import IntegrityError
        
        with pytest.raises(IntegrityError):
            test_result = TestResult(
                report_id=99999,  # Non-existent report
                test_type_id=data["test_type"].id,
                value=7.5,
                unit="10^3/µL",
                status="NORMAL"
            )
            db.add(test_result)
            db.commit()
    
    def test_test_result_with_invalid_test_type_id_fails(self, db, setup_base_data):
        """
        Test that creating a TestResult with an invalid test_type_id fails.
        
        This verifies that the database enforces referential integrity constraints.
        """
        data = setup_base_data
        
        # Try to create a test result with a non-existent test_type_id
        from sqlalchemy.exc import IntegrityError
        
        with pytest.raises(IntegrityError):
            test_result = TestResult(
                report_id=data["report"].id,
                test_type_id=99999,  # Non-existent test type
                value=7.5,
                unit="10^3/µL",
                status="NORMAL"
            )
            db.add(test_result)
            db.commit()
    
    @settings(
        max_examples=50, 
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        value=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    def test_test_result_cascade_relationships(self, db, setup_base_data, value):
        """
        Property 20 (Extended): TestResult relationships are properly cascaded
        
        Verifies that the relationships between TestResult, Report, and TestType
        are properly maintained and can be traversed in both directions.
        
        Validates: Requirements 8.5
        """
        data = setup_base_data
        
        # Create a test result
        test_result = create_test_result(
            db=db,
            report_id=data["report"].id,
            test_type_id=data["test_type"].id,
            value=value,
            unit="10^3/µL",
            status="NORMAL"
        )
        
        # Property: Can traverse from TestResult to Report to User
        assert test_result.report.user.id == data["user"].id, \
            "Should be able to traverse TestResult -> Report -> User"
        assert test_result.report.user.email == "test@example.com", \
            "User data should be accessible through the relationship chain"
        
        # Property: Can traverse from TestResult to TestType to Panel
        assert test_result.test_type.panel.id == data["panel"].id, \
            "Should be able to traverse TestResult -> TestType -> Panel"
        assert test_result.test_type.panel.key == "CBC", \
            "Panel data should be accessible through the relationship chain"
        
        # Property: Can traverse from Report to User to all Reports
        user_reports = test_result.report.user.reports
        assert data["report"] in user_reports, \
            "Should be able to traverse back to all user reports"
        
        # Property: Can traverse from TestType to Panel to all TestTypes
        panel_test_types = test_result.test_type.panel.test_types
        assert data["test_type"] in panel_test_types, \
            "Should be able to traverse back to all panel test types"
