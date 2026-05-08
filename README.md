# Experimental Stopping Database

Python package for the Experimental Stopping Database. This package provides access to the bundled stopping power tables and reference metadata, as well as utilities for material classification and unit conversion. The data is obtained from https://nds.iaea.org/stopping/. When using the data for any purpose, all citations should be made to the original source.

## Data access

Use the bundled API to load the packaged CSV files once and reuse them from memory:

```python
from nds_dedx_database import get_stopping_power_data, get_stopping_power_references

stopping = get_stopping_power_data()
references = get_stopping_power_references()
```

Both functions return pandas DataFrames. By default they return defensive copies of the cached data, so downstream code can mutate the result without affecting later calls.

If you need the shared in-memory object directly, pass `copy=False`.

### Filtering by ions and targets

The API provides convenient functions to filter the stopping power data by specific ions (projectiles), targets, or combinations:

```python
from nds_dedx_database import (
    get_stopping_power_for_ion,
    get_stopping_power_for_target,
    get_stopping_power_for_ion_target,
    get_stopping_power_elemental_targets,
    get_stopping_power_compound_targets,
    get_stopping_power_for_ion_elemental_targets,
    get_stopping_power_for_ion_compound_targets,
)

# Single ion across all targets
h_stopping = get_stopping_power_for_ion("H")

# Single target across all ions
cu_stopping = get_stopping_power_for_target("Cu")

# Specific ion-target pair
h_in_cu = get_stopping_power_for_ion_target("H", "Cu")

# All ions in elemental targets only
elemental = get_stopping_power_elemental_targets()

# All ions in compound targets only
compounds = get_stopping_power_compound_targets()

# Specific ion in elemental targets only
h_elemental = get_stopping_power_for_ion_elemental_targets("H")

# Specific ion in compound targets only
h_compounds = get_stopping_power_for_ion_compound_targets("H")
```

All filtering functions return pandas DataFrames and support the same `copy` parameter as the base functions.

## Utilities

The package also exposes helpers for material classification and unit conversions.

## Contributing

All contributions are welcome! Please open an issue or submit a pull request with any improvements or bug fixes. For major changes, please open an issue first to discuss the proposed changes. These should be submitted at the
[Gitlab repository](https://gitlab.jyu.fi/rd-phys-acclab/radef/stopping/nds-experimental-stopping-database). Github repository is
only used for visibility.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Citation

When using the data for any purpose, all citations should be made to the original source. See the [original data source](https://nds.iaea.org/stopping/) for citation details.
