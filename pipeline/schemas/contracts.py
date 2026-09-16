"""
Data Contract Definition and Enforcement Engine

Implements formal Data Contracts between producers and consumers.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd


@dataclass
class DataContract:
    """Formal contract specifying schema, constraints, and semantics for a dataset."""
    
    dataset_name: str
    version: str
    required_columns: List[str]
    column_types: Dict[str, str] = field(default_factory=dict)
    primary_keys: List[str] = field(default_factory=list)
    allowed_values: Dict[str, List[Any]] = field(default_factory=dict)
    nullable_columns: List[str] = field(default_factory=list)
    description: str = ""

    def validate(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validates whether a given DataFrame fulfills this data contract.
        Returns (is_valid, list_of_violations).
        """
        violations: List[str] = []

        # 1. Check for missing required columns
        for col in self.required_columns:
            if col not in df.columns:
                violations.append(f"Missing required contract column: '{col}'")

        if violations:
            return False, violations

        # 2. Check primary key non-nullability
        for pk in self.primary_keys:
            if pk in df.columns and df[pk].isna().any():
                violations.append(f"Primary key column '{pk}' contains null values")

        # 3. Check allowed values (enums)
        for col, allowed in self.allowed_values.items():
            if col in df.columns:
                non_null_series = df[col].dropna().astype(str).str.strip().str.upper()
                invalid_mask = ~non_null_series.isin([str(v).upper() for v in allowed])
                invalid_count = invalid_mask.sum()
                if invalid_count > 0:
                    invalid_samples = non_null_series[invalid_mask].unique()[:3]
                    violations.append(
                        f"Column '{col}' has {invalid_count} records violating allowed values: {invalid_samples}"
                    )

        # 4. Check non-nullable columns
        for col in self.required_columns:
            if col not in self.nullable_columns and col in df.columns:
                null_count = int(df[col].isna().sum())
                # Also treat whitespace-only strings as null
                str_series = df[col].dropna().astype(str).str.strip()
                empty_str_count = int((str_series == "").sum())
                total_invalid = null_count + empty_str_count
                if total_invalid > 0:
                    violations.append(
                        f"Non-nullable column '{col}' contains {total_invalid} null/empty values"
                    )

        return len(violations) == 0, violations
