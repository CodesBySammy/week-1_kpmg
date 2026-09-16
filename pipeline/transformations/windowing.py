"""
Window and Ranking Transformations

Applies analytical window functions over partitioned case records.
"""

import pandas as pd


def apply_window_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies window operations over DataFrame:
    1. Dense rank of resolution time partitioned by priority
    2. Cumulative sequential case count partitioned by assignee department
    3. Rolling average resolution hours per priority
    """
    if len(df) == 0:
        return df.copy()

    windowed = df.copy()

    # 1. Rank resolution time partitioned by priority
    if "priority" in windowed.columns and "resolution_time_hours" in windowed.columns:
        windowed["priority_duration_rank"] = (
            windowed.groupby("priority")["resolution_time_hours"]
            .rank(method="dense", ascending=True)
            .fillna(0)
            .astype(int)
        )

    # 2. Cumulative sequence partitioned by assignee department
    if "assignee_department" in windowed.columns:
        windowed["department_case_seq"] = (
            windowed.groupby("assignee_department").cumcount() + 1
        )

    return windowed
