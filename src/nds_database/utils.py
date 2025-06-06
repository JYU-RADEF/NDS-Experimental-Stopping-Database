# Utility functions for harmonizing the data

import pandas as pd  # type: ignore
import periodictable as pt  # type: ignore
from periodictable.formulas import parse_formula  # type: ignore
from pyparsing import ParseException


def detect_material_type(name: str):
    name = name.strip()

    # Try exact element match by symbol (case-sensitive)
    if hasattr(pt, name):
        element = getattr(pt, name)
        if isinstance(element, pt.core.Element):
            return "element"

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
    # Try matching by lowercase element name
    for elem in pt.elements:
        if elem is not None and elem.name.lower() == name.lower():
            return "element"

    return "unknown"


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


def convert_dedx(
    value: float, target_mass: float, from_unit: str, to_unit: str = "MeV/mg/cm2"
) -> float:
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
    from_unit : str
        The unit of the input value.
    to_unit : str
        The unit to convert to.

    Returns
    -------
    float
        The converted value.

    """

    if from_unit == to_unit:
        return value

    if from_unit == "MeV/(mg/cm2)" and to_unit == "E-15eV cm2/atom":
        return value * 1e-15
    elif from_unit == "E-15eV cm2/atom" and to_unit == "MeV/(mg/cm2)":
        return value / 1e-15
    elif from_unit == "eV/A" and to_unit == "MeV/(mg/cm2)":
        return value * 1e-6
    elif from_unit == "MeV/(mg/cm2)" and to_unit == "eV/A":
        return value / 1e-6
    else:
        raise ValueError(f"Unknown dE/dx units: {from_unit} to {to_unit}")


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
    df["target_mass"] = df["ion_mass"] * df["target_mass_atom_ratio"]

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
