"""
Tests for ML API
"""
import pytest
from fastapi.testclient import TestClient
from main import app, prediction_history, models

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_history():
    """Reset prediction history before each test"""
    prediction_history.clear()
    yield

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "ML Inference API"
    assert "version" in data

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"] > 0
    assert data["uptime_seconds"] >= 0

def test_list_models():
    """Test listing available models"""
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] in ["default", "model_v2"]
    assert data[0]["loaded"] is True

def test_predict_success():
    """Test successful prediction"""
    response = client.post("/predict", json={
        "features": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "model_name": "default"
    })
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert isinstance(data["prediction"], float)
    assert data["model_name"] == "default"
    assert data["inference_time_ms"] > 0
    assert "timestamp" in data
    assert "request_id" in data

def test_predict_wrong_feature_count():
    """Test prediction with wrong number of features"""
    response = client.post("/predict", json={
        "features": [1.0, 2.0, 3.0],  # Too few features
        "model_name": "default"
    })
    assert response.status_code == 400
    assert "Expected" in response.json()["detail"]

def test_predict_model_not_found():
    """Test prediction with non-existent model"""
    response = client.post("/predict", json={
        "features": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "model_name": "nonexistent_model"
    })
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_batch_predict():
    """Test batch prediction"""
    batch_data = [
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0],
        [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]
    ]
    
    response = client.post("/predict/batch", json={
        "batch": batch_data,
        "model_name": "default"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["predictions"]) == len(batch_data)
    assert data["batch_size"] == 3
    assert data["total_inference_time_ms"] > 0

def test_prediction_history():
    """Test prediction history endpoint"""
    # Make a prediction first
    client.post("/predict", json={
        "features": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "model_name": "default"
    })
    
    # Wait a bit for background task
    import time
    time.sleep(0.2)
    
    # Get history
    response = client.get("/predictions/history?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert data["total"] >= 0

def test_prediction_stats():
    """Test prediction statistics endpoint"""
    # Make several predictions
    for i in range(3):
        client.post("/predict", json={
            "features": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "model_name": "default"
        })
    
    # Wait for background tasks
    import time
    time.sleep(0.3)
    
    # Get stats
    response = client.get("/predictions/stats")
    assert response.status_code == 200
    data = response.json()
    
    if data["total_predictions"] > 0:
        assert "avg_inference_time_ms" in data
        assert "predictions_by_model" in data

def test_multiple_models():
    """Test using different models"""
    # Test default model
    response1 = client.post("/predict", json={
        "features": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "model_name": "default"
    })
    assert response1.status_code == 200
    
    # Test model_v2
    response2 = client.post("/predict", json={
        "features": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "model_name": "model_v2"
    })
    assert response2.status_code == 200
    
    # Predictions should be different (different models)
    assert response1.json()["prediction"] != response2.json()["prediction"]

@pytest.mark.asyncio
async def test_concurrent_predictions():
    """Test concurrent predictions"""
    import asyncio
    from httpx import AsyncClient
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Make 10 concurrent requests
        tasks = [
            ac.post("/predict", json={
                "features": [float(i)] * 10,
                "model_name": "default"
            })
            for i in range(10)
        ]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
