"""Database connector for data ingestion."""

import time
from typing import Any, Dict, Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool

from src.data.connectors.base import BaseConnector
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseConnector(BaseConnector):
    """Connector for reading data from relational databases."""

    def __init__(
        self,
        name: str = "database",
        database_url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        dialect: str = "postgresql",
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs: Any,
    ):
        """Initialize database connector.

        Args:
            name: Connector name
            database_url: Complete SQLAlchemy database URL
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            dialect: SQL dialect (postgresql, mysql, sqlite, etc.)
            pool_size: Connection pool size
            max_overflow: Max connections beyond pool_size
            pool_timeout: Seconds to wait for connection
            pool_recycle: Seconds before recycling connections
            max_retries: Maximum retry attempts for failed connections
            retry_delay: Delay between retries in seconds
            **kwargs: Additional SQLAlchemy engine arguments
        """
        config = {
            "database_url": database_url,
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "dialect": dialect,
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_timeout": pool_timeout,
            "pool_recycle": pool_recycle,
            "max_retries": max_retries,
            "retry_delay": retry_delay,
            **kwargs,
        }
        super().__init__(name=name, config=config)

        # Build database URL if not provided
        if database_url:
            self.database_url = database_url
        else:
            self.database_url = self._build_database_url(
                dialect=dialect,
                user=user,
                password=password,
                host=host,
                port=port,
                database=database,
            )

        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.engine: Optional[Engine] = None

    @staticmethod
    def _build_database_url(
        dialect: str,
        user: str,
        password: str,
        host: str,
        port: Optional[int],
        database: str,
    ) -> str:
        """Build SQLAlchemy database URL.

        Args:
            dialect: SQL dialect
            user: Database user
            password: Database password
            host: Database host
            port: Database port
            database: Database name

        Returns:
            SQLAlchemy database URL
        """
        if port:
            return f"{dialect}://{user}:{password}@{host}:{port}/{database}"
        else:
            return f"{dialect}://{user}:{password}@{host}/{database}"

    def connect(self) -> None:
        """Establish database connection.

        Raises:
            ConnectionError: If connection fails after retries
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                self.engine = create_engine(
                    self.database_url,
                    poolclass=QueuePool,
                    pool_size=self.config["pool_size"],
                    max_overflow=self.config["max_overflow"],
                    pool_timeout=self.config["pool_timeout"],
                    pool_recycle=self.config["pool_recycle"],
                    echo=False,
                )

                # Test connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))

                logger.debug(f"Connected to database: {self.name}")
                return

            except SQLAlchemyError as e:
                logger.warning(
                    f"Connection attempt {attempt}/{self.max_retries} failed: {e}"
                )

                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)  # Exponential backoff
                else:
                    raise ConnectionError(
                        f"Failed to connect to database after {self.max_retries} attempts: {e}"
                    )

    def disconnect(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            logger.debug(f"Disconnected from database: {self.name}")

    def read(
        self,
        query: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        chunksize: Optional[int] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Read data from database.

        Args:
            query: SQL query
            params: Query parameters
            chunksize: Number of rows to read at a time
            **kwargs: Additional pandas read_sql arguments

        Returns:
            DataFrame containing query results

        Raises:
            ValueError: If query is not provided
            SQLAlchemyError: On query execution failures
        """
        if not query:
            raise ValueError("SQL query must be provided")

        if not self.engine:
            raise ConnectionError("Database engine not initialized")

        try:
            df = pd.read_sql_query(
                sql=query, con=self.engine, params=params, chunksize=chunksize, **kwargs
            )

            if chunksize:
                # Return iterator for chunked reading
                logger.info(f"Created chunked reader with chunksize={chunksize}")
                return df
            else:
                logger.info(f"Read {len(df)} records from database query")
                return df

        except SQLAlchemyError as e:
            logger.error(f"Failed to execute query: {e}")
            logger.debug(f"Query: {query}")
            logger.debug(f"Params: {params}")
            raise

    def execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Execute SQL statement (INSERT, UPDATE, DELETE).

        Args:
            query: SQL statement
            params: Query parameters

        Returns:
            Number of rows affected

        Raises:
            SQLAlchemyError: On execution failures
        """
        if not self.engine:
            raise ConnectionError("Database engine not initialized")

        try:
            with self.engine.begin() as conn:
                result = conn.execute(text(query), params or {})
                rows_affected = result.rowcount

            logger.info(f"Executed query, {rows_affected} rows affected")
            return rows_affected

        except SQLAlchemyError as e:
            logger.error(f"Failed to execute statement: {e}")
            logger.debug(f"Query: {query}")
            raise

    def read_table(
        self,
        table_name: str,
        schema: Optional[str] = None,
        columns: Optional[list] = None,
        where: Optional[str] = None,
        limit: Optional[int] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Read entire table or filtered rows.

        Args:
            table_name: Name of the table
            schema: Database schema name
            columns: List of columns to select
            where: WHERE clause (without WHERE keyword)
            limit: Maximum number of rows to return
            **kwargs: Additional pandas read_sql arguments

        Returns:
            DataFrame containing table data
        """
        # Build query
        cols = ", ".join(columns) if columns else "*"
        full_table_name = f"{schema}.{table_name}" if schema else table_name

        query = f"SELECT {cols} FROM {full_table_name}"

        if where:
            query += f" WHERE {where}"

        if limit:
            query += f" LIMIT {limit}"

        return self.read(query=query, **kwargs)

    def write(
        self,
        df: pd.DataFrame,
        table_name: str,
        schema: Optional[str] = None,
        if_exists: str = "append",
        index: bool = False,
        chunksize: int = 10000,
        **kwargs: Any,
    ) -> None:
        """Write DataFrame to database table.

        Args:
            df: DataFrame to write
            table_name: Target table name
            schema: Database schema name
            if_exists: How to behave if table exists ('fail', 'replace', 'append')
            index: Whether to write DataFrame index
            chunksize: Number of rows to write at a time
            **kwargs: Additional pandas to_sql arguments
        """
        if not self.engine:
            raise ConnectionError("Database engine not initialized")

        try:
            df.to_sql(
                name=table_name,
                con=self.engine,
                schema=schema,
                if_exists=if_exists,
                index=index,
                chunksize=chunksize,
                method="multi",
                **kwargs,
            )

            logger.info(f"Wrote {len(df)} records to table '{table_name}'")

        except SQLAlchemyError as e:
            logger.error(f"Failed to write to table '{table_name}': {e}")
            raise

    def table_exists(self, table_name: str, schema: Optional[str] = None) -> bool:
        """Check if table exists.

        Args:
            table_name: Name of the table
            schema: Database schema name

        Returns:
            True if table exists, False otherwise
        """
        if not self.engine:
            raise ConnectionError("Database engine not initialized")

        from sqlalchemy import inspect

        inspector = inspect(self.engine)
        tables = inspector.get_table_names(schema=schema)
        return table_name in tables

    def get_table_info(
        self, table_name: str, schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get table information including columns and row count.

        Args:
            table_name: Name of the table
            schema: Database schema name

        Returns:
            Dictionary containing table information
        """
        if not self.engine:
            raise ConnectionError("Database engine not initialized")

        from sqlalchemy import inspect

        inspector = inspect(self.engine)

        # Get columns
        columns = inspector.get_columns(table_name, schema=schema)

        # Get row count
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        count_query = f"SELECT COUNT(*) as count FROM {full_table_name}"
        result = self.read(query=count_query)
        row_count = result.iloc[0]["count"] if not result.empty else 0

        return {
            "table_name": table_name,
            "schema": schema,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                }
                for col in columns
            ],
            "row_count": row_count,
        }

    def list_tables(self, schema: Optional[str] = None) -> list:
        """List all tables in database.

        Args:
            schema: Database schema name

        Returns:
            List of table names
        """
        if not self.engine:
            raise ConnectionError("Database engine not initialized")

        from sqlalchemy import inspect

        inspector = inspect(self.engine)
        return inspector.get_table_names(schema=schema)
