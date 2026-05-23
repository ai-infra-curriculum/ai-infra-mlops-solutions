"""CSV file connector for data ingestion."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from src.data.connectors.base import BaseConnector
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVConnector(BaseConnector):
    """Connector for reading CSV files from local filesystem or S3."""

    def __init__(
        self,
        name: str = "csv",
        file_path: Optional[str] = None,
        s3_bucket: Optional[str] = None,
        s3_prefix: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_region: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize CSV connector.

        Args:
            name: Connector name
            file_path: Path to CSV file (local or S3)
            s3_bucket: S3 bucket name (for S3 sources)
            s3_prefix: S3 key prefix (for S3 sources)
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            aws_region: AWS region
            **kwargs: Additional pandas read_csv arguments
        """
        config = {
            "file_path": file_path,
            "s3_bucket": s3_bucket,
            "s3_prefix": s3_prefix,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_region": aws_region or "us-east-1",
            **kwargs,
        }
        super().__init__(name=name, config=config)

        self.file_path = file_path
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.read_kwargs = kwargs

        # S3 client (lazy initialization)
        self._s3_client = None

    def connect(self) -> None:
        """Establish connection (validate file access).

        Raises:
            FileNotFoundError: If file doesn't exist
            ConnectionError: If S3 connection fails
        """
        if self.s3_bucket:
            # Initialize S3 client
            try:
                import boto3

                self._s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=self.config.get("aws_access_key_id"),
                    aws_secret_access_key=self.config.get("aws_secret_access_key"),
                    region_name=self.config.get("aws_region"),
                )
                logger.debug(f"Connected to S3 bucket: {self.s3_bucket}")
            except Exception as e:
                raise ConnectionError(f"Failed to connect to S3: {e}")
        elif self.file_path:
            # Check local file exists
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"CSV file not found: {self.file_path}")
            logger.debug(f"Validated local file: {self.file_path}")
        else:
            raise ValueError("Either file_path or s3_bucket must be provided")

    def disconnect(self) -> None:
        """Close connection."""
        self._s3_client = None
        logger.debug(f"Disconnected CSV connector: {self.name}")

    def read(
        self,
        query: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Read data from CSV file.

        Args:
            query: File path override (optional)
            params: Additional parameters
            **kwargs: Override pandas read_csv arguments

        Returns:
            DataFrame containing CSV data

        Raises:
            Exception: On read failures
        """
        # Determine file path
        file_path = query or self.file_path

        # Merge read kwargs
        read_args = {**self.read_kwargs, **kwargs}

        try:
            if self.s3_bucket:
                # Read from S3
                df = self._read_from_s3(file_path, **read_args)
            else:
                # Read from local file
                df = pd.read_csv(file_path, **read_args)

            logger.info(f"Read {len(df)} records from CSV: {file_path}")
            return df

        except Exception as e:
            logger.error(f"Failed to read CSV file '{file_path}': {e}")
            raise

    def _read_from_s3(self, s3_key: Optional[str] = None, **kwargs: Any) -> pd.DataFrame:
        """Read CSV from S3.

        Args:
            s3_key: S3 object key (uses s3_prefix if not provided)
            **kwargs: pandas read_csv arguments

        Returns:
            DataFrame containing CSV data
        """
        if not self._s3_client:
            raise ConnectionError("S3 client not initialized")

        key = s3_key or self.s3_prefix
        if not key:
            raise ValueError("S3 key must be provided")

        try:
            # Get object from S3
            response = self._s3_client.get_object(Bucket=self.s3_bucket, Key=key)

            # Read CSV from bytes
            df = pd.read_csv(response["Body"], **kwargs)

            logger.info(f"Read {len(df)} records from S3: s3://{self.s3_bucket}/{key}")
            return df

        except Exception as e:
            logger.error(f"Failed to read from S3: s3://{self.s3_bucket}/{key}: {e}")
            raise

    def list_s3_files(self, prefix: Optional[str] = None) -> List[str]:
        """List CSV files in S3 bucket.

        Args:
            prefix: S3 key prefix (uses configured prefix if not provided)

        Returns:
            List of S3 keys

        Raises:
            ConnectionError: If S3 client not initialized
        """
        if not self._s3_client:
            raise ConnectionError("S3 client not initialized")

        prefix = prefix or self.s3_prefix or ""

        try:
            response = self._s3_client.list_objects_v2(
                Bucket=self.s3_bucket, Prefix=prefix
            )

            files = []
            if "Contents" in response:
                files = [
                    obj["Key"]
                    for obj in response["Contents"]
                    if obj["Key"].endswith(".csv")
                ]

            logger.info(f"Found {len(files)} CSV files in s3://{self.s3_bucket}/{prefix}")
            return files

        except Exception as e:
            logger.error(f"Failed to list S3 files: {e}")
            raise

    def read_multiple(
        self,
        file_paths: Optional[List[str]] = None,
        pattern: Optional[str] = None,
        concat: bool = True,
        **kwargs: Any,
    ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        """Read multiple CSV files.

        Args:
            file_paths: List of file paths to read
            pattern: File pattern for glob matching (local) or prefix (S3)
            concat: Whether to concatenate into single DataFrame
            **kwargs: pandas read_csv arguments

        Returns:
            Single DataFrame if concat=True, else list of DataFrames
        """
        if file_paths is None:
            if self.s3_bucket:
                # List files from S3
                file_paths = self.list_s3_files(prefix=pattern)
            elif pattern:
                # Glob local files
                from glob import glob

                file_paths = glob(pattern)
            else:
                raise ValueError("Either file_paths or pattern must be provided")

        if not file_paths:
            logger.warning("No files found to read")
            return pd.DataFrame() if concat else []

        logger.info(f"Reading {len(file_paths)} CSV files")

        # Read all files
        dataframes = []
        for file_path in file_paths:
            try:
                df = self.read(query=file_path, **kwargs)
                dataframes.append(df)
            except Exception as e:
                logger.error(f"Failed to read file '{file_path}': {e}")
                # Continue with other files

        if not dataframes:
            logger.warning("No data successfully read from files")
            return pd.DataFrame() if concat else []

        if concat:
            # Concatenate all DataFrames
            combined_df = pd.concat(dataframes, ignore_index=True)
            logger.info(f"Combined {len(dataframes)} files into {len(combined_df)} records")
            return combined_df
        else:
            return dataframes

    def write(
        self,
        df: pd.DataFrame,
        file_path: Optional[str] = None,
        s3_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Write DataFrame to CSV file.

        Args:
            df: DataFrame to write
            file_path: Local file path (if not using S3)
            s3_key: S3 object key (if using S3)
            **kwargs: pandas to_csv arguments
        """
        if self.s3_bucket:
            # Write to S3
            key = s3_key or self.s3_prefix
            if not key:
                raise ValueError("S3 key must be provided")

            try:
                import io

                # Convert DataFrame to CSV bytes
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, **kwargs)

                # Upload to S3
                self._s3_client.put_object(
                    Bucket=self.s3_bucket, Key=key, Body=csv_buffer.getvalue()
                )

                logger.info(f"Wrote {len(df)} records to S3: s3://{self.s3_bucket}/{key}")

            except Exception as e:
                logger.error(f"Failed to write to S3: {e}")
                raise

        else:
            # Write to local file
            output_path = file_path or self.file_path
            if not output_path:
                raise ValueError("File path must be provided")

            try:
                # Create directory if needed
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)

                df.to_csv(output_path, index=False, **kwargs)
                logger.info(f"Wrote {len(df)} records to file: {output_path}")

            except Exception as e:
                logger.error(f"Failed to write to file '{output_path}': {e}")
                raise

    def get_file_info(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get information about CSV file.

        Args:
            file_path: File path (uses configured path if not provided)

        Returns:
            Dictionary containing file information
        """
        path = file_path or self.file_path

        if self.s3_bucket:
            # Get S3 object metadata
            try:
                response = self._s3_client.head_object(Bucket=self.s3_bucket, Key=path)
                return {
                    "location": f"s3://{self.s3_bucket}/{path}",
                    "size_bytes": response["ContentLength"],
                    "last_modified": response["LastModified"].isoformat(),
                    "content_type": response.get("ContentType"),
                }
            except Exception as e:
                logger.error(f"Failed to get S3 object info: {e}")
                return {}
        else:
            # Get local file info
            if not os.path.exists(path):
                return {}

            stat = os.stat(path)
            return {
                "location": path,
                "size_bytes": stat.st_size,
                "last_modified": pd.Timestamp.fromtimestamp(stat.st_mtime).isoformat(),
            }
