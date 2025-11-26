"""
Tests for the latest insight endpoint.

Validates Requirements:
- 12.1: Return most recent TestResult for user and test type
- 12.2: Include previous result for comparison when available
- 12.3: Provide general educational message about the test result
- 12.4: Compute trend indicator (improving, worsening, stable)
- 12.5: Include prominent disclaimer stating information is not a medical diagnosis
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.main import app
from app.db.base import Base
from app.core.dependencies import get_db
from app.db.models import User, Panel, TestType, Report, TestResult
from app.core.security import get_password_hash, create_access_token


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_latest_insight.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create tables and seed data before tests"""
    # Set dependency override
    app.dependency_overrides[get_db] = override_get_db
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpassword123")
        )
        db.add(user)
        db.commit()
        
        # Create panels
        cbc_panel = Panel(key="CBC", display_name="Complete Blood Count")
        metabolic_panel = Panel(key="METABOLIC", display_name="Metabolic Panel")
        lipid_panel = Panel(key="LIPID", display_name="Lipid Panel")
        
        db.add(cbc_panel)
        db.add(metabolic_panel)
        db.add(lipid_panel)
        db.commit()
        
        # Create test types
        wbc = TestType(
            panel_id=cbc_panel.id,
            key="WBC",
            display_name="White Blood Cells",
            unit="10^3/µL",
            ref_low=4.5,
            ref_high=11.0
        )
        glucose = TestType(
            panel_id=metabolic_panel.id,
            key="GLUCOSE",
            display_name="Glucose",
            unit="mg/dL",
            ref_low=70.0,
            ref_high=100.0
        )
        ldl = TestType(
            panel_id=lipid_panel.id,
            key="LDL",
            display_name="LDL Cholesterol",
            unit="mg/dL",
            ref_low=0.0,
            ref_high=100.0
        )
        
        db.add(wbc)
        db.add(glucose)
        db.add(ldl)
        db.commit()
        
        # Create reports
        report1 = Report(
            user_id=user.id,
            original_filename="report1.pdf",
            parsed_success=True
        )
        report2 = Report(
            user_id=user.id,
            original_filename="report2.pdf",
            parsed_success=True
        )
        report3 = Report(
            user_id=user.id,
            original_filename="report3.pdf",
            parsed_success=True
        )
        report4 = Report(
            user_id=user.id,
            original_filename="report4.pdf",
            parsed_success=True
        )
        
        db.add(report1)
        db.add(report2)
        db.add(report3)
        db.add(report4)
        db.commit()
        
        # Create test results with different timestamps
        base_time = datetime.now()
        
        # WBC results - improving trend (moving toward normal)
        result1 = TestResult(
            report_id=report1.id,
            test_type_id=wbc.id,
            value=12.5,  # HIGH
            unit="10^3/µL",
            status="HIGH",
            created_at=base_time - timedelta(days=30)
        )
        result2 = TestResult(
            report_id=report2.id,
            test_type_id=wbc.id,
            value=8.0,  # NORMAL - improving
            unit="10^3/µL",
            status="NORMAL",
            created_at=base_time
        )
        
        # Glucose results - worsening trend
        result3 = TestResult(
            report_id=report3.id,
            test_type_id=glucose.id,
            value=85.0,  # NORMAL
            unit="mg/dL",
            status="NORMAL",
            created_at=base_time - timedelta(days=15)
        )
        result4 = TestResult(
            report_id=report4.id,
            test_type_id=glucose.id,
            value=110.0,  # HIGH - worsening
            unit="mg/dL",
            status="HIGH",
            created_at=base_time
        )
        
        # LDL result - only one result (no previous)
        result5 = TestResult(
            report_id=report1.id,
            test_type_id=ldl.id,
            value=95.0,  # NORMAL
            unit="mg/dL",
            status="NORMAL",
            created_at=base_time
        )
        
        db.add(result1)
        db.add(result2)
        db.add(result3)
        db.add(result4)
        db.add(result5)
        db.commit()
    finally:
        db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    # Remove dependency override
    app.dependency_overrides.pop(get_db, None)


def get_auth_headers():
    """Get authentication headers with valid JWT token"""
    token = create_access_token(data={"sub": "1"})
    return {"Authorization": f"Bearer {token}"}


class TestLatestInsightEndpoint:
    """Tests for GET /tests/{test_key}/latest-insight endpoint"""
    
    def test_get_latest_insight_with_previous(self):
        """
        Test successful retrieval of latest insight with previous result.
        Requirements: 12.1, 12.2, 12.3, 12.4, 12.5
        """
        response = client.get("/tests/WBC/latest-insight", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "latest" in data
        assert "previous" in data
        assert "guidance" in data
        
        # Requirement 12.1: Check latest result
        latest = data["latest"]
        assert latest["value"] == 8.0
        assert latest["unit"] == "10^3/µL"
        assert latest["status"] == "NORMAL"
        assert "timestamp" in latest
        
        # Requirement 12.2: Check previous result is included
        previous = data["previous"]
        assert previous is not None
        assert previous["value"] == 12.5
        assert previous["unit"] == "10^3/µL"
        assert previous["status"] == "HIGH"
        assert "timestamp" in previous
        
        # Requirement 12.3: Check educational message
        guidance = data["guidance"]
        assert "message" in guidance
        assert len(guidance["message"]) > 0
        assert "blood" in guidance["message"].lower() or "cell" in guidance["message"].lower()
        
        # Requirement 12.4: Check trend indicator
        assert "trend" in guidance
        assert guidance["trend"] in ["improving", "worsening", "stable"]
        
        # Requirement 12.5: Check disclaimer
        assert "disclaimer" in guidance
        assert len(guidance["disclaimer"]) > 0
        assert "not a medical diagnosis" in guidance["disclaimer"].lower()
        assert "doctor" in guidance["disclaimer"].lower()
        
        # Check suggestions
        assert "suggestions" in guidance
        assert isinstance(guidance["suggestions"], list)
        assert len(guidance["suggestions"]) > 0
    
    def test_get_latest_insight_without_previous(self):
        """
        Test latest insight when no previous result exists.
        Requirements: 12.1, 12.2
        """
        response = client.get("/tests/LDL/latest-insight", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        # Check latest result exists
        assert "latest" in data
        latest = data["latest"]
        assert latest["value"] == 95.0
        assert latest["status"] == "NORMAL"
        
        # Requirement 12.2: Previous should be None when no history
        assert "previous" in data
        assert data["previous"] is None
        
        # Guidance should still be present
        assert "guidance" in data
        guidance = data["guidance"]
        
        # Trend should be None when no previous result
        assert guidance["trend"] is None
        
        # Message and disclaimer should still be present
        assert len(guidance["message"]) > 0
        assert len(guidance["disclaimer"]) > 0
    
    def test_get_latest_insight_improving_trend(self):
        """
        Test that improving trend is correctly identified.
        Requirements: 12.4
        """
        response = client.get("/tests/WBC/latest-insight", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        # WBC went from 12.5 (HIGH) to 8.0 (NORMAL) - should be improving
        guidance = data["guidance"]
        assert guidance["trend"] == "improving"
    
    def test_get_latest_insight_worsening_trend(self):
        """
        Test that worsening trend is correctly identified.
        Requirements: 12.4
        """
        response = client.get("/tests/GLUCOSE/latest-insight", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        # Glucose went from 85.0 (NORMAL) to 110.0 (HIGH) - should be worsening
        guidance = data["guidance"]
        assert guidance["trend"] == "worsening"
    
    def test_get_latest_insight_nonexistent_test(self):
        """
        Test 404 response for non-existent test key.
        """
        response = client.get("/tests/INVALID/latest-insight", headers=get_auth_headers())
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_latest_insight_no_results(self):
        """
        Test 404 response when user has no results for the test.
        """
        # Create a new user with no test results
        db = TestingSessionLocal()
        try:
            user2 = User(
                email="user2@example.com",
                hashed_password=get_password_hash("password123")
            )
            db.add(user2)
            db.commit()
            
            # Get token for new user
            token = create_access_token(data={"sub": str(user2.id)})
            headers = {"Authorization": f"Bearer {token}"}
            
            response = client.get("/tests/WBC/latest-insight", headers=headers)
            
            assert response.status_code == 404
            assert "no test results" in response.json()["detail"].lower()
        finally:
            db.close()
    
    def test_get_latest_insight_requires_authentication(self):
        """
        Test that latest insight endpoint requires authentication.
        """
        response = client.get("/tests/WBC/latest-insight")
        assert response.status_code == 401
    
    def test_get_latest_insight_cbc_guidance(self):
        """
        Test that CBC tests receive appropriate guidance.
        Requirements: 12.3, 13.1
        """
        response = client.get("/tests/WBC/latest-insight", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        guidance = data["guidance"]
        message = guidance["message"].lower()
        
        # CBC guidance should mention blood cells
        assert "blood" in message or "cell" in message or "wbc" in message
    
    def test_get_latest_insight_metabolic_guidance(self):
        """
        Test that Metabolic Panel tests receive appropriate guidance.
        Requirements: 12.3, 13.2
        """
        response = client.get("/tests/GLUCOSE/latest-insight", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        guidance = data["guidance"]
        message = guidance["message"].lower()
        
        # Metabolic guidance should mention relevant organ function
        assert "glucose" in message or "sugar" in message or "blood" in message
    
    def test_get_latest_insight_lipid_guidance(self):
        """
        Test that Lipid Panel tests receive appropriate guidance.
        Requirements: 12.3, 13.3
        """
        response = client.get("/tests/LDL/latest-insight", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        guidance = data["guidance"]
        message = guidance["message"].lower()
        
        # Lipid guidance should mention heart health
        assert "cholesterol" in message or "heart" in message or "ldl" in message
    
    def test_get_latest_insight_disclaimer_always_present(self):
        """
        Test that disclaimer is always present in guidance.
        Requirements: 12.5, 13.4, 13.5
        """
        # Test multiple different tests
        test_keys = ["WBC", "GLUCOSE", "LDL"]
        
        for test_key in test_keys:
            response = client.get(f"/tests/{test_key}/latest-insight", headers=get_auth_headers())
            
            assert response.status_code == 200
            data = response.json()
            
            guidance = data["guidance"]
            disclaimer = guidance["disclaimer"].lower()
            
            # Requirement 13.4: Disclaimer states information is educational and not diagnostic
            assert "not a medical diagnosis" in disclaimer or "not a diagnosis" in disclaimer
            
            # Requirement 13.5: Disclaimer recommends consulting a doctor
            assert "doctor" in disclaimer or "physician" in disclaimer
            
            # Disclaimer should be substantial, not just a token message
            assert len(guidance["disclaimer"]) > 50
    
    def test_get_latest_insight_suggestions_present(self):
        """
        Test that suggestions are always provided.
        Requirements: 12.3
        """
        response = client.get("/tests/WBC/latest-insight", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        guidance = data["guidance"]
        suggestions = guidance["suggestions"]
        
        # Should have at least one suggestion
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
        # Each suggestion should be a non-empty string
        for suggestion in suggestions:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 0