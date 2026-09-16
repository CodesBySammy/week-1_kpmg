# Pipeline Operational Runbook & Production Maintenance Guide

## 1. Daily Operations & CLI Execution

### Running the Full Pipeline:
```bash
python -m pipeline.cli --mode full
```

### Running an Incremental Delta Pipeline:
```bash
python -m pipeline.cli --mode incremental
```

### Running with a Specific Input File:
```bash
python -m pipeline.cli --mode full --file data/test_inputs/malformed_cases.csv
```

---

## 2. Docker Containerized Execution

### Building the Image:
```bash
docker build -t case-management-pipeline:1.0.0 .
```

### Running Container with Host Volume Mounts:
```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/audit:/app/audit \
  case-management-pipeline:1.0.0 \
  --mode full
```

---

## 3. SLA & Operational Monitoring Thresholds

| Metric | Normal Range | Warning Threshold | Critical Incident |
|---|:---:|:---:|:---:|
| **Reconciliation Status** | `PASS` (0 variance) | N/A | `FAIL` (Non-zero variance) |
| **Quarantine Rate** | $< 2\%$ | $\ge 5\%$ | $\ge 10\%$ (Circuit Breaker) |
| **Full Run Runtime** | $< 2.0$ seconds | $> 5.0$ seconds | $> 15.0$ seconds |
| **Data Freshness** | $< 24$ hours | $> 36$ hours | $> 48$ hours |
