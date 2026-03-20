"""
Tests for the health check endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint_exists():
    """Test that the health check endpoint exists and returns 200."""
    response = client.get("/api/health/")
    assert response.status_code == 200


def test_health_check_response_format():
    """Test that the health check returns expected JSON format."""
    response = client.get("/api/health/")
    data = response.json()
    
    assert "status" in data
    assert "message" in data
    assert data["status"] == "healthy"
    assert data["message"] == "API is running"
