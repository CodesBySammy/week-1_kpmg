# Data Formats Deep Dive: CSV Internals, Pitfalls, and Chunked Ingestion

Comma-Separated Values (**CSV**) remains the most ubiquitous data interchange format in enterprise computing. However, because CSV lacks a standardized binary specification or embedded schema, it is also the most error-prone format in production data pipelines.

---

## 1. CSV Internals & RFC 4180 Standard

The closest standard for CSV is **IETF RFC 4180**:
- Records are separated by line breaks (`CRLF` or `LF`).
- Fields are delimited by commas `,`.
- Fields containing commas, line breaks, or quotation marks must be enclosed in double quotes `"..."`.
- An embedded double quote within a quoted field is escaped by prefixing it with another double quote `""`.

### Common Ingestion Traps in Production

1. **Embedded Delimiters in Text**:
   ```csv
   case_id,title,description
   101,Database timeout,Error occurred on node-1, retried 3 times
   ```
   *Failure*: The unquoted comma in `node-1, retried` shifts subsequent fields, turning a 3-column row into a 4-column row!
   *Fix*: Producers must properly quote text fields: `"Error occurred on node-1, retried 3 times"`.

2. **Embedded Line Breaks**:
   Log messages and user comments often contain `\n` or `\r\n`. Without multiline CSV parser flags, single records are split across multiple erroneous rows.

3. **Leading Zeros in Identifiers**:
   Zip codes (`01234`) or account numbers (`004829`) read as numeric integers lose their leading zeros (`1234`, `4829`).
   *Fix*: Explicitly specify `dtype={"account_number": str}` during ingestion.

4. **Mixed Date/Time Formats**:
   Dates written as `03/04/2026` could mean March 4th (US format) or April 3rd (European/UK format). Always enforce ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`).

---

## 2. Chunked Ingestion for Large Files

Reading a 10 GB CSV into memory with `pd.read_csv()` will crash a 16 GB server with an `OutOfMemoryError` (OOM) because pandas DataFrames typically require 3x to 5x the raw file size in RAM.

To process files larger than available RAM safely, ingest in **chunks**:

```python
import pandas as pd
from typing import Iterator

def stream_csv_chunks(file_path: str, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
    """Streams a large CSV file in bounded chunks to prevent OOM."""
    for chunk in pd.read_csv(
        file_path,
        chunksize=chunk_size,
        dtype=str,  # Ingest raw as strings to avoid premature type inference
        keep_default_na=False,  # Treat empty strings explicitly
    ):
        yield chunk
```

---

## 3. Production CSV Ingestion Architecture in Our Pipeline

In `pipeline/sources/csv_source.py`, we implement `CSVSource` derived from `BaseSource`:

```python
from pathlib import Path
import pandas as pd
from pipeline.sources.base_source import BaseSource

class CSVSource(BaseSource):
    """Production-grade CSV Source Ingestion Component."""

    def __init__(self, file_path: Path, delimiter: str = ",", source_name: str = "csv_source"):
        super().__init__(source_name=source_name)
        self.file_path = Path(file_path)
        self.delimiter = delimiter

    def read(self) -> pd.DataFrame:
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV source file does not exist: {self.file_path}")

        try:
            # Enforce raw string ingestion so validation and standardization can audit defects
            df = pd.read_csv(
                self.file_path,
                sep=self.delimiter,
                dtype=str,
                encoding="utf-8",
                on_bad_lines="error",  # Fail-stop if row column count is corrupted
            )
            return df
        except Exception as exc:
            raise RuntimeError(f"Failed to read CSV source at {self.file_path}: {exc}") from exc
```

### Key Engineering Practices:
- Ingest raw data as `dtype=str` initially. Never let an automatic parser silently coerce corrupted data into `NaN` or incorrect integers.
- Pass raw strings into the **Data Profiler** and **Data Quality Engine** to inspect and quarantine defective inputs before type transformation.
