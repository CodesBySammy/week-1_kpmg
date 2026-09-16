# Performance Optimization: Memory Profiling, Vectorization, and Arrow Backends

In large-scale data engineering, pipeline performance directly impacts cloud infrastructure bills, execution SLAs, and system scalability.

---

## 1. Vectorization vs Python Iteration

Python's dynamic type system incurs significant overhead during loops. Iterating over 1,000,000 rows in Python requires boxing and unboxing dynamic PyObject wrappers 1,000,000 times.

### Performance Comparison:
```python
# SLOW: 1,000,000 row loop in pure Python (~12.5 seconds)
durations = []
for row in df.itertuples():
    durations.append((row.resolved_at - row.created_at).total_seconds() / 3600.0)

# FAST: Vectorized NumPy / Pandas (~0.04 seconds — 300x FASTER!)
durations = (df["resolved_at"] - df["created_at"]).dt.total_seconds() / 3600.0
```

### Golden Rule of Data Engineering:
Never use Python loops (`for row in df...`) when a vectorized pandas, NumPy, PyArrow, or SQL operation exists.

---

## 2. Apache Arrow Backend in Pandas 2.0+

Traditionally, pandas stored string columns as Python object pointers (`dtype="object"`), consuming enormous RAM and preventing hardware SIMD vectorization.

In pandas 2.0+ and 3.0+, you can leverage the **Apache Arrow string backend**:
```python
# Traditional object strings (High RAM, slow)
df["title"] = df["title"].astype("string")

# High-performance PyArrow strings (Zero-copy, SIMD accelerated, 70% less RAM)
df["title"] = df["title"].astype("string[pyarrow]")
```

---

## 3. Projection and Predicate Pushdown

The fastest data to process is data you never read from disk.
1. **Projection Pushdown**: Read only the columns needed for downstream transformations.
   ```python
   # Instead of reading all 50 columns:
   df = pq.read_table("cases.parquet", columns=["case_id", "status", "priority"]).to_pandas()
   ```
2. **Predicate Pushdown**: Filter rows at the storage layer before reading into memory.
   ```python
   # Read only open cases directly from Parquet:
   import pyarrow.dataset as ds
   dataset = ds.dataset("cases.parquet", format="parquet")
   table = dataset.to_table(filter=ds.field("status") == "OPEN")
   ```
