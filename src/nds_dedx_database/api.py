"""Convenience accessors for the bundled stopping power data."""

from functools import lru_cache
from pathlib import Path

import pandas as pd  # type: ignore

DATA_PATH = Path(__file__).parent / "package_data" / "latest"


@lru_cache(maxsize=1)
def _read_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(DATA_PATH / filename, low_memory=False)


def get_stopping_power_data(copy: bool = True) -> pd.DataFrame:
    """Return the bundled stopping power table.

    Parameters
    ----------
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.
    """

    data = _read_csv("StoppingPower.csv")
    return data.copy(deep=True) if copy else data


def get_stopping_power_references(copy: bool = True) -> pd.DataFrame:
    """Return the bundled stopping power reference table."""

    data = _read_csv("StoppingPower_refs.csv")
    return data.copy(deep=True) if copy else data


def clear_stopping_data_cache() -> None:
    """Clear the in-memory CSV cache.

    This is primarily useful for tests or when the package data has been
    swapped out in-process.
    """

    _read_csv.cache_clear()


__all__ = [
    "get_stopping_power_data",
    "get_stopping_power_references",
    "clear_stopping_data_cache",
]
