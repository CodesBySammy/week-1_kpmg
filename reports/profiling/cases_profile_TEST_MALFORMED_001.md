# Data Profiling Report: CASES
**Run ID:** `TEST_MALFORMED_001`  
**Profiled At:** 2026-09-16T06:29:12.952537+00:00  
**Total Records:** 10 | **Columns:** 11  

---

## 1. Completeness Metrics (Null Analysis)
| Column | Missing Count | Missing % | Present Count | Present % |
|---|---|---|---|---|
| `case_id` | 0 | 0.0% | 10 | 100.0% |
| `title` | 1 | 10.0% | 9 | 90.0% |
| `description` | 0 | 0.0% | 10 | 100.0% |
| `status` | 0 | 0.0% | 10 | 100.0% |
| `priority` | 0 | 0.0% | 10 | 100.0% |
| `case_type` | 0 | 0.0% | 10 | 100.0% |
| `created_by` | 0 | 0.0% | 10 | 100.0% |
| `assigned_to` | 0 | 0.0% | 10 | 100.0% |
| `created_at` | 0 | 0.0% | 10 | 100.0% |
| `updated_at` | 0 | 0.0% | 10 | 100.0% |
| `resolved_at` | 10 | 100.0% | 0 | 0.0% |

---

## 2. Uniqueness Metrics
- **case_id:** `{'unique_count': 9, 'duplicate_count': 1, 'uniqueness_ratio': 0.9}`
- **full_row_duplicates:** `0`

---

## 3. Validity Metrics
### Column: `status`
- valid_count: `9`
- invalid_count: `1`
- invalid_samples: `['INVALID_STATUS_XYZ']`
### Column: `priority`
- valid_count: `9`
- invalid_count: `1`
- invalid_samples: `['SUPER_URGENT']`
### Column: `case_type`
- valid_count: `9`
- invalid_count: `1`
- invalid_samples: `['UNSUPPORTED_TYPE']`
### Column: `numeric_case_id`
- negative_count: `1`
- non_numeric_count: `0`

---

## 4. Categorical Distributions
### Distribution of `status`:
- **OPEN**: 9
- **INVALID_STATUS_XYZ**: 1
### Distribution of `priority`:
- **LOW**: 6
- **HIGH**: 2
- **MEDIUM**: 1
- **SUPER_URGENT**: 1
### Distribution of `case_type`:
- **BUG**: 6
- **INQUIRY**: 3
- **UNSUPPORTED_TYPE**: 1

---

## 5. Referential Integrity
- **created_by**: 1 orphan records found (samples: `[np.int64(8888)]`)
- **assigned_to**: 1 orphan records found (samples: `[np.int64(9999)]`)