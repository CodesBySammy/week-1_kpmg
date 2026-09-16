"""
Deduplication Transformations

Implements deterministic primary key deduplication preserving latest update state.
"""

from typing import List, Tuple
import pandas as pd


def deduplicate_cases(
    df: pd.DataFrame,
    primary_key: str = "case_id",
    order_by_col: str = "updated_at",
) -> Tuple[pd.DataFrame, int]:
    """
    Deduplicates a case DataFrame based on primary key.
    When duplicate keys exist, keeps the record with the most recent updated_at timestamp.
    Returns:
        (deduplicated_df, duplicate_count)
    """
    initial_count = len(df)
    if initial_count == 0:
        return df.copy(), 0

    if primary_key not in df.columns:
        return df.copy(), 0

    # Sort so latest updated_at comes last
    if order_by_col in df.columns:
        sorted_df = df.sort_values(by=[primary_key, order_by_col], ascending=[True, True])
    else:
        sorted_df = df

    deduped = sorted_df.drop_duplicates(subset=[primary_key], keep="last").copy()
    deduped.reset_index(drop=True, inplace=True)

    duplicates_removed = initial_count - len(deduped)
    return deduped, duplicates_removed
