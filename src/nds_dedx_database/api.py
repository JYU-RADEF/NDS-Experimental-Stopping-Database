"""Convenience accessors for the bundled stopping power data."""

from functools import lru_cache
from pathlib import Path
from typing import cast

import pandas as pd  # type: ignore
import polars as pl

from . import utils

DATA_PATH = Path(__file__).parent / "package_data" / "latest"
DEDX_CSV = DATA_PATH / "StoppingPower.csv"
REFS_CSV = DATA_PATH / "StoppingPower_refs.csv"


@lru_cache(maxsize=1)
def _read_csv_lazy(filename: str | Path = DEDX_CSV) -> pl.LazyFrame:
    """Read bundled CSV as a lazy frame for deferred execution.

    Returns a Polars LazyFrame that does not materialize data until collect()
    is called, allowing filters to be pushed down efficiently.
    """
    if filename == DEDX_CSV.name:
        return pl.scan_csv(DATA_PATH / filename)
    elif filename == REFS_CSV.name:
        return pl.scan_csv(DATA_PATH / filename)
    else:
        raise ValueError(f"Unknown filename: {filename}")


@lru_cache(maxsize=128)
def _normalize_target(target: str | int) -> str:
    """Normalize target input. Integer -> element symbol; strings left as-is."""
    if isinstance(target, int):
        try:
            return utils.get_symbol(target)
        except Exception as exc:
            raise ValueError(f"Invalid atomic number for target: {target}") from exc

    if isinstance(target, str):
        target = target.strip()
        try:
            return utils.get_symbol(target)
        except Exception:
            pass  # Not an element symbol, return as-is
        if target.isdigit():
            return _normalize_target(int(target))
        return target


def _collection_to_pandas(collection: pl.DataFrame) -> pd.DataFrame:
    """Convert a collected lazy result into a pandas DataFrame."""
    if hasattr(collection, "to_pandas"):
        return cast(pd.DataFrame, collection.to_pandas())
    if hasattr(collection, "to_dicts"):
        return pd.DataFrame(cast(list[dict], collection.to_dicts()))
    raise TypeError("Collected data cannot be converted to pandas")


def get_data(
    ion: str | int | None = None,
    target: str | int | None = None,
    target_type: str = "any",
    copy: bool = True,
    harmonize_units: bool = True,
) -> pd.DataFrame:
    """Unified accessor for stopping power data.

    Builds a lazy filter chain and only materializes data after filtering.

    Parameters
    ----------
    ion : str|int|None
        Projectile name (symbol or full name) or atomic number. If None,
        data for all ions is returned.
    target : str|int|None
        Target name (element symbol, full name, or formula) or atomic number.
        If None, data for all targets is returned.
    target_type : {'any', 'elemental', 'compound'}
        Filter targets by type when requested.
    copy : bool
        Return a defensive copy when True (default).
    """
    if target_type not in {"any", "elemental", "compound"}:
        raise ValueError("target_type must be one of 'any', 'elemental', 'compound'")

    # Start with lazy frame (no data materialization yet)
    lazy_df = _read_csv_lazy("StoppingPower.csv")

    # Apply ion filter lazily
    if ion is not None:
        ion_sym = utils.get_symbol(ion)
        lazy_df = lazy_df.filter(pl.col("projectile_name") == ion_sym)

    # Collect and convert to pandas only after all lazy filters are defined
    # This is where the actual query execution happens
    data = _collection_to_pandas(lazy_df.collect())

    # Apply target filter in pandas after normalization.
    if target is not None:
        target_val = _normalize_target(target)
        data = data[data["target_name"] == target_val]

    # Validate results after basic filters but before target_type filtering
    if data.empty:
        if ion is not None and target is not None:
            raise ValueError(
                f"Ion-target pair ('{ion}', '{target}') not found in database."
            )
        if ion is not None:
            raise ValueError(f"Ion '{ion}' not found in database.")
        if target is not None:
            raise ValueError(f"Target '{target}' not found in database.")

    # Apply target_type filter (requires Python-based is_compound check)
    if target_type == "elemental":
        is_elemental = data["target_name"].apply(
            lambda name: not utils.is_compound(name)
        )
        data = data[is_elemental]
    elif target_type == "compound":
        is_compound_mask = data["target_name"].apply(utils.is_compound)
        data = data[is_compound_mask]

    if harmonize_units:
        data = utils.harmonize_dedx_units(data)
        data = utils.harmonize_energy_units(data)

    return data.copy(deep=True) if copy else data


def get_bundled_df(copy: bool = True) -> pd.DataFrame:
    """Return the bundled stopping power table.

    Parameters
    ----------
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.
    """

    data = _collection_to_pandas(_read_csv_lazy("StoppingPower.csv").collect())
    return data.copy(deep=True) if copy else data


def get_references(copy: bool = True) -> pd.DataFrame:
    """Return the bundled stopping power reference table."""

    data = _collection_to_pandas(_read_csv_lazy("StoppingPower_refs.csv").collect())
    return data.copy(deep=True) if copy else data


def clear_stopping_data_cache() -> None:
    """Clear the in-memory CSV cache.

    This is primarily useful for tests or when the package data has been
    swapped out in-process.
    """

    _read_csv_lazy.cache_clear()


def get_data_for_ion(
    ion: str | int, target_type: str = "any", copy: bool = True
) -> pd.DataFrame:
    """Return stopping power data for a specific projectile (ion) across all targets.

    Parameters
    ----------
    ion : str | int
        Name or atomic number of the projectile (e.g., "H", "He", "C", etc.).
    target_type : str, default "any"
        Filter targets by type when requested. Must be one of "any", "elemental", or "compound".
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.

    Returns
    -------
    pd.DataFrame
        Filtered stopping power data for the specified ion.

    Raises
    ------
    ValueError
        If the specified ion is not found in the database.

    Examples
    --------
    >>> h_stopping = get_data_for_ion("H")
    >>> he_stopping = get_data_for_ion("He")
    """
    return get_data(ion=ion, target_type=target_type, copy=copy)


def get_data_for_target(target: str | int, copy: bool = True) -> pd.DataFrame:
    """Return stopping power data for a specific target across all projectiles.

    Parameters
    ----------
    target : str | int
        Name or atomic number of the target material (e.g., "Cu", "CuO", "Al2O3", etc.).
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.

    Returns
    -------
    pd.DataFrame
        Filtered stopping power data for the specified target.

    Raises
    ------
    ValueError
        If the specified target is not found in the database.

    Examples
    --------
    >>> cu_stopping = get_data_for_target("Cu")
    >>> sio2_stopping = get_data_for_target("SiO2")
    """
    return get_data(target=target, copy=copy)


def get_data_for_ion_target(
    ion: str | int, target: str | int, copy: bool = True
) -> pd.DataFrame:
    """Return stopping power data for a specific ion-target pair.

    Parameters
    ----------
    ion : str | int
        Name or atomic number of the projectile (e.g., "H", "He", "C", etc.).
    target : str | int
        Name or atomic number of the target material (e.g., "Cu", "CuO", "Al2O3", etc.).
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.

    Returns
    -------
    pd.DataFrame
        Filtered stopping power data for the specified ion-target pair.

    Raises
    ------
    ValueError
        If the specified ion-target pair is not found in the database.

    Examples
    --------
    >>> h_in_cu = get_data_ion_target("H", "Cu")
    >>> he_in_sio2 = get_data_ion_target("He", "SiO2")
    """
    return get_data(ion=ion, target=target, copy=copy)


def get_data_elemental_targets(copy: bool = True) -> pd.DataFrame:
    """Return stopping power data for all ions in elemental targets only.

    Parameters
    ----------
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.

    Returns
    -------
    pd.DataFrame
        Stopping power data filtered to include only elemental targets.

    Examples
    --------
    >>> elemental_stopping = get_stopping_power_elemental_targets()
    """
    return get_data(target_type="elemental", copy=copy)


def get_data_compound_targets(copy: bool = True) -> pd.DataFrame:
    """Return stopping power data for all ions in compound targets only.

    Parameters
    ----------
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.

    Returns
    -------
    pd.DataFrame
        Stopping power data filtered to include only compound targets.

    Examples
    --------
    >>> compound_stopping = get_data_compound_targets()
    """
    return get_data(target_type="compound", copy=copy)


__all__ = [
    "get_bundled_df",
    "get_references",
    "clear_stopping_data_cache",
    "get_data_for_ion",
    "get_data_for_target",
    "get_data_for_ion_target",
    "get_data_elemental_targets",
    "get_data_compound_targets",
    "get_data",
]
