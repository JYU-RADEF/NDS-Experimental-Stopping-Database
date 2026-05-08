# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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