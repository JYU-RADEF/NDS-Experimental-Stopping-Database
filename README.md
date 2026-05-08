# Experimental Stopping Database

Python package for the Experimental Stopping Database. This package provides access to the bundled stopping power tables and reference metadata, as well as utilities for material classification and unit conversion. The data is obtained from https://nds.iaea.org/stopping/. When using the data for any purpose, all citations should be made to the original source.

## Data access

Use the bundled API to load the packaged CSV files once and reuse them from memory:

```python
from nds_dedx_database import get_bundled_df, get_references

stopping = get_bundled_df()
references = get_references()
```

Both functions return pandas DataFrames. By default they return defensive copies of the cached data, so downstream code can mutate the result without affecting later calls.

If you need the shared in-memory object directly, pass `copy=False`.

### Filtering by ions and targets

The API provides convenient functions to filter the stopping power data by specific ions (projectiles), targets, or combinations:

```python
from nds_dedx_database import (
    get_data_for_ion,
    get_data_for_target,
    get_data_for_ion_target,
    get_data_elemental_targets,
    get_data_compound_targets,
)

# Single ion across all targets
h_stopping = get_data_for_ion("H")

# Single target across all ions
cu_stopping = get_data_for_target("Cu")

# Specific ion-target pair
h_in_cu = get_data_for_ion_target("H", "Cu")

# All ions in elemental targets only
elemental = get_data_elemental_targets()

# All ions in compound targets only
compounds = get_data_compound_targets()
```

All filtering functions return pandas DataFrames and support the same `copy` parameter as the base functions. Ion and target arguments accept both element symbols (strings) and atomic numbers (integers).

## Utilities

The package exposes helpers for material classification and unit conversions:

```python
from nds_dedx_database import (
    get_symbol,
    is_element_in_periodic_table,
    is_compound,
    get_element_mass,
    get_element_density,
    convert_energy,
    convert_dedx,
    harmonize_energy_units,
    harmonize_dedx_units,
    detect_material_type,
)

# Element/compound detection
is_element_in_periodic_table("H")  # True
is_compound("H2O")  # True

# Material properties
mass = get_element_mass("Cu")
density = get_element_density("Cu")

# Unit conversions
energy_mev = convert_energy(1000, from_unit="keV", to_unit="MeV")
dedx_mev_mg_cm2 = convert_dedx(0.5, from_unit="MeV/mg·cm²", to_unit="MeV/(mg/cm2)")

# Harmonize DataFrame units
df_harmonized = harmonize_energy_units(df, to="MeV/u")
df_harmonized = harmonize_dedx_units(df, to="MeV/(mg/cm2)")
```

Most utility functions are cached for improved performance when called repeatedly.

## Interactive Tools

### Marimo Notebook

An interactive marimo notebook is provided in `notebooks/StoppingPowerDatabase.py` for exploring and visualizing the stopping power data. The notebook features:
- Data loading and inspection
- Energy and stopping power unit harmonization
- Interactive filtering by ion and target materials
- Log-scale scatter plots for stopping power vs. energy
- Density validation checks

To run the notebook, install the notebooks dependencies and use marimo:

```bash
# Install with notebook dependencies
uv sync --group notebooks

# Run the notebook
marimo run notebooks/StoppingPowerDatabase.py

# Or edit the notebook
marimo edit notebooks/StoppingPowerDatabase.py
```

## Contributing

All contributions are welcome! Please open an issue or submit a pull request with any improvements or bug fixes. For major changes, please open an issue first to discuss the proposed changes. These should be submitted at the
[Gitlab repository](https://gitlab.jyu.fi/rd-phys-acclab/radef/stopping/nds-experimental-stopping-database). Github repository is
only used for visibility.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Citation

When using the data for any purpose, all citations should be made to the original source. See the [original data source](https://nds.iaea.org/stopping/) for citation details.
