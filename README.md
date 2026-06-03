# Experimental Stopping Database

[![pipeline status](https://gitlab.jyu.fi/rd-phys-acclab/radef/stopping/nds-experimental-stopping-database/badges/v0.1.4/pipeline.svg?ignore_skipped=true)](https://gitlab.jyu.fi/rd-phys-acclab/radef/stopping/nds-experimental-stopping-database/-/pipelines)

Python package for the Experimental Stopping Database. This package provides access to the bundled stopping power tables and reference metadata, as well as utilities for material classification and unit conversion. The data is obtained from https://nds.iaea.org/stopping/. When using the data for any purpose, all citations should be made to the original source.

## Quick start

Start notebook with `uvx`:

```bash
uvx --index-url https://gitlab.jyu.fi/api/v4/projects/12453/packages/pypi/simple --from nds_dedx_database nds-notebook
```

This will launch the interactive marimo notebook for exploring the stopping power data in your browser.

> Note: For this you will need to install `uv` from https://docs.astral.sh/uv/getting-started/installation/

## Installation

You can install the package from a Gitlab repository, or locally for development.

- From Gitlab (install latest main branch):

```bash
pip install git+https://gitlab.jyu.fi/rd-phys-acclab/radef/stopping/nds-experimental-stopping-database.git
```

- Local editable install (development):

```bash
pip install -e .[test]
```

Notebook quick-start uses `uv`/`uvx`. Ensure `uv` is installed before using the `uvx` example below. You can install `uv` following https://docs.astral.sh/uv/getting-started/installation/ or use the `nds-notebook` entry point directly with Python.

Running the packaged notebook via `uvx` (example):

```bash
uvx --index-url https://gitlab.jyu.fi/api/v4/projects/12453/packages/pypi/simple --from nds_dedx_database nds-notebook
```

Or run the notebook entry point directly (requires `marimo` in the environment):

```bash
python -m nds_dedx_database.notebook_entrypoint
```

## Running tests

Run the test-suite with `pytest` (recommended to run inside a virtual environment):

```bash
python -m pytest
```

If you use `uv` tooling, `uvx pytest` can be used to run tests inside the project's environment.



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
mass = get_element_mass("Cu", isotope=63.546)
density = get_element_density("Cu")

# Unit conversions
energy_mev = convert_energy(1000, from_unit="keV", to_unit="MeV")
dedx_mev_mg_cm2 = convert_dedx(0.5, from_unit="MeV/(mg/cm²)", to_unit="MeV/(mg/cm2)")

# Harmonize DataFrame units
df_harmonized = harmonize_energy_units(df, to="MeV/u")
df_harmonized = harmonize_dedx_units(df, to="MeV/(mg/cm2)")
```

Most utility functions are cached for improved performance when called repeatedly.


## Contributing

All contributions are welcome! Please open an issue or submit a pull request with any improvements or bug fixes. For major changes, please open an issue first to discuss the proposed changes. These should be submitted at the
[Gitlab repository](https://gitlab.jyu.fi/rd-phys-acclab/radef/stopping/nds-experimental-stopping-database). Github repository is
only used for visibility.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Citation

When using the data for any purpose, all citations should be made to the original source. See the [original data source](https://nds.iaea.org/stopping/) for citation details.
