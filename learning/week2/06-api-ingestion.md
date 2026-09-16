# REST API Ingestion: Pagination, Exponential Backoff, Rate Limits, and Fallbacks

In an enterprise data mesh, critical reference data, compliance rules, and external partner signals are accessed over HTTP via REST APIs. Ingesting over a network introduces challenges absent from local file systems: latency, transient network blips, HTTP 429 rate limiting, and downtime.

---

## 1. Network Resilience Engineering

A production API reader must never simply call `requests.get()` without resilience controls:

### A. Explicit Timeouts
By default, Python's `requests` library will block forever if the remote server fails to respond. Always set explicit connect and read timeouts:
```python
response = requests.get(url, timeout=(3.05, 10.0))  # 3.05s connect, 10s read
```

### B. Exponential Backoff with Jitter
When receiving temporary server errors (`500`, `502`, `503`, `504`) or rate limits (`429 Too Many Requests`), retrying immediately will only hammer the struggling service. 

Use **Exponential Backoff with Random Jitter**:
$$\text{delay} = 2^{\text{attempt}} + \text{uniform}(0, 1)$$

```python
import time
import random
import requests

def fetch_with_backoff(url: str, max_retries: int = 3, base_delay: float = 1.0):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code in [429, 500, 502, 503, 504]:
                sleep_time = (base_delay * (2 ** attempt)) + random.uniform(0, 0.5)
                time.sleep(sleep_time)
            else:
                resp.raise_for_status()
        except requests.RequestException:
            if attempt == max_retries - 1:
                raise
            time.sleep(base_delay * (2 ** attempt))
```

---

## 2. API Pagination Strategies

APIs return large collections in pages to conserve memory:
1. **Offset/Limit**: `GET /cases?offset=100&limit=50`
2. **Page Number**: `GET /cases?page=2&per_page=50`
3. **Cursor-Based**: `GET /cases?cursor=eyJpZCI6MTAxfQ==` (recommended for real-time systems to avoid skipped/duplicate rows when new records are added mid-pagination).

---

## 3. Production API Ingestion in Our Pipeline

In `pipeline/sources/api_source.py`, our `APISource` connects to the Week 1 FastAPI service (`GET /api/v1/mock/policies`) and provides a deterministic offline fallback:

```python
import requests
import pandas as pd
from typing import Any, Dict, List, Optional
from pipeline.sources.base_source import BaseSource

class APISource(BaseSource):
    """Production REST API Ingestion Component with Deterministic Fallback."""

    def __init__(
        self,
        endpoint_url: str,
        timeout_seconds: float = 2.0,
        fallback_data: Optional[List[Dict[str, Any]]] = None,
        source_name: str = "api_source",
    ):
        super().__init__(source_name=source_name)
        self.endpoint_url = endpoint_url
        self.timeout_seconds = timeout_seconds
        self.fallback_data = fallback_data or []

    def read(self) -> pd.DataFrame:
        try:
            resp = requests.get(self.endpoint_url, timeout=self.timeout_seconds)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict):
                    # Handle envelope { "data": [...] }
                    records = data.get("data", [data])
                    return pd.DataFrame(records)
        except Exception:
            pass  # Log warning in production

        # Fallback to local cached policy metadata if service is offline
        if self.fallback_data:
            return pd.DataFrame(self.fallback_data)

        return pd.DataFrame()
```

This guarantees pipeline runs remain deterministic during automated test suites or local offline development.
