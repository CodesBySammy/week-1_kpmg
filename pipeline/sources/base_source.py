"""
Base Source Ingestion Abstraction

Defines the contract that all heterogeneous data source readers must implement.
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseSource(ABC):
    """Abstract Base Class for heterogeneous source ingestion."""

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """
        Ingests data from the source and returns a Pandas DataFrame.
        Must raise an appropriate exception if ingestion fails.
        """
        pass
