# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Interactive marimo notebook (`notebooks/StoppingPowerDatabase.py`) for exploring and visualizing stopping power data with features for filtering by ions/targets and interactive plotting
- New dependencies for enhanced functionality:
  - `anywidget>=0.11.0` - Support for custom interactive widgets (main dependency)
  - `pyarrow>=24.0.0` - Arrow support for improved data handling (main dependency)
  - `marimo>=0.23.5` - Interactive notebook framework (notebooks dependency group)

### Fixed
- Improved error handling in `get_element_density()` to gracefully handle isotopes with missing density data; now falls back to natural element density when isotope-specific data is unavailable

## [0.1.3] - 2026-05-08

### Changed
- **BREAKING**: Refactored primary data access API with clearer naming:
  - `get_stopping_power_data()` → `get_bundled_df()`
  - `get_stopping_power_references()` → `get_references()`
  - `get_stopping_power_for_ion()` → `get_data_for_ion()`
  - `get_stopping_power_for_target()` → `get_data_for_target()`
  - `get_stopping_power_for_ion_target()` → `get_data_for_ion_target()`
  - `get_stopping_power_elemental_targets()` → `get_data_elemental_targets()`
  - `get_stopping_power_compound_targets()` → `get_data_compound_targets()`
- **BREAKING**: Removed redundant elemental/compound filtering functions:
  - `get_stopping_power_for_ion_elemental_targets()` - use `get_data_for_ion()` with `target_type="elemental"` parameter instead
  - `get_stopping_power_for_ion_compound_targets()` - use `get_data_for_ion()` with `target_type="compound"` parameter instead
  - `get_stopping_power_elemental_targets_for_target()` - use `get_data_for_target()` with `target_type="elemental"` parameter instead
  - `get_stopping_power_compound_targets_for_target()` - use `get_data_for_target()` with `target_type="compound"` parameter instead
- **BREAKING**: Renamed utility function `get_element_symbol()` → `get_symbol()` and updated its signature to accept both element symbols (str) and atomic numbers (int)
- Improved filtering API design: consolidated target type filtering into optional `target_type` parameter across all data access functions
- Switched to lazy evaluation with Polars backend for improved query performance; data is materialized only after filtering
- Enhanced ion and target parameter support: all data access functions now accept both element symbols/names (str) and atomic numbers (int)

### Added
- Caching (`@lru_cache`) to utility functions for improved performance: `get_symbol()`, `is_element_in_periodic_table()`, `is_compound()`, `get_element_mass()`, `get_element_density()`, and `detect_material_type()`
- New unified `get_data()` function providing flexible filtering by ion, target, and target type with lazy evaluation
- Enhanced error messages with helpful guidance when ion/target queries return no results
- Moved `py.typed` marker file into source directory for better PEP 561 compliance

## [0.1.2] - 2026-05-08

### Added
- Cached data access API for the bundled stopping power tables and reference metadata.
- Exported core functions from package root: `get_stopping_power_data`, `get_stopping_power_references`, and `clear_stopping_data_cache`.
- Filtering functions to query stopping power data by ions, targets, and material types:
  - `get_stopping_power_for_ion()` - Query single ion across all targets
  - `get_stopping_power_for_target()` - Query single target across all ions
  - `get_stopping_power_for_ion_target()` - Query specific ion-target pair
  - `get_stopping_power_elemental_targets()` - Query elemental targets only
  - `get_stopping_power_compound_targets()` - Query compound targets only
  - `get_stopping_power_for_ion_elemental_targets()` - Query ion in elemental targets only
  - `get_stopping_power_for_ion_compound_targets()` - Query ion in compound targets only
  - `get_stopping_power_elemental_targets_for_target()` - Query specific elemental target
  - `get_stopping_power_compound_targets_for_target()` - Query specific compound target

### Fixed
- Removed accidentally tracked `.DS_Store` files from repository.

## [0.1.1] - 2026-04-15

### Added
- MIT License file.
- CI/CD pipeline for automated testing, building, and package deployment.

### Changed
- Updated `.gitignore` to prevent tracking of system and build artifacts.

## [0.1.0] - 2026-04-10

### Added
- Initial release of the Experimental Stopping Database package.
- Core API module for accessing bundled stopping power data.
- Comprehensive test suite for API functionality.
- Utility functions for data harmonization and material classification.
- Support for querying stopping power data with pandas DataFrames.
- Package data including stopping power tables and reference metadata.