"""Data ingestion pipeline orchestrator."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from src.data.connectors.api_connector import APIConnector
from src.data.connectors.base import BaseConnector
from src.data.connectors.csv_connector import CSVConnector
from src.data.connectors.database_connector import DatabaseConnector
from src.data.connectors.kafka_connector import KafkaConnector
from src.utils.config import get_config
from src.utils.logger import get_logger
from src.utils.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()
config = get_config()


class DataIngestionPipeline:
    """Orchestrates data ingestion from multiple sources."""

    def __init__(
        self,
        pipeline_name: str = "default",
        enable_caching: bool = True,
        cache_ttl: int = 3600,
    ):
        """Initialize data ingestion pipeline.

        Args:
            pipeline_name: Name of the pipeline
            enable_caching: Whether to enable result caching
            cache_ttl: Cache time-to-live in seconds
        """
        self.pipeline_name = pipeline_name
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl

        # Registry of connectors
        self._connectors: Dict[str, BaseConnector] = {}

        # Pipeline metadata
        self._metadata = {
            "pipeline_name": pipeline_name,
            "created_at": datetime.now(),
            "ingestions": [],
        }

        logger.info(f"Initialized DataIngestionPipeline: {pipeline_name}")

    def register_connector(
        self,
        connector_name: str,
        connector: BaseConnector,
    ) -> None:
        """Register a data connector.

        Args:
            connector_name: Unique name for the connector
            connector: Connector instance
        """
        if connector_name in self._connectors:
            logger.warning(f"Connector '{connector_name}' already registered, overwriting")

        self._connectors[connector_name] = connector
        logger.info(f"Registered connector: {connector_name} ({connector.__class__.__name__})")

    def register_csv_connector(
        self,
        name: str,
        file_path: Optional[str] = None,
        s3_bucket: Optional[str] = None,
        s3_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Register a CSV connector.

        Args:
            name: Connector name
            file_path: Path to CSV file (local or S3)
            s3_bucket: S3 bucket name
            s3_prefix: S3 key prefix
            **kwargs: Additional CSVConnector arguments
        """
        connector = CSVConnector(
            name=name,
            file_path=file_path,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            aws_region=config.aws_region,
            **kwargs,
        )
        self.register_connector(name, connector)

    def register_database_connector(
        self,
        name: str,
        database_url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Register a database connector.

        Args:
            name: Connector name
            database_url: Complete database URL
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            **kwargs: Additional DatabaseConnector arguments
        """
        connector = DatabaseConnector(
            name=name,
            database_url=database_url,
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            **kwargs,
        )
        self.register_connector(name, connector)

    def register_api_connector(
        self,
        name: str,
        base_url: Optional[str] = None,
        endpoint: Optional[str] = None,
        auth_type: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Register an API connector.

        Args:
            name: Connector name
            base_url: Base URL of the API
            endpoint: API endpoint path
            auth_type: Authentication type
            api_key: API key
            **kwargs: Additional APIConnector arguments
        """
        connector = APIConnector(
            name=name,
            base_url=base_url,
            endpoint=endpoint,
            auth_type=auth_type,
            api_key=api_key,
            **kwargs,
        )
        self.register_connector(name, connector)

    def register_kafka_connector(
        self,
        name: str,
        bootstrap_servers: Optional[str] = None,
        topic: Optional[str] = None,
        group_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Register a Kafka connector.

        Args:
            name: Connector name
            bootstrap_servers: Kafka bootstrap servers
            topic: Kafka topic
            group_id: Consumer group ID
            **kwargs: Additional KafkaConnector arguments
        """
        connector = KafkaConnector(
            name=name,
            bootstrap_servers=bootstrap_servers,
            topic=topic,
            group_id=group_id,
            **kwargs,
        )
        self.register_connector(name, connector)

    def get_connector(self, connector_name: str) -> BaseConnector:
        """Get a registered connector.

        Args:
            connector_name: Name of the connector

        Returns:
            Connector instance

        Raises:
            KeyError: If connector not found
        """
        if connector_name not in self._connectors:
            raise KeyError(f"Connector '{connector_name}' not registered")

        return self._connectors[connector_name]

    def list_connectors(self) -> List[str]:
        """List all registered connectors.

        Returns:
            List of connector names
        """
        return list(self._connectors.keys())

    def ingest(
        self,
        connector_name: str,
        query: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        incremental: bool = False,
        validate: bool = True,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Ingest data from a specific connector.

        Args:
            connector_name: Name of the connector to use
            query: Query/path/endpoint for the connector
            params: Query parameters
            incremental: Whether to perform incremental ingestion
            validate: Whether to validate connection before ingestion
            **kwargs: Additional connector-specific arguments

        Returns:
            DataFrame containing ingested data

        Raises:
            KeyError: If connector not found
            Exception: On ingestion failures
        """
        start_time = datetime.now()
        connector = self.get_connector(connector_name)

        logger.info(
            f"Starting ingestion from connector '{connector_name}' "
            f"(incremental={incremental})"
        )

        try:
            # Validate connection if requested
            if validate and not connector.validate_connection():
                raise ConnectionError(f"Failed to validate connector '{connector_name}'")

            # Perform ingestion
            df = connector.ingest(
                query=query,
                params=params,
                incremental=incremental,
                **kwargs,
            )

            # Record ingestion metadata
            ingestion_metadata = {
                "connector_name": connector_name,
                "connector_type": connector.__class__.__name__,
                "query": query,
                "records_count": len(df),
                "start_time": start_time,
                "end_time": datetime.now(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "incremental": incremental,
            }
            self._metadata["ingestions"].append(ingestion_metadata)

            logger.info(
                f"Successfully ingested {len(df)} records from '{connector_name}' "
                f"in {ingestion_metadata['duration_seconds']:.2f}s"
            )

            return df

        except Exception as e:
            logger.error(f"Failed to ingest from '{connector_name}': {e}")
            metrics.increment_data_ingestion(
                source=connector_name,
                status="failure",
                count=0,
            )
            raise

    def ingest_multiple(
        self,
        sources: List[Dict[str, Any]],
        merge_on: Optional[Union[str, List[str]]] = None,
        merge_how: str = "outer",
        validate_all: bool = True,
    ) -> pd.DataFrame:
        """Ingest data from multiple sources and optionally merge.

        Args:
            sources: List of source configurations, each containing:
                - connector_name: Name of the connector
                - query: Query/path/endpoint
                - params: Query parameters (optional)
                - incremental: Whether incremental (optional)
                - **kwargs: Additional connector arguments
            merge_on: Column(s) to merge on (None for concatenation)
            merge_how: How to merge ('inner', 'outer', 'left', 'right')
            validate_all: Whether to validate all connections before starting

        Returns:
            DataFrame containing merged/concatenated data

        Raises:
            ValueError: If sources is empty or invalid
        """
        if not sources:
            raise ValueError("Sources list cannot be empty")

        logger.info(f"Starting multi-source ingestion from {len(sources)} sources")

        # Validate all connections first if requested
        if validate_all:
            logger.info("Validating all connectors before ingestion")
            for source in sources:
                connector_name = source.get("connector_name")
                if not connector_name:
                    raise ValueError("Each source must have 'connector_name'")

                connector = self.get_connector(connector_name)
                if not connector.validate_connection():
                    raise ConnectionError(
                        f"Failed to validate connector '{connector_name}'"
                    )

        # Ingest from all sources
        dataframes = []
        for idx, source in enumerate(sources):
            connector_name = source.pop("connector_name")
            query = source.pop("query", None)
            params = source.pop("params", None)
            incremental = source.pop("incremental", False)

            logger.info(f"Ingesting from source {idx + 1}/{len(sources)}: {connector_name}")

            try:
                df = self.ingest(
                    connector_name=connector_name,
                    query=query,
                    params=params,
                    incremental=incremental,
                    validate=False,  # Already validated
                    **source,
                )
                dataframes.append(df)
            except Exception as e:
                logger.error(f"Failed to ingest from source '{connector_name}': {e}")
                # Continue with other sources or raise based on policy
                # For now, we'll raise to ensure data integrity
                raise

        if not dataframes:
            logger.warning("No data ingested from any source")
            return pd.DataFrame()

        # Merge or concatenate DataFrames
        if merge_on:
            logger.info(f"Merging {len(dataframes)} DataFrames on '{merge_on}' (how={merge_how})")
            result_df = dataframes[0]
            for df in dataframes[1:]:
                result_df = pd.merge(result_df, df, on=merge_on, how=merge_how)
        else:
            logger.info(f"Concatenating {len(dataframes)} DataFrames")
            result_df = pd.concat(dataframes, ignore_index=True)

        logger.info(f"Multi-source ingestion complete: {len(result_df)} total records")

        return result_df

    def save_to_file(
        self,
        df: pd.DataFrame,
        output_path: str,
        file_format: str = "parquet",
        **kwargs: Any,
    ) -> None:
        """Save DataFrame to file.

        Args:
            df: DataFrame to save
            output_path: Output file path
            file_format: File format ('csv', 'parquet', 'json', 'feather')
            **kwargs: Format-specific arguments
        """
        # Create directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving {len(df)} records to {output_path} ({file_format} format)")

        try:
            if file_format == "csv":
                df.to_csv(output_path, index=False, **kwargs)
            elif file_format == "parquet":
                df.to_parquet(output_path, index=False, **kwargs)
            elif file_format == "json":
                df.to_json(output_path, orient="records", **kwargs)
            elif file_format == "feather":
                df.to_feather(output_path, **kwargs)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")

            logger.info(f"Successfully saved data to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save data to {output_path}: {e}")
            raise

    def save_to_database(
        self,
        df: pd.DataFrame,
        connector_name: str,
        table_name: str,
        schema: Optional[str] = None,
        if_exists: str = "append",
        **kwargs: Any,
    ) -> None:
        """Save DataFrame to database table.

        Args:
            df: DataFrame to save
            connector_name: Name of the database connector
            table_name: Target table name
            schema: Database schema name
            if_exists: How to behave if table exists ('fail', 'replace', 'append')
            **kwargs: Additional to_sql arguments
        """
        connector = self.get_connector(connector_name)

        if not isinstance(connector, DatabaseConnector):
            raise TypeError(
                f"Connector '{connector_name}' is not a DatabaseConnector "
                f"(type: {connector.__class__.__name__})"
            )

        logger.info(
            f"Saving {len(df)} records to table '{table_name}' "
            f"via connector '{connector_name}'"
        )

        try:
            connector.connect()
            connector.write(
                df=df,
                table_name=table_name,
                schema=schema,
                if_exists=if_exists,
                **kwargs,
            )
            logger.info(f"Successfully saved data to table '{table_name}'")

        except Exception as e:
            logger.error(f"Failed to save data to table '{table_name}': {e}")
            raise

        finally:
            connector.disconnect()

    def get_metadata(self) -> Dict[str, Any]:
        """Get pipeline metadata.

        Returns:
            Dictionary containing pipeline metadata
        """
        return {
            **self._metadata,
            "total_ingestions": len(self._metadata["ingestions"]),
            "total_records": sum(
                ing["records_count"] for ing in self._metadata["ingestions"]
            ),
            "registered_connectors": {
                name: connector.get_metadata()
                for name, connector in self._connectors.items()
            },
        }

    def clear_connectors(self) -> None:
        """Clear all registered connectors."""
        logger.info(f"Clearing {len(self._connectors)} registered connectors")
        self._connectors.clear()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"DataIngestionPipeline(name='{self.pipeline_name}', "
            f"connectors={len(self._connectors)})"
        )


def create_pipeline_from_config(config_dict: Dict[str, Any]) -> DataIngestionPipeline:
    """Create and configure pipeline from configuration dictionary.

    Args:
        config_dict: Pipeline configuration with structure:
            {
                "pipeline_name": "my_pipeline",
                "enable_caching": true,
                "cache_ttl": 3600,
                "connectors": [
                    {
                        "type": "csv",
                        "name": "customer_data",
                        "file_path": "/path/to/customers.csv"
                    },
                    {
                        "type": "database",
                        "name": "transactions_db",
                        "database_url": "postgresql://..."
                    },
                    ...
                ]
            }

    Returns:
        Configured DataIngestionPipeline instance
    """
    # Create pipeline
    pipeline = DataIngestionPipeline(
        pipeline_name=config_dict.get("pipeline_name", "default"),
        enable_caching=config_dict.get("enable_caching", True),
        cache_ttl=config_dict.get("cache_ttl", 3600),
    )

    # Register connectors
    connectors = config_dict.get("connectors", [])
    for connector_config in connectors:
        connector_type = connector_config.pop("type")
        connector_name = connector_config.pop("name")

        if connector_type == "csv":
            pipeline.register_csv_connector(connector_name, **connector_config)
        elif connector_type == "database":
            pipeline.register_database_connector(connector_name, **connector_config)
        elif connector_type == "api":
            pipeline.register_api_connector(connector_name, **connector_config)
        elif connector_type == "kafka":
            pipeline.register_kafka_connector(connector_name, **connector_config)
        else:
            logger.warning(f"Unknown connector type: {connector_type}")

    logger.info(
        f"Created pipeline '{pipeline.pipeline_name}' with "
        f"{len(pipeline.list_connectors())} connectors"
    )

    return pipeline
