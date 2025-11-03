"""Database connection and management utilities."""

from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manage database connections and operations."""

    def __init__(
        self,
        database_url: Optional[str] = None,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
    ):
        """Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL (uses config if not provided)
            pool_size: Number of permanent connections to maintain
            max_overflow: Number of connections that can be created beyond pool_size
            pool_timeout: Seconds to wait before giving up on getting a connection
            pool_recycle: Seconds after which to recycle connections
        """
        config = get_config()
        self.database_url = database_url or config.database_url

        try:
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_recycle=pool_recycle,
                echo=config.debug,
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("Database connection initialized successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session context manager.

        Yields:
            Database session

        Raises:
            SQLAlchemyError: On database errors
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        fetch: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        """Execute a SQL query.

        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results

        Returns:
            Query results as list of dictionaries if fetch=True, else None

        Raises:
            SQLAlchemyError: On database errors
        """
        with self.get_session() as session:
            try:
                result = session.execute(text(query), params or {})

                if fetch:
                    # Convert result to list of dictionaries
                    columns = result.keys()
                    rows = result.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                else:
                    session.commit()
                    return None

            except SQLAlchemyError as e:
                logger.error(f"Query execution failed: {e}")
                logger.debug(f"Query: {query}")
                logger.debug(f"Params: {params}")
                raise

    def execute_many(
        self,
        query: str,
        params_list: List[Dict[str, Any]],
    ) -> None:
        """Execute a SQL query with multiple parameter sets.

        Args:
            query: SQL query string
            params_list: List of parameter dictionaries

        Raises:
            SQLAlchemyError: On database errors
        """
        with self.get_session() as session:
            try:
                session.execute(text(query), params_list)
                session.commit()
                logger.debug(f"Executed query with {len(params_list)} parameter sets")
            except SQLAlchemyError as e:
                logger.error(f"Batch execution failed: {e}")
                raise

    def read_dataframe(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        chunksize: Optional[int] = None,
    ) -> pd.DataFrame:
        """Read query results into a pandas DataFrame.

        Args:
            query: SQL query string
            params: Query parameters
            chunksize: Number of rows to read at a time (for large results)

        Returns:
            pandas DataFrame containing query results

        Raises:
            SQLAlchemyError: On database errors
        """
        try:
            df = pd.read_sql_query(
                sql=query,
                con=self.engine,
                params=params,
                chunksize=chunksize,
            )
            logger.debug(f"Read {len(df) if not chunksize else 'chunked'} rows from database")
            return df
        except SQLAlchemyError as e:
            logger.error(f"Failed to read DataFrame: {e}")
            raise

    def write_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "append",
        index: bool = False,
        chunksize: int = 10000,
    ) -> None:
        """Write a pandas DataFrame to database table.

        Args:
            df: pandas DataFrame to write
            table_name: Target table name
            if_exists: How to behave if table exists ('fail', 'replace', 'append')
            index: Whether to write DataFrame index
            chunksize: Number of rows to write at a time

        Raises:
            SQLAlchemyError: On database errors
        """
        try:
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists=if_exists,
                index=index,
                chunksize=chunksize,
                method="multi",
            )
            logger.info(f"Wrote {len(df)} rows to table '{table_name}'")
        except SQLAlchemyError as e:
            logger.error(f"Failed to write DataFrame to table '{table_name}': {e}")
            raise

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists.

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            )
        """
        result = self.execute_query(query, {"table_name": table_name})
        return result[0]["exists"] if result else False

    def get_table_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table.

        Args:
            table_name: Name of the table

        Returns:
            Number of rows in the table

        Raises:
            ValueError: If table doesn't exist
        """
        if not self.table_exists(table_name):
            raise ValueError(f"Table '{table_name}' does not exist")

        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    def truncate_table(self, table_name: str, cascade: bool = False) -> None:
        """Truncate a table.

        Args:
            table_name: Name of the table to truncate
            cascade: Whether to cascade truncation to dependent tables

        Raises:
            ValueError: If table doesn't exist
        """
        if not self.table_exists(table_name):
            raise ValueError(f"Table '{table_name}' does not exist")

        cascade_clause = "CASCADE" if cascade else ""
        query = f"TRUNCATE TABLE {table_name} {cascade_clause}"
        self.execute_query(query, fetch=False)
        logger.info(f"Truncated table '{table_name}'")

    def close(self) -> None:
        """Close database connections and dispose of connection pool."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

    def __enter__(self) -> "DatabaseManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
