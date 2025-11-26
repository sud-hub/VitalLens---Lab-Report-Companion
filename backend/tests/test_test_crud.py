"""
Tests for test result CRUD operations.

Validates: Requirements 8.1, 8.2, 11.1, 12.1, 12.2
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.db.base import Base
from app.db.models import User, Panel, TestType, Report, TestResult
from app.crud.tests import (
    create_test_result,
    get_test_history,
    get_latest_test_result,
    get_previous_test_result,
    get_test_type_by_key
)


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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
def setup_test_data(db):
    """Set up test data: user, panel, test type, and report"""
    # Create user
    user = User(
        email="test@example.com",
        hashed_password="hashed_password"
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


class TestCreateTestResult:
    """Tests for create_test_result function"""
    
    def test_create_test_result_success(self, db, setup_test_data):
        """Test creating a test result successfully"""
        data = setup_test_data
        
        result = create_test_result(
            db=db,
            report_id=data["report"].id,
            test_type_id=data["test_type"].id,
            value=7.5,
            unit="10^3/µL",
            status="NORMAL",
            confidence=0.95
        )
        
        assert result.id is not None
        assert result.report_id == data["report"].id
        assert result.test_type_id == data["test_type"].id
        assert result.value == 7.5
        assert result.unit == "10^3/µL"
        assert result.status == "NORMAL"
        assert result.confidence == 0.95
        assert result.created_at is not None
    
    def test_create_test_result_without_confidence(self, db, setup_test_data):
        """Test creating a test result without confidence score"""
        data = setup_test_data
        
        result = create_test_result(
            db=db,
            report_id=data["report"].id,
            test_type_id=data["test_type"].id,
            value=12.0,
            unit="10^3/µL",
            status="HIGH"
        )
        
        assert result.id is not None
        assert result.value == 12.0
        assert result.status == "HIGH"
        assert result.confidence is None


class TestGetTestHistory:
    """Tests for get_test_history function"""
    
    def test_get_test_history_empty(self, db, setup_test_data):
        """Test getting history when no results exist"""
        data = setup_test_data
        
        history = get_test_history(
            db=db,
            user_id=data["user"].id,
            test_key="WBC"
        )
        
        assert history == []
    
    def test_get_test_history_single_result(self, db, setup_test_data):
        """Test getting history with one result"""
        data = setup_test_data
        
        # Create a test result
        create_test_result(
            db=db,
            report_id=data["report"].id,
            test_type_id=data["test_type"].id,
            value=7.5,
            unit="10^3/µL",
            status="NORMAL"
        )
        
        history = get_test_history(
            db=db,
            user_id=data["user"].id,
            test_key="WBC"
        )
        
        assert len(history) == 1
        assert history[0].value == 7.5
        assert history[0].status == "NORMAL"
    
    def test_get_test_history_chronological_order(self, db, setup_test_data):
        """Test that history is returned in chronological order (oldest to newest)"""
        data = setup_test_data
        
        # Create multiple reports and test results
        for i, value in enumerate([7.5, 8.0, 6.5]):
            report = Report(
                user_id=data["user"].id,
                original_filename=f"report_{i}.pdf",
                parsed_success=True
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            
            create_test_result(
                db=db,
                report_id=report.id,
                test_type_id=data["test_type"].id,
                value=value,
                unit="10^3/µL",
                status="NORMAL"
            )
        
        history = get_test_history(
            db=db,
            user_id=data["user"].id,
            test_key="WBC"
        )
        
        assert len(history) == 3
        assert history[0].value == 7.5
        assert history[1].value == 8.0
        assert history[2].value == 6.5
    
    def test_get_test_history_filters_by_user(self, db, setup_test_data):
        """Test that history only returns results for the specified user"""
        data = setup_test_data
        
        # Create another user
        other_user = User(
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        
        # Create report for other user
        other_report = Report(
            user_id=other_user.id,
            original_filename="other_report.pdf",
            parsed_success=True
        )
        db.add(other_report)
        db.commit()
        db.refresh(other_report)
        
        # Create test results for both users
        create_test_result(
            db=db,
            report_id=data["report"].id,
            test_type_id=data["test_type"].id,
            value=7.5,
            unit="10^3/µL",
            status="NORMAL"
        )
        
        create_test_result(
            db=db,
            report_id=other_report.id,
            test_type_id=data["test_type"].id,
            value=9.0,
            unit="10^3/µL",
            status="NORMAL"
        )
        
        # Get history for first user
        history = get_test_history(
            db=db,
            user_id=data["user"].id,
            test_key="WBC"
        )
        
        assert len(history) == 1
        assert history[0].value == 7.5


class TestGetLatestTestResult:
    """Tests for get_latest_test_result function"""
    
    def test_get_latest_test_result_none(self, db, setup_test_data):
        """Test getting latest result when none exist"""
        data = setup_test_data
        
        result = get_latest_test_result(
            db=db,
            user_id=data["user"].id,
            test_key="WBC"
        )
        
        assert result is None
    
    def test_get_latest_test_result_single(self, db, setup_test_data):
        """Test getting latest result with one result"""
        data = setup_test_data
        
        create_test_result(
            db=db,
            report_id=data["report"].id,
            test_type_id=data["test_type"].id,
            value=7.5,
            unit="10^3/µL",
            status="NORMAL"
        )
        
        result = get_latest_test_result(
            db=db,
            user_id=data["user"].id,
            test_key="WBC"
        )
        
        assert result is not None
        assert result.value == 7.5
    
    def test_get_latest_test_result_multiple(self, db, setup_test_data):
        """Test getting latest result returns most recent"""
        data = setup_test_data
        
        # Create multiple results
        values = [7.5, 8.0, 6.5]
        for i, value in enumerate(values):
            report = Report(
                user_id=data["user"].id,
                original_filename=f"report_{i}.pdf",
                parsed_success=True
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            
            create_test_result(
                db=db,
                report_id=report.id,
                test_type_id=data["test_type"].id,
                value=value,
                unit="10^3/µL",
                status="NORMAL"
            )
        
        result = get_latest_test_result(
            db=db,
            user_id=data["user"].id,
            test_key="WBC"
        )
        
        assert result is not None
        # The latest result should be one of the created values
        assert result.value in values


class TestGetPreviousTestResult:
    """Tests for get_previous_test_result function"""
    
    def test_get_previous_test_result_none(self, db, setup_test_data):
        """Test getting previous result when none exist"""
        data = setup_test_data
        
        result = get_previous_test_result(
            db=db,
            user_id=data["user"].id,
            test_key="WBC",
            before_timestamp=datetime.now()
        )
        
        assert result is None
    
    def test_get_previous_test_result_before_latest(self, db, setup_test_data):
        """Test getting previous result before the latest"""
        data = setup_test_data
        
        # Create two results
        first_result = create_test_result(
            db=db,
            report_id=data["report"].id,
            test_type_id=data["test_type"].id,
            value=7.5,
            unit="10^3/µL",
            status="NORMAL"
        )
        
        # Create second report
        report2 = Report(
            user_id=data["user"].id,
            original_filename="report2.pdf",
            parsed_success=True
        )
        db.add(report2)
        db.commit()
        db.refresh(report2)
        
        second_result = create_test_result(
            db=db,
            report_id=report2.id,
            test_type_id=data["test_type"].id,
            value=8.0,
            unit="10^3/µL",
            status="NORMAL"
        )
        
        # Get previous result before second result
        previous = get_previous_test_result(
            db=db,
            user_id=data["user"].id,
            test_key="WBC",
            before_timestamp=second_result.created_at
        )
        
        assert previous is not None
        assert previous.value == 7.5


class TestGetTestTypeByKey:
    """Tests for get_test_type_by_key function"""
    
    def test_get_test_type_by_key_exists(self, db, setup_test_data):
        """Test getting test type that exists"""
        data = setup_test_data
        
        test_type = get_test_type_by_key(db=db, test_key="WBC")
        
        assert test_type is not None
        assert test_type.key == "WBC"
        assert test_type.display_name == "White Blood Cell Count"
        assert test_type.unit == "10^3/µL"
    
    def test_get_test_type_by_key_not_exists(self, db, setup_test_data):
        """Test getting test type that doesn't exist"""
        test_type = get_test_type_by_key(db=db, test_key="NONEXISTENT")
        
        assert test_type is None
