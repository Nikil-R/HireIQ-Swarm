import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_api_startup():
    """Verify the API can initialize without errors."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_execute_invalid_payload():
    """Ensure the API rejects malformed execute requests."""
    response = client.post("/execute", json={})
    assert response.status_code == 422 # Unprocessable Entity

def test_execute_and_poll_status():
    """Verify a task can be created and checked."""
    # Start a dummy task
    response = client.post("/execute", json={"goal": "Test Research"})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    
    # Check status
    task_id = data["task_id"]
    status_response = client.get(f"/status/{task_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["task_id"] == task_id
    assert status_data["status"] in ["running", "completed", "failed"]
