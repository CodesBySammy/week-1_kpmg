# Data Profiling Report: CASES
**Run ID:** `RUN_20260916_062855`  
**Profiled At:** 2026-09-16T06:28:58.160514+00:00  
**Total Records:** 20 | **Columns:** 11  

---

## 1. Completeness Metrics (Null Analysis)
| Column | Missing Count | Missing % | Present Count | Present % |
|---|---|---|---|---|
| `case_id` | 0 | 0.0% | 20 | 100.0% |
| `title` | 1 | 5.0% | 19 | 95.0% |
| `description` | 0 | 0.0% | 20 | 100.0% |
| `status` | 0 | 0.0% | 20 | 100.0% |
| `priority` | 0 | 0.0% | 20 | 100.0% |
| `case_type` | 0 | 0.0% | 20 | 100.0% |
| `created_by` | 0 | 0.0% | 20 | 100.0% |
| `assigned_to` | 0 | 0.0% | 20 | 100.0% |
| `created_at` | 0 | 0.0% | 20 | 100.0% |
| `updated_at` | 0 | 0.0% | 20 | 100.0% |
| `resolved_at` | 14 | 70.0% | 6 | 30.0% |

---

## 2. Uniqueness Metrics
- **case_id:** `{'unique_count': 19, 'duplicate_count': 1, 'uniqueness_ratio': 0.95}`
- **full_row_duplicates:** `0`

---

## 3. Validity Metrics
### Column: `status`
- valid_count: `19`
- invalid_count: `1`
- invalid_samples: `['PENDING_APPROVAL']`
### Column: `priority`
- valid_count: `19`
- invalid_count: `1`
- invalid_samples: `['URGENT']`
### Column: `case_type`
- valid_count: `20`
- invalid_count: `0`
- invalid_samples: `[]`
### Column: `numeric_case_id`
- negative_count: `1`
- non_numeric_count: `0`

---

## 4. Categorical Distributions
### Distribution of `status`:
- **OPEN**: 9
- **IN_PROGRESS**: 4
- **RESOLVED**: 4
- **CLOSED**: 2
- **PENDING_APPROVAL**: 1
### Distribution of `priority`:
- **HIGH**: 7
- **LOW**: 5
- **CRITICAL**: 4
- **MEDIUM**: 3
- **URGENT**: 1
### Distribution of `case_type`:
- **BUG**: 10
- **FEATURE_REQUEST**: 5
- **INQUIRY**: 3
- **COMPLAINT**: 2

---

## 5. Referential Integrity
- **created_by**: 0 orphan records found (samples: `[]`)
- **assigned_to**: 1 orphan records found (samples: `[np.int64(999)]`)