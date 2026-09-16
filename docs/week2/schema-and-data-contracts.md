# Schema Design & Data Contracts Engine

## 1. Declarative Contract Architecture

In `pipeline/schemas/contracts.py`, `DataContract` defines the contract between producers and consumers:

```python
@dataclass
class DataContract:
    dataset_name: str
    version: str
    required_columns: List[str]
    column_types: Dict[str, str] = field(default_factory=dict)
    primary_keys: List[str] = field(default_factory=list)
    allowed_values: Dict[str, List[Any]] = field(default_factory=dict)
    nullable_columns: List[str] = field(default_factory=list)
    description: str = ""
```

---

## 2. Schema Evolution Contract Rules

1. **Required Columns Check**: Ensures all non-nullable critical columns exist in the DataFrame.
2. **Primary Key Non-Nullability**: Asserts that primary key columns contain zero nulls.
3. **Allowed Values (Enums)**: Normalizes casing and verifies values match allowed enum sets.
4. **Non-Nullable Field Check**: Checks that non-nullable columns contain neither `NaN` nor whitespace-only empty strings.
5. **Schema Evolution Tolerance**: Additive new columns (extra tags, telemetry) are safely passed through without failing validation.
