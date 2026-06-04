"""FastAPI server for model serving."""

import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from pydantic import BaseModel, Field

from src.features.engineering import FeatureEngineer
from src.utils.cache import get_cache_manager
from src.utils.config import get_config
from src.utils.logger import get_logger
from src.utils.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()
config = get_config()
cache = get_cache_manager()

# Initialize FastAPI app
app = FastAPI(
    title="Customer Churn Prediction API",
    description="Production ML API for predicting customer churn",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Pydantic models for request/response
class CustomerData(BaseModel):
    """Customer data for prediction."""

    customer_id: str = Field(..., description="Customer ID")
    age: int = Field(..., ge=18, le=100, description="Customer age")
    gender: str = Field(..., description="Gender (Male/Female/Other)")
    tenure: int = Field(..., ge=0, description="Tenure in months")
    monthly_charges: float = Field(..., ge=0, description="Monthly charges")
    total_charges: float = Field(..., ge=0, description="Total charges")
    contract_type: str = Field(..., description="Contract type")
    payment_method: str = Field(..., description="Payment method")
    internet_service: str = Field(..., description="Internet service type")
    online_security: str = Field(default="No", description="Online security")
    tech_support: str = Field(default="No", description="Tech support")

    class Config:
        schema_extra = {
            "example": {
                "customer_id": "CUST001",
                "age": 45,
                "gender": "Male",
                "tenure": 24,
                "monthly_charges": 75.50,
                "total_charges": 1812.00,
                "contract_type": "One year",
                "payment_method": "Credit card",
                "internet_service": "Fiber optic",
                "online_security": "Yes",
                "tech_support": "Yes",
            }
        }


class BatchPredictionRequest(BaseModel):
    """Batch prediction request."""

    customers: List[CustomerData]


class PredictionResponse(BaseModel):
    """Prediction response."""

    customer_id: str
    churn_probability: float
    churn_prediction: int
    risk_level: str
    timestamp: str


class BatchPredictionResponse(BaseModel):
    """Batch prediction response."""

    predictions: List[PredictionResponse]
    total_customers: int
    high_risk_count: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    model_loaded: bool
    version: str


# Global model and feature engineer
model = None
feature_engineer = None
model_version = None


def load_model(model_path: Optional[str] = None) -> None:
    """Load model from MLflow or disk.

    Args:
        model_path: Path to model file or MLflow URI
    """
    global model, feature_engineer, model_version

    try:
        if model_path and model_path.startswith("models:/"):
            # Load from MLflow Model Registry
            logger.info(f"Loading model from MLflow: {model_path}")
            model = mlflow.pyfunc.load_model(model_path)
            model_version = model_path.split("/")[-1]

        elif model_path:
            # Load from local file
            logger.info(f"Loading model from file: {model_path}")
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            model_version = "local"

        else:
            # Load default model
            default_path = Path("models") / "champion_model.pkl"
            if default_path.exists():
                logger.info(f"Loading default model: {default_path}")
                with open(default_path, "rb") as f:
                    model = pickle.load(f)
                model_version = "default"
            else:
                logger.warning("No model found, predictions will fail")

        # Load feature engineer
        artifacts_dir = Path("models") / "artifacts"
        if artifacts_dir.exists():
            feature_engineer = FeatureEngineer()
            feature_engineer.load_artifacts(str(artifacts_dir))
            logger.info("Loaded feature engineering artifacts")
        else:
            feature_engineer = FeatureEngineer()
            logger.warning("Feature engineering artifacts not found, using defaults")

        logger.info(f"Model loaded successfully (version={model_version})")

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("Starting Customer Churn Prediction API")

    # Load model
    try:
        load_model()
    except Exception as e:
        logger.error(f"Failed to load model on startup: {e}")

    logger.info("API startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Customer Churn Prediction API")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and track metrics."""
    start_time = datetime.now()

    response = await call_next(request)

    duration = (datetime.now() - start_time).total_seconds()

    # Log request
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s"
    )

    # Track metrics
    metrics.track_api_request(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
        duration=duration,
    )

    return response


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Customer Churn Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if model is not None else "degraded",
        timestamp=datetime.now().isoformat(),
        model_loaded=model is not None,
        version=model_version or "unknown",
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(customer: CustomerData):
    """Predict churn for single customer.

    Args:
        customer: Customer data

    Returns:
        Prediction response with churn probability and risk level
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start_time = datetime.now()

    try:
        # Check cache
        cache_key = f"prediction:{customer.customer_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for customer {customer.customer_id}")
            metrics.increment_cache_hits()
            return PredictionResponse(**cached_result)

        # Convert to DataFrame
        df = pd.DataFrame([customer.dict()])

        # Engineer features
        if feature_engineer:
            df = feature_engineer.engineer_features(df, fit=False)

        # Make prediction
        df_features = df.drop(columns=["customer_id", "churn"], errors="ignore")
        churn_proba = model.predict_proba(df_features)[0][1]
        churn_pred = int(churn_proba >= 0.5)

        # Determine risk level
        if churn_proba >= 0.7:
            risk_level = "high"
        elif churn_proba >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Create response
        response = PredictionResponse(
            customer_id=customer.customer_id,
            churn_probability=float(churn_proba),
            churn_prediction=churn_pred,
            risk_level=risk_level,
            timestamp=datetime.now().isoformat(),
        )

        # Cache result
        cache.set(cache_key, response.dict(), ttl=3600)

        # Track metrics
        duration = (datetime.now() - start_time).total_seconds()
        metrics.track_prediction(
            model_name=model_version or "unknown",
            prediction_type="single",
            duration=duration,
        )

        logger.info(
            f"Prediction for {customer.customer_id}: "
            f"probability={churn_proba:.3f}, risk={risk_level}"
        )

        return response

    except Exception as e:
        logger.error(f"Prediction failed for {customer.customer_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest):
    """Predict churn for multiple customers.

    Args:
        request: Batch prediction request with list of customers

    Returns:
        Batch prediction response with all predictions
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start_time = datetime.now()

    try:
        # Convert to DataFrame
        customers_data = [c.dict() for c in request.customers]
        df = pd.DataFrame(customers_data)

        # Engineer features
        if feature_engineer:
            df = feature_engineer.engineer_features(df, fit=False)

        # Make predictions
        df_features = df.drop(columns=["customer_id", "churn"], errors="ignore")
        churn_probas = model.predict_proba(df_features)[:, 1]
        churn_preds = (churn_probas >= 0.5).astype(int)

        # Create responses
        predictions = []
        high_risk_count = 0

        for idx, customer in enumerate(request.customers):
            churn_proba = float(churn_probas[idx])
            churn_pred = int(churn_preds[idx])

            # Determine risk level
            if churn_proba >= 0.7:
                risk_level = "high"
                high_risk_count += 1
            elif churn_proba >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"

            predictions.append(
                PredictionResponse(
                    customer_id=customer.customer_id,
                    churn_probability=churn_proba,
                    churn_prediction=churn_pred,
                    risk_level=risk_level,
                    timestamp=datetime.now().isoformat(),
                )
            )

        # Track metrics
        duration = (datetime.now() - start_time).total_seconds()
        metrics.track_prediction(
            model_name=model_version or "unknown",
            prediction_type="batch",
            duration=duration,
            count=len(request.customers),
        )

        logger.info(
            f"Batch prediction: {len(request.customers)} customers, "
            f"{high_risk_count} high risk, {duration:.3f}s"
        )

        return BatchPredictionResponse(
            predictions=predictions,
            total_customers=len(request.customers),
            high_risk_count=high_risk_count,
        )

    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/info")
async def model_info():
    """Get model information."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    info = {
        "model_version": model_version,
        "model_type": type(model).__name__,
        "features_count": len(feature_engineer.get_feature_names())
        if feature_engineer
        else 0,
        "loaded_at": datetime.now().isoformat(),
    }

    return info


@app.post("/model/reload")
async def reload_model(model_path: Optional[str] = None):
    """Reload model from path or MLflow.

    Args:
        model_path: Optional model path or MLflow URI
    """
    try:
        load_model(model_path)
        return {"status": "success", "message": "Model reloaded successfully"}
    except Exception as e:
        logger.error(f"Failed to reload model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the API server."""
    import uvicorn

    uvicorn.run(
        "src.api.server:app",
        host=config.api_host,
        port=config.api_port,
        reload=False,
        workers=config.api_workers,
    )


if __name__ == "__main__":
    main()
