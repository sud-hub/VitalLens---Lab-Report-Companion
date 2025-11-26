"""
Tests for the main FastAPI application setup.

This module tests the application initialization, middleware, and error handlers.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns correct information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["version"] == "1.0.0"


def test_health_check_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_cors_headers():
    """Test that CORS headers are properly configured."""
    response = client.options("/", headers={"Origin": "http://localhost:3000"})
    # CORS middleware should add appropriate headers
    assert "access-control-allow-origin" in response.headers


def test_openapi_docs_available():
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "Lab Report Companion API"


def test_all_routers_registered():
    """Test that all required routers are registered."""
    response = client.get("/openapi.json")
    data = response.json()
    paths = data["paths"]
    
    # Check auth endpoints
    assert "/auth/register" in paths
    assert "/auth/login" in paths
    
    # Check user endpoints
    assert "/users/me" in paths
    
    # Check report endpoints
    assert "/reports/upload" in paths
    
    # Check test endpoints
    assert "/panels" in paths
    assert "/panels/{panel_key}/tests" in paths
    assert "/tests/{test_key}/history" in paths
    assert "/tests/{test_key}/latest-insight" in paths


def test_validation_error_handler():
    """Test that validation errors are handled properly."""
    # Try to register with invalid data (missing required fields)
    response = client.post("/auth/register", json={})
    assert response.status_code == 422  # FastAPI returns 422 for validation errors
    data = response.json()
    assert "detail" in data


def test_404_for_nonexistent_endpoint():
    """Test that non-existent endpoints return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
