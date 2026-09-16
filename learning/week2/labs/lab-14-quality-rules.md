# Lab 14: Implementing & Evaluating Automated Data Quality Rules

## Objective
Evaluate custom data quality rules against incoming case records and separate valid rows from rejected records.

---

## Exercise

1. Execute `QualityRulesEvaluator`:
```python
import pandas as pd
from pipeline.validation.quality_rules import CASE_QUALITY_RULES, QualityRulesEvaluator

evaluator = QualityRulesEvaluator(
    rules=CASE_QUALITY_RULES,
    context={"valid_user_ids": {1, 2, 3, 4, 5}}
)

batch_df = pd.DataFrame([
    # Valid
    {"case_id": 10, "title": "Database slow", "status": "OPEN", "priority": "HIGH", "case_type": "BUG", "created_by": 1, "created_at": "2026-03-01T10:00:00Z"},
    # Invalid: empty title
    {"case_id": 11, "title": "   ", "status": "OPEN", "priority": "HIGH", "case_type": "BUG", "created_by": 1, "created_at": "2026-03-01T10:00:00Z"},
    # Invalid: non-existent creator
    {"case_id": 12, "title": "Valid title", "status": "OPEN", "priority": "HIGH", "case_type": "BUG", "created_by": 999, "created_at": "2026-03-01T10:00:00Z"},
])

valid_df, rejected = evaluator.evaluate(batch_df, run_id="LAB_14", source_name="lab_cases")

print(f"Valid count: {len(valid_df)}")
print(f"Rejected count: {len(rejected)}")
for r in rejected:
    print(f"  Failed Rule: {r['rule_id']} -> {r['reason']}")
```

---

## Verification
- Confirm 1 row passed and 2 rows were rejected with explicit rule IDs (`RULE-CASE-001` and `RULE-CASE-006`).
