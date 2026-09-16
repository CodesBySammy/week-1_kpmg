# Lab 07: Enforcing Data Contracts & Detecting Producer Schema Drift

## Objective
Define a declarative `DataContract`, validate incoming DataFrames against it, and verify that breaking contract changes are flagged.

---

## Exercise

1. Instantiate a contract and test validation:
```python
import pandas as pd
from pipeline.schemas.contracts import DataContract
from pipeline.validation.schema_validator import SchemaValidator

contract = DataContract(
    dataset_name="cases",
    version="1.0.0",
    required_columns=["case_id", "title", "status"],
    primary_keys=["case_id"],
    allowed_values={"status": ["OPEN", "CLOSED"]},
)

validator = SchemaValidator(contract)

# Case 1: Valid Data
valid_df = pd.DataFrame([
    {"case_id": 1, "title": "Crash on login", "status": "OPEN"}
])
is_valid, violations = validator.validate(valid_df)
print("Valid DF passed?", is_valid, violations)

# Case 2: Upstream producer dropped required column 'title'
corrupted_df = pd.DataFrame([
    {"case_id": 2, "status": "OPEN"}
])
is_valid, violations = validator.validate(corrupted_df)
print("Corrupted DF passed?", is_valid, violations)
```

---

## Verification
- Assert that `corrupted_df` fails with violation: `"Missing required contract column: 'title'"`.
