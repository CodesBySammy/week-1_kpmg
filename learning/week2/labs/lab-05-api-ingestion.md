# Lab 05: REST API Ingestion with Timeouts and Deterministic Fallback

## Objective
Ingest reference policy rules from an HTTP REST endpoint with timeout protection and offline cache fallback.

---

## Exercise

1. Test API ingestion against mock endpoint with fallback:
```python
from pipeline.sources.api_source import APISource

mock_url = "http://127.0.0.1:8000/api/v1/mock/policies"
cached_fallback = [
    {"policy_id": "FALLBACK-01", "case_type": "BUG", "priority": "CRITICAL", "sla_hours": 2.0}
]

# Case A: Online / Fallback behavior
source = APISource(
    endpoint_url=mock_url,
    timeout_seconds=1.0,
    fallback_data=cached_fallback,
    source_name="lab_api",
)

df = source.read()
print(f"API Source returned {len(df)} records")
print(df.head())

# Case B: Unreachable endpoint triggers graceful fallback
bad_source = APISource(
    endpoint_url="http://127.0.0.1:59999/unreachable",
    timeout_seconds=0.2,
    fallback_data=cached_fallback,
)
fallback_df = bad_source.read()
print(f"Fallback safely returned {len(fallback_df)} cached records without crashing!")
```

---

## Verification
- Confirm that the pipeline does not raise an unhandled exception when an API endpoint is unreachable.
