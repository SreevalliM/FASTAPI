"""
ML API with Async Inference and Background Logging
===================================================
"""
import asyncio
import time
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path
import pickle
import numpy as np

from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="ML Inference API",
    description="Production ML API with async inference and background logging",
    version="1.0.0"
)

# In-memory prediction history
prediction_history = []

# Models
class PredictionInput(BaseModel):
    """Input data for prediction"""
    features: List[float] = Field(..., description="Input features for the model")
    model_name: str = Field(default="default", description="Name of the model to use")

class PredictionOutput(BaseModel):
    """Output from prediction"""
    prediction: float
    model_name: str
    inference_time_ms: float
    timestamp: str
    request_id: str

class BatchPredictionInput(BaseModel):
    """Batch prediction input"""
    batch: List[List[float]] = Field(..., description="Batch of feature vectors")
    model_name: str = Field(default="default", description="Name of the model to use")

class BatchPredictionOutput(BaseModel):
    """Batch prediction output"""
    predictions: List[float]
    model_name: str
    batch_size: int
    total_inference_time_ms: float
    timestamp: str

class ModelInfo(BaseModel):
    """Model information"""
    name: str
    type: str
    loaded: bool
    feature_count: Optional[int] = None

class HealthStatus(BaseModel):
    """Health check status"""
    status: str
    models_loaded: int
    uptime_seconds: float
    total_predictions: int

# Simple ML Model (In production, load real trained models)
class SimpleLinearModel:
    """Simple linear regression model for demonstration"""
    def __init__(self, name: str = "default"):
        self.name = name
        self.weights = np.random.randn(10)  # 10 features
        self.bias = np.random.randn()
        self.feature_count = 10
        logger.info(f"Initialized model: {name}")
    
    async def predict(self, features: List[float]) -> float:
        """Async prediction method"""
        # Simulate some computation time
        await asyncio.sleep(0.01)  # 10ms delay
        
        if len(features) != self.feature_count:
            raise ValueError(f"Expected {self.feature_count} features, got {len(features)}")
        
        # Simple linear prediction
        features_array = np.array(features)
        prediction = np.dot(self.weights, features_array) + self.bias
        
        return float(prediction)
    
    async def predict_batch(self, batch: List[List[float]]) -> List[float]:
        """Batch prediction with parallel processing"""
        # Process predictions in parallel
        tasks = [self.predict(features) for features in batch]
        predictions = await asyncio.gather(*tasks)
        return predictions
    
    def save(self, path: str):
        """Save model to disk"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'weights': self.weights,
                'bias': self.bias,
                'feature_count': self.feature_count
            }, f)
        logger.info(f"Model {self.name} saved to {path}")
    
    @classmethod
    def load(cls, path: str, name: str = "default"):
        """Load model from disk"""
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            model = cls(name=name)
            model.weights = data['weights']
            model.bias = data['bias']
            model.feature_count = data['feature_count']
            logger.info(f"Model {name} loaded from {path}")
            return model
        except FileNotFoundError:
            logger.warning(f"Model file not found at {path}, creating new model")
            return cls(name=name)

# Model registry
models = {}
start_time = time.time()

# Background logging functions
async def log_prediction_async(
    request_id: str,
    model_name: str,
    features: List[float],
    prediction: float,
    inference_time: float
):
    """Async background logging of predictions"""
    log_entry = {
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "model_name": model_name,
        "feature_count": len(features),
        "prediction": prediction,
        "inference_time_ms": inference_time
    }
    
    # Store in history
    prediction_history.append(log_entry)
    
    # Keep only last 1000 predictions in memory
    if len(prediction_history) > 1000:
        prediction_history.pop(0)
    
    # Log to file
    logger.info(f"Prediction logged: {log_entry}")
    
    # Simulate writing to external system (database, cloud storage, etc.)
    await asyncio.sleep(0.05)  # Simulate I/O operation

def log_prediction_sync(
    request_id: str,
    model_name: str,
    features: List[float],
    prediction: float,
    inference_time: float
):
    """Sync version for background tasks"""
    log_entry = {
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "model_name": model_name,
        "feature_count": len(features),
        "prediction": prediction,
        "inference_time_ms": inference_time
    }
    
    prediction_history.append(log_entry)
    
    if len(prediction_history) > 1000:
        prediction_history.pop(0)
    
    logger.info(f"Prediction logged (sync): {log_entry}")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    logger.info("Starting ML API...")
    
    # Load or create default model
    models["default"] = SimpleLinearModel.load("models/default.pkl", name="default")
    
    # Load additional models
    models["model_v2"] = SimpleLinearModel(name="model_v2")
    
    logger.info(f"Loaded {len(models)} models")

@app.on_event("shutdown")
async def shutdown_event():
    """Save models on shutdown"""
    logger.info("Shutting down ML API...")
    
    for name, model in models.items():
        model.save(f"models/{name}.pkl")
    
    logger.info("All models saved")

# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "ML Inference API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthStatus, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - start_time
    return HealthStatus(
        status="healthy",
        models_loaded=len(models),
        uptime_seconds=uptime,
        total_predictions=len(prediction_history)
    )

@app.get("/models", response_model=List[ModelInfo], tags=["Models"])
async def list_models():
    """List all loaded models"""
    return [
        ModelInfo(
            name=name,
            type="LinearRegression",
            loaded=True,
            feature_count=model.feature_count
        )
        for name, model in models.items()
    ]

@app.post("/predict", response_model=PredictionOutput, tags=["Inference"])
async def predict(
    input_data: PredictionInput,
    background_tasks: BackgroundTasks
):
    """
    Make a prediction with background logging
    
    - **features**: List of numerical features
    - **model_name**: Name of the model to use (default: "default")
    """
    # Validate model exists
    if input_data.model_name not in models:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{input_data.model_name}' not found"
        )
    
    model = models[input_data.model_name]
    request_id = f"req_{int(time.time()*1000)}"
    
    # Measure inference time
    start = time.time()
    try:
        prediction = await model.predict(input_data.features)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    inference_time = (time.time() - start) * 1000  # Convert to ms
    
    # Add background logging task
    background_tasks.add_task(
        log_prediction_sync,
        request_id=request_id,
        model_name=input_data.model_name,
        features=input_data.features,
        prediction=prediction,
        inference_time=inference_time
    )
    
    return PredictionOutput(
        prediction=prediction,
        model_name=input_data.model_name,
        inference_time_ms=inference_time,
        timestamp=datetime.utcnow().isoformat(),
        request_id=request_id
    )

@app.post("/predict/batch", response_model=BatchPredictionOutput, tags=["Inference"])
async def predict_batch(
    input_data: BatchPredictionInput,
    background_tasks: BackgroundTasks
):
    """
    Make batch predictions with async processing
    
    - **batch**: List of feature vectors
    - **model_name**: Name of the model to use
    """
    if input_data.model_name not in models:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{input_data.model_name}' not found"
        )
    
    model = models[input_data.model_name]
    
    # Measure inference time
    start = time.time()
    try:
        predictions = await model.predict_batch(input_data.batch)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    inference_time = (time.time() - start) * 1000
    
    # Log batch prediction in background
    background_tasks.add_task(
        logger.info,
        f"Batch prediction: {len(input_data.batch)} samples, "
        f"model={input_data.model_name}, time={inference_time:.2f}ms"
    )
    
    return BatchPredictionOutput(
        predictions=predictions,
        model_name=input_data.model_name,
        batch_size=len(input_data.batch),
        total_inference_time_ms=inference_time,
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/predictions/history", tags=["Logging"])
async def get_prediction_history(limit: int = 10):
    """
    Get recent prediction history
    
    - **limit**: Number of recent predictions to return (max 100)
    """
    limit = min(limit, 100)
    return {
        "total": len(prediction_history),
        "limit": limit,
        "predictions": prediction_history[-limit:]
    }

@app.get("/predictions/stats", tags=["Logging"])
async def get_prediction_stats():
    """Get prediction statistics"""
    if not prediction_history:
        return {
            "total_predictions": 0,
            "message": "No predictions yet"
        }
    
    # Calculate statistics
    inference_times = [p["inference_time_ms"] for p in prediction_history]
    model_counts = {}
    
    for pred in prediction_history:
        model_name = pred["model_name"]
        model_counts[model_name] = model_counts.get(model_name, 0) + 1
    
    return {
        "total_predictions": len(prediction_history),
        "avg_inference_time_ms": sum(inference_times) / len(inference_times),
        "min_inference_time_ms": min(inference_times),
        "max_inference_time_ms": max(inference_times),
        "predictions_by_model": model_counts
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
