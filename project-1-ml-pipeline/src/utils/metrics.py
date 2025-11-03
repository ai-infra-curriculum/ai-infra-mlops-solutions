"""Prometheus metrics collection and management."""

from typing import Dict, List, Optional

from prometheus_client import Counter, Gauge, Histogram, Info, Summary
from prometheus_client import REGISTRY, CollectorRegistry
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from src.utils.logger import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Centralized metrics collector using Prometheus."""

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize metrics collector.

        Args:
            registry: Prometheus registry (uses default if not provided)
        """
        self.registry = registry or REGISTRY
        self._metrics: Dict[str, any] = {}

        # Initialize common metrics
        self._init_api_metrics()
        self._init_model_metrics()
        self._init_data_metrics()
        self._init_system_metrics()

        logger.info("Metrics collector initialized")

    def _init_api_metrics(self) -> None:
        """Initialize API-related metrics."""
        self._metrics["api_requests_total"] = Counter(
            "api_requests_total",
            "Total number of API requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self._metrics["api_request_duration_seconds"] = Histogram(
            "api_request_duration_seconds",
            "API request duration in seconds",
            ["method", "endpoint"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
            registry=self.registry,
        )

        self._metrics["api_errors_total"] = Counter(
            "api_errors_total",
            "Total number of API errors",
            ["method", "endpoint", "error_type"],
            registry=self.registry,
        )

        self._metrics["api_active_requests"] = Gauge(
            "api_active_requests",
            "Number of active API requests",
            registry=self.registry,
        )

    def _init_model_metrics(self) -> None:
        """Initialize model-related metrics."""
        self._metrics["predictions_total"] = Counter(
            "predictions_total",
            "Total number of predictions made",
            ["model_name", "model_version"],
            registry=self.registry,
        )

        self._metrics["prediction_duration_seconds"] = Histogram(
            "prediction_duration_seconds",
            "Model prediction duration in seconds",
            ["model_name", "model_version"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
            registry=self.registry,
        )

        self._metrics["prediction_probability"] = Histogram(
            "prediction_probability",
            "Distribution of prediction probabilities",
            ["model_name", "prediction_class"],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry,
        )

        self._metrics["model_load_time_seconds"] = Gauge(
            "model_load_time_seconds",
            "Time taken to load model in seconds",
            ["model_name", "model_version"],
            registry=self.registry,
        )

        self._metrics["model_info"] = Info(
            "model_info",
            "Information about the current model",
            registry=self.registry,
        )

    def _init_data_metrics(self) -> None:
        """Initialize data-related metrics."""
        self._metrics["data_ingestion_records_total"] = Counter(
            "data_ingestion_records_total",
            "Total number of records ingested",
            ["source", "status"],
            registry=self.registry,
        )

        self._metrics["data_validation_checks_total"] = Counter(
            "data_validation_checks_total",
            "Total number of validation checks",
            ["check_type", "result"],
            registry=self.registry,
        )

        self._metrics["feature_generation_duration_seconds"] = Histogram(
            "feature_generation_duration_seconds",
            "Feature generation duration in seconds",
            buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry,
        )

        self._metrics["feature_drift_score"] = Gauge(
            "feature_drift_score",
            "Drift score for each feature",
            ["feature_name", "drift_method"],
            registry=self.registry,
        )

    def _init_system_metrics(self) -> None:
        """Initialize system-related metrics."""
        self._metrics["training_duration_seconds"] = Histogram(
            "training_duration_seconds",
            "Model training duration in seconds",
            ["model_type"],
            buckets=[60, 300, 600, 1800, 3600, 7200],
            registry=self.registry,
        )

        self._metrics["training_accuracy"] = Gauge(
            "training_accuracy",
            "Model training accuracy",
            ["model_type", "dataset"],
            registry=self.registry,
        )

        self._metrics["model_auc_roc"] = Gauge(
            "model_auc_roc",
            "Model AUC-ROC score",
            ["model_type", "dataset"],
            registry=self.registry,
        )

        self._metrics["drift_alerts_total"] = Counter(
            "drift_alerts_total",
            "Total number of drift alerts",
            ["severity", "drift_type"],
            registry=self.registry,
        )

        self._metrics["cache_hits_total"] = Counter(
            "cache_hits_total",
            "Total number of cache hits",
            ["cache_type"],
            registry=self.registry,
        )

        self._metrics["cache_misses_total"] = Counter(
            "cache_misses_total",
            "Total number of cache misses",
            ["cache_type"],
            registry=self.registry,
        )

    # API metrics methods
    def increment_api_requests(
        self, method: str, endpoint: str, status: int
    ) -> None:
        """Increment API request counter.

        Args:
            method: HTTP method
            endpoint: API endpoint
            status: HTTP status code
        """
        self._metrics["api_requests_total"].labels(
            method=method, endpoint=endpoint, status=status
        ).inc()

    def observe_api_duration(
        self, method: str, endpoint: str, duration: float
    ) -> None:
        """Record API request duration.

        Args:
            method: HTTP method
            endpoint: API endpoint
            duration: Request duration in seconds
        """
        self._metrics["api_request_duration_seconds"].labels(
            method=method, endpoint=endpoint
        ).observe(duration)

    def increment_api_errors(
        self, method: str, endpoint: str, error_type: str
    ) -> None:
        """Increment API error counter.

        Args:
            method: HTTP method
            endpoint: API endpoint
            error_type: Type of error
        """
        self._metrics["api_errors_total"].labels(
            method=method, endpoint=endpoint, error_type=error_type
        ).inc()

    def set_active_requests(self, count: int) -> None:
        """Set number of active requests.

        Args:
            count: Number of active requests
        """
        self._metrics["api_active_requests"].set(count)

    # Model metrics methods
    def increment_predictions(
        self, model_name: str, model_version: str
    ) -> None:
        """Increment prediction counter.

        Args:
            model_name: Name of the model
            model_version: Version of the model
        """
        self._metrics["predictions_total"].labels(
            model_name=model_name, model_version=model_version
        ).inc()

    def observe_prediction_duration(
        self, model_name: str, model_version: str, duration: float
    ) -> None:
        """Record prediction duration.

        Args:
            model_name: Name of the model
            model_version: Version of the model
            duration: Prediction duration in seconds
        """
        self._metrics["prediction_duration_seconds"].labels(
            model_name=model_name, model_version=model_version
        ).observe(duration)

    def observe_prediction_probability(
        self, model_name: str, prediction_class: str, probability: float
    ) -> None:
        """Record prediction probability.

        Args:
            model_name: Name of the model
            prediction_class: Predicted class
            probability: Prediction probability
        """
        self._metrics["prediction_probability"].labels(
            model_name=model_name, prediction_class=prediction_class
        ).observe(probability)

    def set_model_load_time(
        self, model_name: str, model_version: str, duration: float
    ) -> None:
        """Set model load time.

        Args:
            model_name: Name of the model
            model_version: Version of the model
            duration: Load time in seconds
        """
        self._metrics["model_load_time_seconds"].labels(
            model_name=model_name, model_version=model_version
        ).set(duration)

    def set_model_info(self, info: Dict[str, str]) -> None:
        """Set model information.

        Args:
            info: Dictionary containing model information
        """
        self._metrics["model_info"].info(info)

    # Data metrics methods
    def increment_data_ingestion(
        self, source: str, status: str, count: int = 1
    ) -> None:
        """Increment data ingestion counter.

        Args:
            source: Data source name
            status: Ingestion status (success/failure)
            count: Number of records
        """
        self._metrics["data_ingestion_records_total"].labels(
            source=source, status=status
        ).inc(count)

    def increment_validation_checks(
        self, check_type: str, result: str
    ) -> None:
        """Increment validation check counter.

        Args:
            check_type: Type of validation check
            result: Check result (pass/fail)
        """
        self._metrics["data_validation_checks_total"].labels(
            check_type=check_type, result=result
        ).inc()

    def observe_feature_generation_duration(self, duration: float) -> None:
        """Record feature generation duration.

        Args:
            duration: Generation duration in seconds
        """
        self._metrics["feature_generation_duration_seconds"].observe(duration)

    def set_feature_drift_score(
        self, feature_name: str, drift_method: str, score: float
    ) -> None:
        """Set feature drift score.

        Args:
            feature_name: Name of the feature
            drift_method: Drift detection method
            score: Drift score
        """
        self._metrics["feature_drift_score"].labels(
            feature_name=feature_name, drift_method=drift_method
        ).set(score)

    # System metrics methods
    def observe_training_duration(
        self, model_type: str, duration: float
    ) -> None:
        """Record training duration.

        Args:
            model_type: Type of model
            duration: Training duration in seconds
        """
        self._metrics["training_duration_seconds"].labels(
            model_type=model_type
        ).observe(duration)

    def set_training_accuracy(
        self, model_type: str, dataset: str, accuracy: float
    ) -> None:
        """Set training accuracy.

        Args:
            model_type: Type of model
            dataset: Dataset name (train/val/test)
            accuracy: Accuracy score
        """
        self._metrics["training_accuracy"].labels(
            model_type=model_type, dataset=dataset
        ).set(accuracy)

    def set_model_auc_roc(
        self, model_type: str, dataset: str, auc_roc: float
    ) -> None:
        """Set model AUC-ROC score.

        Args:
            model_type: Type of model
            dataset: Dataset name
            auc_roc: AUC-ROC score
        """
        self._metrics["model_auc_roc"].labels(
            model_type=model_type, dataset=dataset
        ).set(auc_roc)

    def increment_drift_alerts(
        self, severity: str, drift_type: str
    ) -> None:
        """Increment drift alert counter.

        Args:
            severity: Alert severity level
            drift_type: Type of drift
        """
        self._metrics["drift_alerts_total"].labels(
            severity=severity, drift_type=drift_type
        ).inc()

    def increment_cache_hits(self, cache_type: str) -> None:
        """Increment cache hit counter.

        Args:
            cache_type: Type of cache
        """
        self._metrics["cache_hits_total"].labels(cache_type=cache_type).inc()

    def increment_cache_misses(self, cache_type: str) -> None:
        """Increment cache miss counter.

        Args:
            cache_type: Type of cache
        """
        self._metrics["cache_misses_total"].labels(cache_type=cache_type).inc()

    def get_metrics(self) -> bytes:
        """Get all metrics in Prometheus format.

        Returns:
            Metrics in Prometheus text format
        """
        return generate_latest(self.registry)

    def get_content_type(self) -> str:
        """Get content type for metrics response.

        Returns:
            Content type string
        """
        return CONTENT_TYPE_LATEST


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance.

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
