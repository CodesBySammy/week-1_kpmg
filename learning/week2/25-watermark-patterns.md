# Watermark Patterns: High-Watermark State Management and Late-Arriving Data

In distributed data pipelines, tracking the "high-watermark" requires careful architecture to handle state persistence, late-arriving data, clock skew, and rerun recovery.

---

## 1. High-Watermark State Storage

The watermark state must be stored in a durable, ACID-compliant medium (e.g., a metadata database, an S3/GCS state file, or a local JSON audit store).

In `pipeline/orchestration/incremental.py`, our `WatermarkTracker` persists state to `audit/watermark.json`:

```json
{
  "high_watermark": "2026-03-01T12:00:00+00:00",
  "updated_at": "2026-09-16T12:05:00.123456+00:00",
  "last_batch_id": "BATCH_20260916_1205"
}
```

```python
class WatermarkTracker:
    def __init__(self, watermark_path: Path):
        self.watermark_path = Path(watermark_path)

    def get_watermark(self) -> Optional[datetime]:
        if not self.watermark_path.exists():
            return None
        with open(self.watermark_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return datetime.fromisoformat(data["high_watermark"])

    def update_watermark(self, new_watermark: datetime, batch_id: str) -> None:
        payload = {
            "high_watermark": new_watermark.isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_batch_id": batch_id,
        }
        with open(self.watermark_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
```

---

## 2. Handling Late-Arriving Data: Sliding Lookback Windows

In real-world networks, mobile devices or microservices may be offline when an update occurs. When they reconnect hours later, they upload records whose `updated_at` timestamp is **older than the current high-watermark**!

If your query is strictly:
```sql
WHERE updated_at > :high_watermark
```
That late-arriving record will be **silently ignored forever**!

### The Sliding Lookback Window Solution:
Subtract a safety buffer (e.g. 1 hour or 24 hours) from the watermark when querying:
```python
lookback_buffer = timedelta(hours=2)
query_watermark = current_watermark - lookback_buffer
```
```sql
WHERE updated_at > :query_watermark
```
Because querying with a lookback window introduces overlapping records, the pipeline's **Deduplication Stage** automatically deduplicates the overlapping records, keeping the freshest state.

---

## 3. Watermark Commit Semantics: Two-Phase Commit

Crucially, the watermark must **never** be updated at the beginning of a run. It must only be committed at the very end of the pipeline execution after:
1. All records have successfully landed in the Curated Layer.
2. Source-to-Target Reconciliation has verified zero data leakage (`status == 'PASS'`).
3. The Audit Manifest has been written.
