"""
REST API Source Ingestion Component

Consumes dynamic compliance and policy metadata programmatically from REST endpoints.
Includes timeout controls, status code verification, and deterministic test fallback.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import requests
from pipeline.sources.base_source import BaseSource


class APISource(BaseSource):
    """Ingests records from an HTTP REST API."""

    def __init__(
        self,
        endpoint_url: str,
        params: Optional[Dict[str, Any]] = None,
        timeout_seconds: float = 5.0,
        source_name: str = "mock_rest_api",
        fallback_data: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(source_name=source_name)
        self.endpoint_url = endpoint_url
        self.params = params or {}
        self.timeout_seconds = timeout_seconds
        self.fallback_data = fallback_data

    def read(self) -> pd.DataFrame:
        try:
            response = requests.get(
                self.endpoint_url,
                params=self.params,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                return pd.DataFrame([data])
            else:
                raise ValueError(f"Unexpected JSON response structure: {type(data)}")
        except (requests.RequestException, ConnectionError) as exc:
            # If fallback data is configured (for deterministic tests without active server)
            if self.fallback_data is not None:
                return pd.DataFrame(self.fallback_data)
            raise RuntimeError(
                f"Failed to ingest from REST API endpoint {self.endpoint_url}: {exc}"
            ) from exc
