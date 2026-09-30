# LAB-07: Performance Benchmarking & Latency Profiling

## 1. Objective
Measure p50, p95, and p99 latencies across API, RAG, and workflow components.

## 2. Prerequisites
Python `time.perf_counter()`, pytest benchmarking fixtures.

## 3. Practical Task
Execute benchmark tests and evaluate measured results against production SLAs.

## 4. Step-by-Step Instructions
1. Run `pytest tests/performance/test_performance_benchmarks.py -v -s`.
2. Review recorded latencies in `docs/week5/testing/PERFORMANCE_BENCHMARKS.md`.
3. Compare measured p95 values against target SLAs.

## 5. Expected Result
Benchmark outputs showing API < 5ms, hybrid search < 10ms, workflow < 20ms.

## 6. Verification & Automated Validation
Run `pytest tests/performance/test_performance_benchmarks.py`.

## 7. Challenge Questions
Why might p99 latency spike significantly higher than p50 in a garbage-collected language?
