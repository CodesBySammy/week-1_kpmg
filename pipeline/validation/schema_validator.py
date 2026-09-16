"""
Schema Validation Module

Validates incoming DataFrames against declared schemas and data contracts.
"""

from typing import List, Tuple
import pandas as pd
from pipeline.schemas.contracts import DataContract


class SchemaValidator:
    """Validates structural schema compliance of ingested datasets."""

    def __init__(self, contract: DataContract):
        self.contract = contract

    def validate(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validates DataFrame against assigned DataContract."""
        return self.contract.validate(df)
