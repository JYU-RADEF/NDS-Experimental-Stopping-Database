"""Convenience accessors for the bundled stopping power data."""

from functools import lru_cache
from pathlib import Path

import pandas as pd  # type: ignore

from . import utils

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


def get_stopping_power_for_ion(ion: str, copy: bool = True) -> pd.DataFrame:
    """Return stopping power data for a specific projectile (ion) across all targets.

    Parameters
    ----------
    ion : str
        Name of the projectile (e.g., "H", "He", "C", etc.).
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
    >>> h_stopping = get_stopping_power_for_ion("H")
    >>> he_stopping = get_stopping_power_for_ion("He")
    """
    data = _read_csv("StoppingPower.csv")
    filtered = data[data["projectile_name"] == ion]

    if filtered.empty:
        raise ValueError(
            f"Ion '{ion}' not found in database. "
            f"Available ions: {sorted(data['projectile_name'].unique().tolist())}"
        )

    return filtered.copy(deep=True) if copy else filtered


def get_stopping_power_for_target(target: str, copy: bool = True) -> pd.DataFrame:
    """Return stopping power data for a specific target across all projectiles.

    Parameters
    ----------
    target : str
        Name of the target material (e.g., "Cu", "CuO", "Al2O3", etc.).
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
    >>> cu_stopping = get_stopping_power_for_target("Cu")
    >>> sio2_stopping = get_stopping_power_for_target("SiO2")
    """
    data = _read_csv("StoppingPower.csv")
    filtered = data[data["target_name"] == target]

    if filtered.empty:
        raise ValueError(
            f"Target '{target}' not found in database. "
            f"Available targets: {sorted(data['target_name'].unique().tolist())}"
        )

    return filtered.copy(deep=True) if copy else filtered


def get_stopping_power_for_ion_target(
    ion: str, target: str, copy: bool = True
) -> pd.DataFrame:
    """Return stopping power data for a specific ion-target pair.

    Parameters
    ----------
    ion : str
        Name of the projectile (e.g., "H", "He", "C", etc.).
    target : str
        Name of the target material (e.g., "Cu", "CuO", "Al2O3", etc.).
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
    >>> h_in_cu = get_stopping_power_for_ion_target("H", "Cu")
    >>> he_in_sio2 = get_stopping_power_for_ion_target("He", "SiO2")
    """
    data = _read_csv("StoppingPower.csv")
    filtered = data[(data["projectile_name"] == ion) & (data["target_name"] == target)]

    if filtered.empty:
        raise ValueError(
            f"Ion-target pair ('{ion}', '{target}') not found in database."
        )

    return filtered.copy(deep=True) if copy else filtered


def get_stopping_power_elemental_targets(copy: bool = True) -> pd.DataFrame:
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
    data = _read_csv("StoppingPower.csv")
    is_elemental = data["target_name"].apply(lambda name: not utils.is_compound(name))
    filtered = data[is_elemental]

    return filtered.copy(deep=True) if copy else filtered


def get_stopping_power_compound_targets(copy: bool = True) -> pd.DataFrame:
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
    >>> compound_stopping = get_stopping_power_compound_targets()
    """
    data = _read_csv("StoppingPower.csv")
    is_compound = data["target_name"].apply(utils.is_compound)
    filtered = data[is_compound]

    return filtered.copy(deep=True) if copy else filtered


def get_stopping_power_for_ion_elemental_targets(
    ion: str, copy: bool = True
) -> pd.DataFrame:
    """Return stopping power data for a specific ion in elemental targets only.

    Parameters
    ----------
    ion : str
        Name of the projectile (e.g., "H", "He", "C", etc.).
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.

    Returns
    -------
    pd.DataFrame
        Filtered stopping power data for the specified ion in elemental targets.

    Raises
    ------
    ValueError
        If the specified ion is not found in elemental targets.

    Examples
    --------
    >>> h_elemental = get_stopping_power_for_ion_elemental_targets("H")
    """
    data = _read_csv("StoppingPower.csv")
    is_elemental = data["target_name"].apply(lambda name: not utils.is_compound(name))
    filtered = data[(data["projectile_name"] == ion) & is_elemental]

    if filtered.empty:
        raise ValueError(f"Ion '{ion}' not found in elemental targets in database.")

    return filtered.copy(deep=True) if copy else filtered


def get_stopping_power_for_ion_compound_targets(
    ion: str, copy: bool = True
) -> pd.DataFrame:
    """Return stopping power data for a specific ion in compound targets only.

    Parameters
    ----------
    ion : str
        Name of the projectile (e.g., "H", "He", "C", etc.).
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.

    Returns
    -------
    pd.DataFrame
        Filtered stopping power data for the specified ion in compound targets.

    Raises
    ------
    ValueError
        If the specified ion is not found in compound targets.

    Examples
    --------
    >>> h_compound = get_stopping_power_for_ion_compound_targets("H")
    """
    data = _read_csv("StoppingPower.csv")
    is_compound = data["target_name"].apply(utils.is_compound)
    filtered = data[(data["projectile_name"] == ion) & is_compound]

    if filtered.empty:
        raise ValueError(f"Ion '{ion}' not found in compound targets in database.")

    return filtered.copy(deep=True) if copy else filtered


def get_stopping_power_elemental_targets_for_target(
    target: str, copy: bool = True
) -> pd.DataFrame:
    """Return stopping power data for a specific elemental target across all ions.

    Parameters
    ----------
    target : str
        Name of the elemental target (e.g., "Cu", "Al", "Au", etc.).
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.

    Returns
    -------
    pd.DataFrame
        Filtered stopping power data for the specified elemental target.

    Raises
    ------
    ValueError
        If the specified target is not found or is not elemental.

    Examples
    --------
    >>> cu_stopping = get_stopping_power_elemental_targets_for_target("Cu")
    """
    data = _read_csv("StoppingPower.csv")

    if utils.is_compound(target):
        raise ValueError(f"Target '{target}' is a compound, not an element.")

    filtered = data[data["target_name"] == target]

    if filtered.empty:
        raise ValueError(f"Elemental target '{target}' not found in database.")

    return filtered.copy(deep=True) if copy else filtered


def get_stopping_power_compound_targets_for_target(
    target: str, copy: bool = True
) -> pd.DataFrame:
    """Return stopping power data for a specific compound target across all ions.

    Parameters
    ----------
    target : str
        Name of the compound target (e.g., "SiO2", "Al2O3", "CuO", etc.).
    copy : bool, default True
        Return a defensive copy of the cached DataFrame. Set to False when
        you want to reuse the in-memory cached object directly.

    Returns
    -------
    pd.DataFrame
        Filtered stopping power data for the specified compound target.

    Raises
    ------
    ValueError
        If the specified target is not found or is not a compound.

    Examples
    --------
    >>> sio2_stopping = get_stopping_power_compound_targets_for_target("SiO2")
    """
    data = _read_csv("StoppingPower.csv")

    if not utils.is_compound(target):
        raise ValueError(f"Target '{target}' is not a compound.")

    filtered = data[data["target_name"] == target]

    if filtered.empty:
        raise ValueError(f"Compound target '{target}' not found in database.")

    return filtered.copy(deep=True) if copy else filtered


__all__ = [
    "get_stopping_power_data",
    "get_stopping_power_references",
    "clear_stopping_data_cache",
    "get_stopping_power_for_ion",
    "get_stopping_power_for_target",
    "get_stopping_power_for_ion_target",
    "get_stopping_power_elemental_targets",
    "get_stopping_power_compound_targets",
    "get_stopping_power_for_ion_elemental_targets",
    "get_stopping_power_for_ion_compound_targets",
    "get_stopping_power_elemental_targets_for_target",
    "get_stopping_power_compound_targets_for_target",
]
