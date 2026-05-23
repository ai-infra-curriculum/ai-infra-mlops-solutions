"""Feature store implementation using PostgreSQL."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy import Column, DateTime, Float, Integer, MetaData, String, Table, create_engine
from sqlalchemy.exc import SQLAlchemyError

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.utils.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()
config = get_config()


class FeatureStore:
    """Feature store for versioned feature management."""

    def __init__(
        self,
        database_url: Optional[str] = None,
        schema: str = "feature_store",
    ):
        """Initialize feature store.

        Args:
            database_url: Database connection URL
            schema: Database schema name
        """
        self.database_url = database_url or config.database_url
        self.schema = schema
        self.engine = create_engine(self.database_url)
        self.metadata = MetaData(schema=schema)

        # Initialize schema
        self._init_schema()

        logger.info(f"Initialized FeatureStore with schema '{schema}'")

    def _init_schema(self) -> None:
        """Initialize feature store schema and tables."""
        try:
            # Create schema if not exists
            with self.engine.connect() as conn:
                conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")
                conn.commit()

            # Define feature sets table
            self.feature_sets = Table(
                "feature_sets",
                self.metadata,
                Column("feature_set_id", String, primary_key=True),
                Column("feature_set_name", String, nullable=False),
                Column("version", Integer, nullable=False),
                Column("description", String),
                Column("created_at", DateTime, default=datetime.now),
                Column("created_by", String),
                Column("feature_count", Integer),
                Column("entity_type", String),
            )

            # Define features table
            self.features = Table(
                "features",
                self.metadata,
                Column("feature_id", String, primary_key=True),
                Column("feature_set_id", String, nullable=False),
                Column("feature_name", String, nullable=False),
                Column("feature_type", String),
                Column("description", String),
                Column("created_at", DateTime, default=datetime.now),
            )

            # Define feature values table (wide format)
            self.feature_values = Table(
                "feature_values",
                self.metadata,
                Column("entity_id", String, primary_key=True),
                Column("feature_set_id", String, primary_key=True),
                Column("timestamp", DateTime, primary_key=True, default=datetime.now),
                # Dynamic columns added based on features
            )

            # Create tables
            self.metadata.create_all(self.engine)

            logger.debug(f"Initialized feature store schema '{self.schema}'")

        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize feature store schema: {e}")
            raise

    def create_feature_set(
        self,
        feature_set_name: str,
        features: List[str],
        version: int = 1,
        description: Optional[str] = None,
        entity_type: str = "customer",
        created_by: Optional[str] = None,
    ) -> str:
        """Create a new feature set.

        Args:
            feature_set_name: Name of the feature set
            features: List of feature names
            version: Feature set version
            description: Feature set description
            entity_type: Type of entity (customer, product, etc.)
            created_by: Creator identifier

        Returns:
            Feature set ID
        """
        feature_set_id = f"{feature_set_name}_v{version}"

        logger.info(
            f"Creating feature set '{feature_set_id}' with {len(features)} features"
        )

        try:
            with self.engine.connect() as conn:
                # Insert feature set metadata
                conn.execute(
                    self.feature_sets.insert().values(
                        feature_set_id=feature_set_id,
                        feature_set_name=feature_set_name,
                        version=version,
                        description=description,
                        created_at=datetime.now(),
                        created_by=created_by or "system",
                        feature_count=len(features),
                        entity_type=entity_type,
                    )
                )

                # Insert feature metadata
                for feature_name in features:
                    feature_id = f"{feature_set_id}:{feature_name}"
                    conn.execute(
                        self.features.insert().values(
                            feature_id=feature_id,
                            feature_set_id=feature_set_id,
                            feature_name=feature_name,
                            feature_type="float",  # Default type
                            created_at=datetime.now(),
                        )
                    )

                conn.commit()

            logger.info(f"Created feature set '{feature_set_id}'")
            return feature_set_id

        except SQLAlchemyError as e:
            logger.error(f"Failed to create feature set: {e}")
            raise

    def write_features(
        self,
        feature_set_id: str,
        df: pd.DataFrame,
        entity_id_column: str = "customer_id",
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Write features to the feature store.

        Args:
            feature_set_id: Feature set ID
            df: DataFrame containing features
            entity_id_column: Column name for entity ID
            timestamp: Feature timestamp (defaults to now)
        """
        timestamp = timestamp or datetime.now()

        logger.info(
            f"Writing {len(df)} feature records to feature set '{feature_set_id}'"
        )

        try:
            # Create table name for this feature set
            table_name = f"features_{feature_set_id.replace('-', '_')}"

            # Write to database (dynamic table per feature set)
            df_copy = df.copy()
            df_copy["entity_id"] = df_copy[entity_id_column]
            df_copy["feature_set_id"] = feature_set_id
            df_copy["timestamp"] = timestamp

            # Drop original entity ID column if different name
            if entity_id_column != "entity_id":
                df_copy = df_copy.drop(columns=[entity_id_column])

            df_copy.to_sql(
                name=table_name,
                con=self.engine,
                schema=self.schema,
                if_exists="append",
                index=False,
            )

            logger.info(f"Wrote features to table '{self.schema}.{table_name}'")
            metrics.increment_feature_store_writes(
                feature_set=feature_set_id,
                count=len(df),
            )

        except SQLAlchemyError as e:
            logger.error(f"Failed to write features: {e}")
            raise

    def read_features(
        self,
        feature_set_id: str,
        entity_ids: Optional[List[str]] = None,
        feature_names: Optional[List[str]] = None,
        as_of_timestamp: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Read features from the feature store.

        Args:
            feature_set_id: Feature set ID
            entity_ids: List of entity IDs (None for all)
            feature_names: List of feature names (None for all)
            as_of_timestamp: Point-in-time timestamp for features

        Returns:
            DataFrame with requested features
        """
        logger.info(f"Reading features from feature set '{feature_set_id}'")

        try:
            table_name = f"features_{feature_set_id.replace('-', '_')}"

            # Build query
            query = f'SELECT * FROM {self.schema}."{table_name}" WHERE 1=1'

            if entity_ids:
                entity_ids_str = "', '".join(entity_ids)
                query += f" AND entity_id IN ('{entity_ids_str}')"

            if as_of_timestamp:
                query += f" AND timestamp <= '{as_of_timestamp}'"

            # Get latest timestamp per entity (if as_of_timestamp provided)
            if as_of_timestamp:
                query = f"""
                SELECT t1.* FROM {self.schema}."{table_name}" t1
                INNER JOIN (
                    SELECT entity_id, MAX(timestamp) as max_timestamp
                    FROM {self.schema}."{table_name}"
                    WHERE timestamp <= '{as_of_timestamp}'
                    GROUP BY entity_id
                ) t2 ON t1.entity_id = t2.entity_id AND t1.timestamp = t2.max_timestamp
                """
                if entity_ids:
                    entity_ids_str = "', '".join(entity_ids)
                    query += f" WHERE t1.entity_id IN ('{entity_ids_str}')"

            df = pd.read_sql(query, con=self.engine)

            # Filter columns if specified
            if feature_names:
                keep_cols = ["entity_id", "feature_set_id", "timestamp"] + feature_names
                df = df[[col for col in keep_cols if col in df.columns]]

            logger.info(f"Read {len(df)} feature records")
            metrics.increment_feature_store_reads(
                feature_set=feature_set_id,
                count=len(df),
            )

            return df

        except SQLAlchemyError as e:
            logger.error(f"Failed to read features: {e}")
            raise

    def list_feature_sets(self) -> pd.DataFrame:
        """List all feature sets.

        Returns:
            DataFrame with feature set metadata
        """
        try:
            query = f"SELECT * FROM {self.schema}.feature_sets ORDER BY created_at DESC"
            df = pd.read_sql(query, con=self.engine)
            logger.info(f"Found {len(df)} feature sets")
            return df

        except SQLAlchemyError as e:
            logger.error(f"Failed to list feature sets: {e}")
            raise

    def get_feature_set_metadata(self, feature_set_id: str) -> Dict[str, Any]:
        """Get metadata for a feature set.

        Args:
            feature_set_id: Feature set ID

        Returns:
            Dictionary with feature set metadata
        """
        try:
            # Get feature set info
            query = f"""
            SELECT * FROM {self.schema}.feature_sets
            WHERE feature_set_id = '{feature_set_id}'
            """
            fs_df = pd.read_sql(query, con=self.engine)

            if fs_df.empty:
                raise ValueError(f"Feature set '{feature_set_id}' not found")

            # Get feature list
            query = f"""
            SELECT feature_name, feature_type, description
            FROM {self.schema}.features
            WHERE feature_set_id = '{feature_set_id}'
            """
            features_df = pd.read_sql(query, con=self.engine)

            metadata = fs_df.iloc[0].to_dict()
            metadata["features"] = features_df.to_dict("records")

            return metadata

        except SQLAlchemyError as e:
            logger.error(f"Failed to get feature set metadata: {e}")
            raise

    def delete_feature_set(self, feature_set_id: str) -> None:
        """Delete a feature set and all associated data.

        Args:
            feature_set_id: Feature set ID
        """
        logger.warning(f"Deleting feature set '{feature_set_id}' and all data")

        try:
            with self.engine.connect() as conn:
                # Delete feature values table
                table_name = f"features_{feature_set_id.replace('-', '_')}"
                conn.execute(f'DROP TABLE IF EXISTS {self.schema}."{table_name}"')

                # Delete features
                conn.execute(
                    f"DELETE FROM {self.schema}.features WHERE feature_set_id = '{feature_set_id}'"
                )

                # Delete feature set
                conn.execute(
                    f"DELETE FROM {self.schema}.feature_sets WHERE feature_set_id = '{feature_set_id}'"
                )

                conn.commit()

            logger.info(f"Deleted feature set '{feature_set_id}'")

        except SQLAlchemyError as e:
            logger.error(f"Failed to delete feature set: {e}")
            raise

    def __repr__(self) -> str:
        """String representation."""
        return f"FeatureStore(schema='{self.schema}')"
