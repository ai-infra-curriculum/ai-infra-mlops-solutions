"""ML Pipeline for Customer Churn Prediction.

This package implements a production-grade MLOps pipeline including:
- Data ingestion from multiple sources
- Data validation with Great Expectations
- Feature engineering and feature store
- Model training with hyperparameter optimization
- Model serving via REST API
- Monitoring and drift detection
- Orchestration with Airflow
"""

__version__ = "1.0.0"
__author__ = "AI Infrastructure Curriculum"
__email__ = "ai-infra-curriculum@joshua-ferguson.com"

from src.utils.config import Config
from src.utils.logger import get_logger

__all__ = ["Config", "get_logger", "__version__"]
