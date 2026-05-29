from pathlib import Path

from .api import (
    clear_stopping_data_cache,
    get_bundled_df,
    get_data,
    get_data_compound_targets,
    get_data_elemental_targets,
    get_data_for_ion,
    get_data_for_ion_target,
    get_data_for_target,
    get_references,
)
from .utils import (
    convert_dedx,
    convert_energy,
    get_element_density,
    get_element_mass,
    get_symbol,
    harmonize_dedx_units,
    harmonize_energy_units,
    is_compound,
    is_element_in_periodic_table,
)

DATA_PATH = Path(__file__).parent / "package_data" / "latest"

__all__ = [
    "is_compound",
    "is_element_in_periodic_table",
    "get_element_mass",
    "get_element_density",
    "get_symbol",
    "convert_energy",
    "convert_dedx",
    "harmonize_energy_units",
    "harmonize_dedx_units",
    "get_bundled_df",
    "get_references",
    "clear_stopping_data_cache",
    "get_data_for_ion",
    "get_data_for_target",
    "get_data_for_ion_target",
    "get_data_elemental_targets",
    "get_data_compound_targets",
    "get_data",
    "DATA_PATH",
]
