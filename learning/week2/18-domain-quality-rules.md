# Case Management Domain Quality Rules Catalog

In Week 2, our data pipeline enforces **8 explicit business domain rules** designed specifically for the Case Management System. Every rule is codified in `pipeline/validation/quality_rules.py`.

---

## 1. The 8 Automated Quality Rules

| Rule ID | Name & Description | Severity | Failure Action | Evaluator Function |
|---|---|:---:|:---:|---|
| **`RULE-CASE-001`** | **Required Title**: Case title must be non-null and non-empty. | `CRITICAL` | `QUARANTINE` | `check_required_title` |
| **`RULE-CASE-002`** | **Valid Status Enum**: Status must be `OPEN`, `IN_PROGRESS`, `RESOLVED`, or `CLOSED`. | `CRITICAL` | `QUARANTINE` | `check_valid_status` |
| **`RULE-CASE-003`** | **Valid Priority Enum**: Priority must be `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`. | `CRITICAL` | `QUARANTINE` | `check_valid_priority` |
| **`RULE-CASE-004`** | **Valid Case Type Enum**: Case type must be `BUG`, `FEATURE_REQUEST`, `INQUIRY`, or `COMPLAINT`. | `CRITICAL` | `QUARANTINE` | `check_valid_case_type` |
| **`RULE-CASE-005`** | **Positive Identifier**: Case ID must be a positive integer greater than zero. | `CRITICAL` | `QUARANTINE` | `check_positive_id` |
| **`RULE-CASE-006`** | **Creator Referential Integrity**: `created_by` must reference an existing user in reference data. | `CRITICAL` | `QUARANTINE` | `check_referential_creator` |
| **`RULE-CASE-007`** | **Assignee Referential Integrity**: If assigned, `assigned_to` must reference an existing user in reference data. | `CRITICAL` | `QUARANTINE` | `check_referential_assignee` |
| **`RULE-CASE-008`** | **Valid Timestamps**: `created_at` must be a valid parseable ISO-8601 timestamp. | `CRITICAL` | `QUARANTINE` | `check_valid_created_at` |

---

## 2. Rule Implementation Pattern

Each rule is implemented as a clean, testable callable returning `(bool, str)`:

```python
def check_required_title(row: pd.Series, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    title = row.get("title")
    if pd.isna(title) or str(title).strip() == "":
        return False, "Title is null or empty"
    return True, ""

def check_referential_creator(row: pd.Series, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    val = row.get("created_by")
    if pd.isna(val):
        return False, "created_by is null"
    try:
        creator_id = int(val)
        if context and "valid_user_ids" in context:
            if creator_id not in context["valid_user_ids"]:
                return False, f"Creator user ID {creator_id} does not exist in reference data"
    except (ValueError, TypeError):
        return False, f"created_by '{val}' is not a valid integer"
    return True, ""
```

---

## 3. How Rules Are Evaluated in the Pipeline

During Stage 5 of the pipeline run:
1. The `QualityRulesEvaluator` receives the standardized DataFrame and the context lookup sets (e.g. `{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}`).
2. Each row is tested against all 8 rules.
3. If any `CRITICAL` rule fails, the row is marked for quarantine, enriched with failure metadata (rule ID, explanation, rejection timestamp), and extracted from the clean processing stream.
4. Clean rows proceed to deduplication and curated publishing.
