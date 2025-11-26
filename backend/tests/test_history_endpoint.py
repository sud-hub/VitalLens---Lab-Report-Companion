"""
Tests for test history endpoint.

Requirements tested:
- 11.1: Return all TestResult records for user and test type ordered by timestamp
- 11.2: Include timestamp, value, unit, and status for each result
- 11.3: Return empty data array if user has no results
- 11.4: Return 404 for non-existent test key
- 11.5: Include panel key, test key, display name, and unit metadata
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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_history.db"
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
        
        db.add(cbc_panel)
        db.add(metabolic_panel)
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
        
        db.add(wbc)
        db.add(glucose)
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
        
        db.add(report1)
        db.add(report2)
        db.add(report3)
        db.commit()
        
        # Create test results with different timestamps
        base_time = datetime.now()
        
        result1 = TestResult(
            report_id=report1.id,
            test_type_id=wbc.id,
            value=5.5,
            unit="10^3/µL",
            status="NORMAL",
            created_at=base_time - timedelta(days=30)
        )
        result2 = TestResult(
            report_id=report2.id,
            test_type_id=wbc.id,
            value=6.2,
            unit="10^3/µL",
            status="NORMAL",
            created_at=base_time - timedelta(days=15)
        )
        result3 = TestResult(
            report_id=report3.id,
            test_type_id=wbc.id,
            value=7.8,
            unit="10^3/µL",
            status="NORMAL",
            created_at=base_time
        )
        
        db.add(result1)
        db.add(result2)
        db.add(result3)
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


class TestHistoryEndpoint:
    """Tests for GET /tests/{test_key}/history endpoint"""
    
    def test_get_history_success(self):
        """
        Test successful retrieval of test history.
        Requirements: 11.1, 11.2, 11.5
        """
        response = client.get("/tests/WBC/history", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        # Check metadata structure
        assert "metadata" in data
        assert "data" in data
        
        metadata = data["metadata"]
        assert metadata["panel_key"] == "CBC"
        assert metadata["test_key"] == "WBC"
        assert metadata["display_name"] == "White Blood Cells"
        assert metadata["unit"] == "10^3/µL"
        assert metadata["ref_low"] == 4.5
        assert metadata["ref_high"] == 11.0
        
        # Check data points
        history = data["data"]
        assert len(history) == 3
        
        # Check chronological order (oldest to newest)
        assert history[0]["value"] == 5.5
        assert history[1]["value"] == 6.2
        assert history[2]["value"] == 7.8
        
        # Check each data point has required fields
        for point in history:
            assert "timestamp" in point
            assert "value" in point
            assert "unit" in point
            assert "status" in point
            assert point["unit"] == "10^3/µL"
            assert point["status"] == "NORMAL"
    
    def test_get_history_empty(self):
        """
        Test empty history for test with no results.
        Requirements: 11.3
        """
        response = client.get("/tests/GLUCOSE/history", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have metadata but empty data array
        assert "metadata" in data
        assert "data" in data
        assert len(data["data"]) == 0
        assert data["data"] == []
        
        # Metadata should still be present
        metadata = data["metadata"]
        assert metadata["test_key"] == "GLUCOSE"
        assert metadata["display_name"] == "Glucose"
    
    def test_get_history_nonexistent_test(self):
        """
        Test 404 response for non-existent test key.
        Requirements: 11.4
        """
        response = client.get("/tests/INVALID/history", headers=get_auth_headers())
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_history_requires_authentication(self):
        """
        Test that history endpoint requires authentication.
        """
        response = client.get("/tests/WBC/history")
        assert response.status_code == 401
    
    def test_get_history_chronological_order(self):
        """
        Test that history is returned in chronological order.
        Requirements: 11.1
        """
        response = client.get("/tests/WBC/history", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        history = data["data"]
        
        # Extract timestamps and verify they're in ascending order
        timestamps = [point["timestamp"] for point in history]
        
        # Convert to datetime objects for comparison
        dt_timestamps = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
        
        # Check that each timestamp is >= the previous one
        for i in range(1, len(dt_timestamps)):
            assert dt_timestamps[i] >= dt_timestamps[i-1], (
                f"Timestamps not in chronological order: "
                f"{dt_timestamps[i-1]} should be <= {dt_timestamps[i]}"
            )
    
    def test_get_history_includes_all_metadata(self):
        """
        Test that response includes all required metadata fields.
        Requirements: 11.5
        """
        response = client.get("/tests/WBC/history", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        metadata = data["metadata"]
        
        # Check all required metadata fields
        required_fields = ["panel_key", "test_key", "display_name", "unit"]
        for field in required_fields:
            assert field in metadata, f"Missing required metadata field: {field}"
            assert metadata[field] is not None, f"Metadata field {field} is None"
            assert len(str(metadata[field])) > 0, f"Metadata field {field} is empty"
        
        # Reference ranges should be present (can be None for some tests)
        assert "ref_low" in metadata
        assert "ref_high" in metadata
