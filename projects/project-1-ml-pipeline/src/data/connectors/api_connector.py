"""REST API connector for data ingestion."""

import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlencode

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

from src.data.connectors.base import BaseConnector
from src.utils.logger import get_logger

logger = get_logger(__name__)


class APIConnector(BaseConnector):
    """Connector for reading data from REST APIs."""

    def __init__(
        self,
        name: str = "api",
        base_url: Optional[str] = None,
        endpoint: Optional[str] = None,
        auth_type: Optional[str] = None,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.5,
        retry_on_status: Optional[List[int]] = None,
        rate_limit_delay: float = 0.0,
        **kwargs: Any,
    ):
        """Initialize API connector.

        Args:
            name: Connector name
            base_url: Base URL of the API
            endpoint: API endpoint path
            auth_type: Authentication type ('api_key', 'basic', 'bearer', None)
            api_key: API key for authentication
            username: Username for basic auth
            password: Password for basic auth
            headers: Custom HTTP headers
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff_factor: Backoff factor for retries
            retry_on_status: HTTP status codes to retry on
            rate_limit_delay: Delay between requests in seconds
            **kwargs: Additional request parameters
        """
        config = {
            "base_url": base_url,
            "endpoint": endpoint,
            "auth_type": auth_type,
            "api_key": api_key,
            "username": username,
            "timeout": timeout,
            "max_retries": max_retries,
            "retry_backoff_factor": retry_backoff_factor,
            "retry_on_status": retry_on_status or [429, 500, 502, 503, 504],
            "rate_limit_delay": rate_limit_delay,
            "headers": headers or {},
            **kwargs,
        }
        super().__init__(name=name, config=config)

        self.base_url = base_url
        self.endpoint = endpoint
        self.auth_type = auth_type
        self.api_key = api_key
        self.username = username
        self.password = password
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay

        # Session (lazy initialization)
        self._session: Optional[requests.Session] = None

        # Setup custom headers
        self.headers = headers or {}
        self._setup_auth_headers()

    def _setup_auth_headers(self) -> None:
        """Setup authentication headers based on auth type."""
        if self.auth_type == "api_key" and self.api_key:
            self.headers["X-API-Key"] = self.api_key
        elif self.auth_type == "bearer" and self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def connect(self) -> None:
        """Establish connection (create session with retry logic).

        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            # Create session
            self._session = requests.Session()

            # Setup retry strategy
            retry_strategy = Retry(
                total=self.config["max_retries"],
                backoff_factor=self.config["retry_backoff_factor"],
                status_forcelist=self.config["retry_on_status"],
                allowed_methods=["GET", "POST", "PUT", "DELETE"],
                raise_on_status=False,
            )

            adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)

            # Set headers
            self._session.headers.update(self.headers)

            # Setup authentication
            if self.auth_type == "basic" and self.username and self.password:
                self._session.auth = (self.username, self.password)

            # Test connection
            if self.base_url:
                response = self._session.get(self.base_url, timeout=self.timeout)
                response.raise_for_status()

            logger.debug(f"Connected to API: {self.name}")

        except RequestException as e:
            raise ConnectionError(f"Failed to connect to API: {e}")

    def disconnect(self) -> None:
        """Close connection."""
        if self._session:
            self._session.close()
            self._session = None
            logger.debug(f"Disconnected from API: {self.name}")

    def read(
        self,
        query: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        json_path: Optional[str] = None,
        normalize: bool = True,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Read data from API endpoint.

        Args:
            query: API endpoint path (overrides configured endpoint)
            params: Query parameters
            method: HTTP method (GET, POST, etc.)
            json_path: Path to data in JSON response (e.g., 'data.items')
            normalize: Whether to normalize nested JSON
            **kwargs: Additional request parameters

        Returns:
            DataFrame containing API response data

        Raises:
            RequestException: On API request failures
        """
        if not self._session:
            raise ConnectionError("Session not initialized")

        # Build URL
        endpoint = query or self.endpoint
        if not endpoint:
            raise ValueError("Endpoint must be provided")

        url = urljoin(self.base_url, endpoint) if self.base_url else endpoint

        # Rate limiting
        if self.rate_limit_delay > 0:
            time.sleep(self.rate_limit_delay)

        try:
            # Make request
            if method.upper() == "GET":
                response = self._session.get(url, params=params, timeout=self.timeout, **kwargs)
            elif method.upper() == "POST":
                response = self._session.post(url, json=params, timeout=self.timeout, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Extract data from nested JSON if path provided
            if json_path:
                for key in json_path.split("."):
                    data = data[key]

            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                if normalize:
                    df = pd.json_normalize(data)
                else:
                    df = pd.DataFrame([data])
            else:
                raise ValueError(f"Unexpected data type: {type(data)}")

            logger.info(f"Read {len(df)} records from API: {url}")
            return df

        except RequestException as e:
            logger.error(f"Failed to read from API '{url}': {e}")
            raise

    def read_paginated(
        self,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        page_param: str = "page",
        page_size_param: str = "page_size",
        page_size: int = 100,
        max_pages: Optional[int] = None,
        json_path: Optional[str] = None,
        total_path: Optional[str] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Read paginated data from API.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            page_param: Name of page parameter
            page_size_param: Name of page size parameter
            page_size: Number of records per page
            max_pages: Maximum number of pages to fetch
            json_path: Path to data in JSON response
            total_path: Path to total count in JSON response
            **kwargs: Additional request parameters

        Returns:
            DataFrame containing all paginated data
        """
        if params is None:
            params = {}

        all_data = []
        page = 1
        total_records = None

        logger.info(f"Starting paginated read from {endpoint or self.endpoint}")

        while True:
            # Set pagination parameters
            params[page_param] = page
            params[page_size_param] = page_size

            # Fetch page
            df = self.read(
                query=endpoint, params=params, json_path=json_path, normalize=False, **kwargs
            )

            if df.empty:
                logger.debug(f"No more data at page {page}")
                break

            all_data.append(df)

            # Check if we should continue
            if max_pages and page >= max_pages:
                logger.debug(f"Reached max pages: {max_pages}")
                break

            # Check if we have all data (if total is available)
            if total_path:
                # This would require keeping the raw response
                # Simplified: just check if we got less than page_size
                if len(df) < page_size:
                    logger.debug("Received partial page, assuming end of data")
                    break
            else:
                # If no total path, check if we got less than page_size
                if len(df) < page_size:
                    logger.debug("Received partial page, assuming end of data")
                    break

            page += 1

            # Rate limiting between pages
            if self.rate_limit_delay > 0:
                time.sleep(self.rate_limit_delay)

        if not all_data:
            logger.warning("No data retrieved from paginated API")
            return pd.DataFrame()

        # Combine all pages
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Retrieved {len(combined_df)} total records across {len(all_data)} pages")

        return combined_df

    def post(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        endpoint: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send data to API via POST.

        Args:
            data: Data to send
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            JSON response as dictionary

        Raises:
            RequestException: On API request failures
        """
        if not self._session:
            raise ConnectionError("Session not initialized")

        endpoint_path = endpoint or self.endpoint
        if not endpoint_path:
            raise ValueError("Endpoint must be provided")

        url = urljoin(self.base_url, endpoint_path) if self.base_url else endpoint_path

        try:
            response = self._session.post(url, json=data, timeout=self.timeout, **kwargs)
            response.raise_for_status()

            logger.info(f"Posted data to API: {url}")
            return response.json()

        except RequestException as e:
            logger.error(f"Failed to post to API '{url}': {e}")
            raise

    def batch_post(
        self,
        data: List[Dict[str, Any]],
        endpoint: Optional[str] = None,
        batch_size: int = 100,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Send data in batches via POST.

        Args:
            data: List of records to send
            endpoint: API endpoint path
            batch_size: Number of records per batch
            **kwargs: Additional request parameters

        Returns:
            List of JSON responses
        """
        responses = []

        logger.info(f"Posting {len(data)} records in batches of {batch_size}")

        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]

            try:
                response = self.post(data=batch, endpoint=endpoint, **kwargs)
                responses.append(response)

                logger.debug(f"Posted batch {i // batch_size + 1} ({len(batch)} records)")

                # Rate limiting between batches
                if self.rate_limit_delay > 0:
                    time.sleep(self.rate_limit_delay)

            except RequestException as e:
                logger.error(f"Failed to post batch {i // batch_size + 1}: {e}")
                # Continue with remaining batches

        logger.info(f"Completed batch posting: {len(responses)}/{(len(data) + batch_size - 1) // batch_size} batches succeeded")

        return responses

    def get_api_info(self) -> Dict[str, Any]:
        """Get API information.

        Returns:
            Dictionary containing API metadata
        """
        return {
            "base_url": self.base_url,
            "endpoint": self.endpoint,
            "auth_type": self.auth_type,
            "timeout": self.timeout,
            "max_retries": self.config["max_retries"],
            "rate_limit_delay": self.rate_limit_delay,
        }
