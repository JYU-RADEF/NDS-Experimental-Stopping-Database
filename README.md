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

## Utilities

The package also exposes helpers for material classification and unit conversions.