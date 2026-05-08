# Utility functions for harmonizing the data

import logging
from functools import lru_cache
from typing import Callable, Optional, cast

import pandas as pd  # type: ignore
import periodictable as pt  # type: ignore
from periodictable.formulas import parse_formula  # type: ignore
from pyparsing import ParseException

logger = logging.getLogger(__name__)


@lru_cache(maxsize=128)
def get_symbol(value: str | int) -> str:
    """Get element symbol from the Periodic Table module.

    Parameters
    ----------
    value : str | int
        Name of the element (e.g., "Copper" or "cu") or atomic number.

    Returns
    -------
    str
        Symbol of the element (e.g., "Cu").

    """
    if isinstance(value, int):
        try:
            elem = pt.elements[value]
            return elem.symbol
        except Exception as exc:
            raise ValueError(f"Invalid atomic number for element: {value}") from exc

    name = value.strip()

    if len(name) <= 2:
        element = getattr(pt, name.capitalize(), None)
    elif len(name) > 2:
        element = getattr(pt, name.lower(), None)
    else:
        raise ValueError(f"Invalid element name: {value}")

    if element is not None and isinstance(element, pt.core.Element):
        return element.symbol
    else:
        raise ValueError(f"Element '{value}' not found in the periodic table.")


@lru_cache(maxsize=128)
def detect_material_type(name: str):
    """Detect if the name corresponds to an element or a compound.

    Parameters
    ----------
    name : str
        Name of the material.

    Returns
    -------
    str
        "element" if the name corresponds to an element, "compound" if it corresponds to a compound, "unknown" otherwise.
    """

    name = name.strip()

    # Check if found as an element in the periodic table
    try:
        get_symbol(name)
        return "element"
    except ValueError:
        pass

    # Try parsing as a chemical formula
    try:
        formula = parse_formula(name)
        elements = list(formula.atoms)
        if len(elements) == 1 and not any(v > 1 for v in formula.atoms.values()):
            return "element"
        elif len(elements) > 1 or any(v > 1 for v in formula.atoms.values()):
            return "compound"
    except (ParseException, ValueError):
        pass  # Not a valid chemical formula

    return "unknown"


@lru_cache(maxsize=128)
def is_element_in_periodic_table(name: str) -> bool:
    """Check if the element is in the Periodic Table module.

    Parameters
    ----------
    name : str
        Name of the element, either as a symbol (e.g., "Cu") or full name (e.g., "copper").

    Returns
    -------
    bool
        True if the element is in the Periodic Table, False otherwise.

    Examples
    --------
    >>> is_element_in_periodic_table("Cu")
    True
    >>> is_element_in_periodic_table("cu")
    True
    >>> is_element_in_periodic_table("copper")
    True
    >>> is_element_in_periodic_table("xyz")
    False
    >>> is_element_in_periodic_table("TiN")
    False
    """
    # Try as a properly capitalized symbol (first letter capital, rest lowercase)
    if "element" in detect_material_type(name):
        return True
    else:
        return False


@lru_cache(maxsize=128)
def is_compound(name: str) -> bool:
    """Check if the name is a compound.

    Parameters
    ----------
    name : str
        Name of the element or compound.

    Returns
    -------
    bool
        True if the name is a compound, False otherwise.

    Examples
    --------
    >>> is_compound("Cu")
    False
    >>> is_compound("CuO")
    True
    >>> is_compound("H2O")
    True
    >>> is_compound("NaCl")
    True
    >>> is_compound("O2")
    True
    >>> is_compound("TiN")
    True
    >>> is_compound("He")
    False
    >>> is_compound("Copper")
    False
    >>> is_compound("hydrogen")
    False
    """

    if "compound" in detect_material_type(name):
        return True
    else:
        return False


@lru_cache(maxsize=128)
def get_element_mass(name: str, isotope: float) -> float:
    """Get element mass from the Periodic Table module.

    Given isotope mass is translated to the closest mass value in the
    Periodic Table module. The function uses the name of the element
    and the isotope number to find the corresponding mass.

    Parameters
    ----------
    name : str
        Name of the element (e.g., "Cu").
    isotope : float
        Isotope number (e.g., 63.546).

    Returns
    -------
    float
        Mass of the element in atomic mass units (amu).

    """
    isotopes = getattr(pt, name).isotopes
    masses = [getattr(pt, name)[x] for x in isotopes]

    closest = min(masses, key=lambda x: abs(x.mass - isotope))

    return closest.mass


@lru_cache(maxsize=128)
def get_element_density(name: str, isotope: Optional[float] = None) -> float:
    """Get element density from the Periodic Table module.

    Parameters
    ----------
    name : str
        Name of the element (e.g., "Cu").
    isotope : float, optional
        Isotope number (e.g., 63.546).

    Returns
    -------
    float
        Density of the element in g/cm3.

    """
    name_ = name
    try:
        options = [getattr(pt, name)[x] for x in getattr(pt, name).isotopes]
    except AttributeError:
        try:
            logger.debug(
                f"Trying to get isotopes for element '{name_}' by lowercase name."
            )
            name = name.lower()
            options = [getattr(pt, name)[x] for x in getattr(pt, name).isotopes]
        except AttributeError:
            raise ValueError(f"Element '{name_}' not found in the periodic table.")

    if isotope is not None:
        closest = min(options, key=lambda x: abs(x.mass - isotope))
        try:
            return closest.density
        except TypeError:
            logger.warning(
                f"Could not calculate density for isotope of {name_} with mass {isotope}. "
                f"Falling back to natural element density."
            )
            return getattr(pt, name).density
    else:
        return getattr(pt, name).density


@lru_cache(maxsize=128)
def convert_energy(
    value: float, mass: float, from_unit: str, to_unit: str = "MeV/u"
) -> tuple[float, str]:

    new_unit = to_unit

    if from_unit[0] == to_unit[0]:
        new_value = value
    elif from_unit[0] == "M" and to_unit[0] == "k":
        new_value = value * 1000
    elif from_unit[0] == "k" and to_unit[0] == "M":
        new_value = value / 1000
    else:
        raise ValueError(f"Unknown energy units: {from_unit} to {to_unit}")

    if "/u" in from_unit and "/u" in to_unit:
        return new_value, new_unit
    elif "/u" in from_unit and "/u" not in to_unit:
        new_value = new_value * mass
        return new_value, to_unit
    elif "/u" not in from_unit and "/u" in to_unit:
        new_value = new_value / mass
        return new_value, to_unit
    elif "/u" not in from_unit and "/u" not in to_unit:
        return new_value, to_unit
    else:
        raise ValueError(f"Unknown energy units: {from_unit} to {to_unit}")


@lru_cache(maxsize=128)
def convert_dedx(
    value: float,
    target_mass: Optional[float],
    target_rho: Optional[float],
    from_unit: str,
    to_unit: str = "MeV/mg/cm2",
) -> tuple[float, str]:
    """Convert dE/dx values between different units.

    Possible units are:
        - `MeV/(mg/cm2)`
        - `E-15eV cm2/atom`
        - `eV/A`
        - `eV/(mg/cm2)`

    Unit conversions are defined in "Stopping of Heavy Ions - A Theoretical Approach" by P. Sigmund. The conversions are:

    - `MeV/(mg/cm2)` to `E-15eV cm2/atom`: multiply by 1.6605 * A2
    - `E-15eV cm2/atom` to `MeV/(mg/cm2)`: divide by 1.6605 * A2

    Parameters
    ----------
    value : float
        The value to convert.
    target_mass : Optional[float]
        The mass of the target element in atomic mass units (amu).
    target_rho : Optional[float]
        The density of the target material in g/cm3. Required for conversions involving `eV/Å`.
    from_unit : str
        The unit of the input value.
    to_unit : str
        The unit to convert to.

    Returns
    -------
    float, str
        The converted value and the new unit.

    """

    if from_unit == to_unit:
        return value, to_unit

    if target_mass is None and any(
        "E-15eV cm2/atom" in unit for unit in (from_unit, to_unit)
    ):
        raise ValueError(
            "target_mass must be provided for conversions involving E-15eV cm2/atom."
        )
    if target_rho is None and any("eV/A" in unit for unit in (from_unit, to_unit)):
        raise ValueError("target_rho must be provided for conversions involving eV/A.")

    mass = cast(float, target_mass)
    rho = cast(float, target_rho)

    _DEDX_CONVERSIONS: dict[tuple[str, str], Callable[[float, float, float], float]] = {
        ("E-15eV cm2/atom", "MeV/(mg/cm2)"): lambda v, A, *_: v / (1.6605 * A),
        ("MeV/(mg/cm2)", "E-15eV cm2/atom"): lambda v, A, *_: v * 1.6605 * A,
        ("eV/(mg/cm2)", "MeV/(mg/cm2)"): lambda v, *_: v * 1e-6,
        ("eV/A", "MeV/(mg/cm2)"): lambda v, _, rho: v / (1e3 * rho) * 1e8 * 1e-6,
        ("MeV/(mg/cm2)", "eV/A"): lambda v, _, rho: v * (1e3 * rho) / 1e8 / 1e-6,
    }

    try:
        return _DEDX_CONVERSIONS[(from_unit, to_unit)](value, mass, rho), to_unit
    except KeyError:
        raise ValueError(f"Conversion from {from_unit} to {to_unit} not supported.")


def harmonize_energy_units(df: pd.DataFrame, to: str = "MeV/u") -> pd.DataFrame:
    """
    Harmonizes the energy units in the DataFrame. The possible values for energy units are:
    'MeV/u', 'keV/u', 'keV', 'MeV'.
    The function converts all energy values to the specified unit.
    The default is 'MeV/u'.

    """

    df = df.copy()

    ion_mass = df[["projectile_name", "ion_isotope"]].apply(
        lambda x: get_element_mass(x["projectile_name"], x["ion_isotope"]), axis=1
    )
    df["ion_mass"] = ion_mass
    df["target_mass"] = df["target_mass_atom_ratio"]

    df["energy"], df["energy_unit"] = zip(
        *df.apply(
            lambda x: convert_energy(
                x["energy"],
                x["ion_mass"],
                x["energy_unit"],
                to,
            ),
            axis=1,
        )
    )
    return df


def harmonize_dedx_units(df: pd.DataFrame, to: str = "MeV/(mg/cm2)") -> pd.DataFrame:
    """
    Harmonizes the dE/dx units in the DataFrame. The possible values for dE/dx units are:
    'MeV/(mg/cm2)', 'E-15eV cm2/atom', 'eV/Å', 'eV/(mg/cm2)'.
    The function converts all dE/dx values to the specified unit.
    The default is 'MeV/(mg/cm2)'.

    NOTE: This function only works for elemental targets.

    """

    df_ = df.copy()
    df_ = df_[df_["target_name"].apply(is_element_in_periodic_table)].reset_index(
        drop=True
    )

    df_["target_name"] = df_["target_name"].apply(get_symbol)

    if df_.shape[0] != df.shape[0]:
        logger.warning(
            "Some rows were removed in harmonize_dedx_units because they contain non-elemental targets."
        )

    target_densities = df_[["target_name", "target_mass"]].apply(
        lambda x: get_element_density(x["target_name"], x["target_mass"]), axis=1
    )
    df_["target_rho"] = target_densities

    df_["stopping_power"], df_["stopping_unit"] = zip(
        *df_.apply(
            lambda x: convert_dedx(
                x["stopping_power"],
                x["target_mass"],
                x["target_rho"],
                x["stopping_unit"],
                to,
            ),
            axis=1,
        )
    )
    return df_
