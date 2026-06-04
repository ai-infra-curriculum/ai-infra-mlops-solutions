"""Base connector class for data ingestion."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd

from src.utils.logger import get_logger
from src.utils.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class BaseConnector(ABC):
    """Abstract base class for data connectors."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize connector.

        Args:
            name: Connector name
            config: Connector-specific configuration
        """
        self.name = name
        self.config = config or {}
        self._last_ingestion_time: Optional[datetime] = None
        self._records_ingested = 0

        logger.info(f"Initialized {self.__class__.__name__}: {self.name}")

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to data source.

        Raises:
            ConnectionError: If connection fails
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to data source."""
        pass

    @abstractmethod
    def read(
        self,
        query: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Read data from source.

        Args:
            query: Optional query/filter
            params: Query parameters
            **kwargs: Additional connector-specific arguments

        Returns:
            DataFrame containing ingested data

        Raises:
            Exception: On read failures
        """
        pass

    def validate_connection(self) -> bool:
        """Validate connection to data source.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            self.connect()
            logger.debug(f"Connection validated for {self.name}")
            return True
        except Exception as e:
            logger.error(f"Connection validation failed for {self.name}: {e}")
            return False
        finally:
            try:
                self.disconnect()
            except Exception:
                pass

    def ingest(
        self,
        query: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        incremental: bool = False,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Ingest data with error handling and metrics.

        Args:
            query: Optional query/filter
            params: Query parameters
            incremental: Whether to perform incremental ingestion
            **kwargs: Additional arguments

        Returns:
            DataFrame containing ingested data

        Raises:
            Exception: On ingestion failures
        """
        start_time = datetime.now()
        logger.info(f"Starting data ingestion from {self.name}")

        try:
            # Connect to source
            self.connect()

            # Handle incremental ingestion
            if incremental and self._last_ingestion_time:
                logger.info(f"Performing incremental ingestion since {self._last_ingestion_time}")
                if params is None:
                    params = {}
                params["last_ingestion_time"] = self._last_ingestion_time

            # Read data
            df = self.read(query=query, params=params, **kwargs)

            # Update metrics
            records_count = len(df)
            self._records_ingested += records_count
            self._last_ingestion_time = datetime.now()

            duration = (self._last_ingestion_time - start_time).total_seconds()

            # Log metrics
            metrics.increment_data_ingestion(
                source=self.name,
                status="success",
                count=records_count,
            )

            logger.info(
                f"Successfully ingested {records_count} records from {self.name} "
                f"in {duration:.2f}s"
            )

            return df

        except Exception as e:
            logger.error(f"Failed to ingest data from {self.name}: {e}")
            metrics.increment_data_ingestion(
                source=self.name,
                status="failure",
                count=0,
            )
            raise

        finally:
            try:
                self.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting from {self.name}: {e}")

    def get_metadata(self) -> Dict[str, Any]:
        """Get connector metadata.

        Returns:
            Dictionary containing connector metadata
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "last_ingestion_time": self._last_ingestion_time.isoformat()
            if self._last_ingestion_time
            else None,
            "total_records_ingested": self._records_ingested,
            "config": {k: v for k, v in self.config.items() if k not in ["password", "api_key"]},
        }

    def __enter__(self) -> "BaseConnector":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}')"
