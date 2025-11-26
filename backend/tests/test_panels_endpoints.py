"""
Tests for panels and tests endpoints.

Requirements tested:
- 9.1, 9.2, 9.3, 9.5: GET /panels endpoint
- 10.1, 10.2, 10.3, 10.4, 10.5: GET /panels/{panel_key}/tests endpoint
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hypothesis import given, strategies as st, settings

from app.main import app
from app.db.base import Base
from app.core.dependencies import get_db
from app.db.models import User, Panel, TestType
from app.core.security import get_password_hash, create_access_token


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_panels.db"
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
    """Create tables and seed data before each test"""
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
        
        # Create test types for CBC
        wbc = TestType(
            panel_id=cbc_panel.id,
            key="WBC",
            display_name="White Blood Cells",
            unit="10^3/µL",
            ref_low=4.5,
            ref_high=11.0
        )
        rbc = TestType(
            panel_id=cbc_panel.id,
            key="RBC",
            display_name="Red Blood Cells",
            unit="10^6/µL",
            ref_low=4.5,
            ref_high=5.9
        )
        
        db.add(wbc)
        db.add(rbc)
        
        # Create test types for Metabolic
        glucose = TestType(
            panel_id=metabolic_panel.id,
            key="GLUCOSE",
            display_name="Glucose",
            unit="mg/dL",
            ref_low=70.0,
            ref_high=100.0
        )
        
        db.add(glucose)
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


class TestPanelsEndpoint:
    """Tests for GET /panels endpoint"""
    
    def test_get_panels_success(self):
        """
        Test successful retrieval of all panels.
        Requirements: 9.1, 9.2, 9.5
        """
        response = client.get("/panels", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return all three panels
        assert len(data) == 3
        
        # Check panel structure
        panel_keys = [p["key"] for p in data]
        assert "CBC" in panel_keys
        assert "METABOLIC" in panel_keys
        assert "LIPID" in panel_keys
        
        # Check each panel has required fields
        for panel in data:
            assert "id" in panel
            assert "key" in panel
            assert "display_name" in panel
    
    def test_get_panels_requires_authentication(self):
        """
        Test that panels endpoint requires authentication.
        Requirements: 9.3
        """
        response = client.get("/panels")
        assert response.status_code == 401
    
    def test_get_panels_consistent_order(self):
        """
        Test that panels are returned in consistent order.
        Requirements: 9.5
        """
        response1 = client.get("/panels", headers=get_auth_headers())
        response2 = client.get("/panels", headers=get_auth_headers())
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Order should be consistent across calls
        assert [p["key"] for p in data1] == [p["key"] for p in data2]


class TestPanelTestsEndpoint:
    """Tests for GET /panels/{panel_key}/tests endpoint"""
    
    def test_get_panel_tests_success(self):
        """
        Test successful retrieval of tests for a panel.
        Requirements: 10.1, 10.2
        """
        response = client.get("/panels/CBC/tests", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        # CBC panel should have 2 tests (WBC, RBC)
        assert len(data) == 2
        
        # Check test structure
        for test in data:
            assert "id" in test
            assert "key" in test
            assert "display_name" in test
            assert "unit" in test
            assert "ref_low" in test
            assert "ref_high" in test
            assert "panel_id" in test
        
        # Check specific tests
        test_keys = [t["key"] for t in data]
        assert "WBC" in test_keys
        assert "RBC" in test_keys
    
    def test_get_panel_tests_case_insensitive(self):
        """
        Test that panel key lookup is case-insensitive.
        """
        response = client.get("/panels/cbc/tests", headers=get_auth_headers())
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
    
    def test_get_panel_tests_nonexistent_panel(self):
        """
        Test 404 response for non-existent panel.
        Requirements: 10.3
        """
        response = client.get("/panels/INVALID/tests", headers=get_auth_headers())
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_panel_tests_empty_panel(self):
        """
        Test empty list for panel with no tests.
        Requirements: 10.4
        """
        # LIPID panel has no tests in our seed data
        response = client.get("/panels/LIPID/tests", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        assert data == []
    
    def test_get_panel_tests_requires_authentication(self):
        """
        Test that panel tests endpoint requires authentication.
        Requirements: 10.5
        """
        response = client.get("/panels/CBC/tests")
        assert response.status_code == 401
    
    def test_get_panel_tests_includes_reference_ranges(self):
        """
        Test that test responses include reference ranges.
        Requirements: 10.2
        """
        response = client.get("/panels/CBC/tests", headers=get_auth_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        # Find WBC test
        wbc = next((t for t in data if t["key"] == "WBC"), None)
        assert wbc is not None
        
        # Check reference ranges
        assert wbc["ref_low"] == 4.5
        assert wbc["ref_high"] == 11.0
        assert wbc["unit"] == "10^3/µL"



class TestPanelPropertiesPropertyBased:
    """
    Property-based tests for panel endpoint properties.
    
    **Feature: lab-report-companion, Property 22: Panel endpoint returns complete data**
    **Feature: lab-report-companion, Property 23: Panel results are consistently ordered**
    """
    
    @settings(max_examples=100)
    @given(st.integers(min_value=1, max_value=100))
    def test_property_22_panel_endpoint_returns_complete_data(self, num_calls):
        """
        Property 22: Panel endpoint returns complete data
        
        For any panel returned by the /panels endpoint, the response should 
        include both the panel key and display name.
        
        **Validates: Requirements 9.2**
        """
        # Make the API call
        response = client.get("/panels", headers=get_auth_headers())
        
        assert response.status_code == 200
        panels = response.json()
        
        # Property: For any panel in the response, it must have key and display_name
        for panel in panels:
            assert "key" in panel, f"Panel missing 'key' field: {panel}"
            assert "display_name" in panel, f"Panel missing 'display_name' field: {panel}"
            
            # Both fields should be non-empty strings
            assert isinstance(panel["key"], str), f"Panel key is not a string: {panel['key']}"
            assert isinstance(panel["display_name"], str), f"Panel display_name is not a string: {panel['display_name']}"
            assert len(panel["key"]) > 0, f"Panel key is empty: {panel}"
            assert len(panel["display_name"]) > 0, f"Panel display_name is empty: {panel}"
            
            # Should also have id field
            assert "id" in panel, f"Panel missing 'id' field: {panel}"
            assert isinstance(panel["id"], int), f"Panel id is not an integer: {panel['id']}"
    
    @settings(max_examples=100)
    @given(st.integers(min_value=2, max_value=50))
    def test_property_23_panel_results_consistently_ordered(self, num_calls):
        """
        Property 23: Panel results are consistently ordered
        
        For any two consecutive calls to the /panels endpoint, the panels 
        should be returned in the same order.
        
        **Validates: Requirements 9.5**
        """
        # Make multiple calls and collect the ordering
        orderings = []
        
        for _ in range(min(num_calls, 10)):  # Cap at 10 to avoid excessive API calls
            response = client.get("/panels", headers=get_auth_headers())
            assert response.status_code == 200
            
            panels = response.json()
            # Extract the order as a tuple of panel keys
            order = tuple(panel["key"] for panel in panels)
            orderings.append(order)
        
        # Property: All orderings should be identical
        first_order = orderings[0]
        for i, order in enumerate(orderings[1:], start=1):
            assert order == first_order, (
                f"Panel ordering inconsistent between calls. "
                f"First call: {first_order}, Call {i+1}: {order}"
            )
        
        # Additional check: The order should be deterministic (same across test runs)
        # We verify this by checking that panels are ordered by their ID
        response = client.get("/panels", headers=get_auth_headers())
        panels = response.json()
        
        if len(panels) > 1:
            panel_ids = [panel["id"] for panel in panels]
            # Check if IDs are in ascending order (consistent with order_by(Panel.id))
            assert panel_ids == sorted(panel_ids), (
                f"Panels are not ordered by ID. Got: {panel_ids}, "
                f"Expected: {sorted(panel_ids)}"
            )
