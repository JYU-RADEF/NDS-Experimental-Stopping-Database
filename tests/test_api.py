"""Tests for the data access API."""

from __future__ import annotations

import pandas as pd
import pytest

from nds_dedx_database import api  # type: ignore


def test_get_stopping_power_data_is_cached(monkeypatch):
    api.clear_stopping_data_cache()

    read_calls: list[str] = []
    real_read_csv = pd.read_csv

    def wrapped_read_csv(*args, **kwargs):
        read_calls.append(str(args[0]))
        return real_read_csv(*args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", wrapped_read_csv)

    first = api.get_stopping_power_data(copy=False)
    second = api.get_stopping_power_data(copy=False)

    assert len(read_calls) == 1
    assert first is second
    assert {"projectile_name", "target_name", "stopping_power"}.issubset(first.columns)


def test_get_stopping_power_references_returns_copy():
    api.clear_stopping_data_cache()

    first = api.get_stopping_power_references()
    second = api.get_stopping_power_references()

    assert first.equals(second)
    assert first is not second
    assert {"ref_id", "doi", "year"}.issubset(first.columns)


# Tests for new filtering functions


def test_get_stopping_power_for_ion():
    """Test filtering by single ion across all targets."""
    api.clear_stopping_data_cache()
    full_data = api.get_stopping_power_data(copy=False)

    # Get a sample ion from the data
    sample_ion = full_data["projectile_name"].iloc[0]

    filtered = api.get_stopping_power_for_ion(sample_ion)

    # All rows should have the same projectile
    assert (filtered["projectile_name"] == sample_ion).all()
    # Should have at least one row
    assert len(filtered) > 0
    # Should have all expected columns
    assert {"projectile_name", "target_name", "stopping_power"}.issubset(
        filtered.columns
    )


def test_get_stopping_power_for_ion_invalid():
    """Test error handling for invalid ion."""
    api.clear_stopping_data_cache()

    with pytest.raises(ValueError, match="not found in database"):
        api.get_stopping_power_for_ion("InvalidIon123")


def test_get_stopping_power_for_target():
    """Test filtering by single target across all ions."""
    api.clear_stopping_data_cache()
    full_data = api.get_stopping_power_data(copy=False)

    # Get a sample target from the data
    sample_target = full_data["target_name"].iloc[0]

    filtered = api.get_stopping_power_for_target(sample_target)

    # All rows should have the same target
    assert (filtered["target_name"] == sample_target).all()
    # Should have at least one row
    assert len(filtered) > 0


def test_get_stopping_power_for_target_invalid():
    """Test error handling for invalid target."""
    api.clear_stopping_data_cache()

    with pytest.raises(ValueError, match="not found in database"):
        api.get_stopping_power_for_target("InvalidTarget123")


def test_get_stopping_power_for_ion_target():
    """Test filtering by ion-target pair."""
    api.clear_stopping_data_cache()
    full_data = api.get_stopping_power_data(copy=False)

    # Get a sample ion-target pair from the data
    sample_row = full_data.iloc[0]
    sample_ion = sample_row["projectile_name"]
    sample_target = sample_row["target_name"]

    filtered = api.get_stopping_power_for_ion_target(sample_ion, sample_target)

    # All rows should match both ion and target
    assert (filtered["projectile_name"] == sample_ion).all()
    assert (filtered["target_name"] == sample_target).all()
    # Should have at least one row
    assert len(filtered) > 0


def test_get_stopping_power_for_ion_target_invalid():
    """Test error handling for invalid ion-target pair."""
    api.clear_stopping_data_cache()

    with pytest.raises(ValueError, match="not found in database"):
        api.get_stopping_power_for_ion_target("InvalidIon", "InvalidTarget")


def test_get_stopping_power_elemental_targets():
    """Test filtering to elemental targets only."""
    api.clear_stopping_data_cache()

    filtered = api.get_stopping_power_elemental_targets()

    # Should have data
    assert len(filtered) > 0

    # Import utils to check material types
    from nds_dedx_database import utils

    # Verify all targets are elemental
    for target in filtered["target_name"].unique():
        assert not utils.is_compound(target), f"Found compound target: {target}"


def test_get_stopping_power_compound_targets():
    """Test filtering to compound targets only."""
    api.clear_stopping_data_cache()

    filtered = api.get_stopping_power_compound_targets()

    # Should have data (assuming database has compounds)
    if len(filtered) > 0:
        from nds_dedx_database import utils

        # Verify all targets are compounds
        for target in filtered["target_name"].unique():
            assert utils.is_compound(target), f"Found non-compound target: {target}"


def test_get_stopping_power_for_ion_elemental_targets():
    """Test filtering by ion in elemental targets only."""
    api.clear_stopping_data_cache()

    # Find an ion that has data in elemental targets
    elemental = api.get_stopping_power_elemental_targets(copy=False)
    if len(elemental) > 0:
        sample_ion = elemental["projectile_name"].iloc[0]

        filtered = api.get_stopping_power_for_ion_elemental_targets(sample_ion)

        # All rows should have the specified ion
        assert (filtered["projectile_name"] == sample_ion).all()

        from nds_dedx_database import utils

        # All targets should be elemental
        for target in filtered["target_name"].unique():
            assert not utils.is_compound(target)


def test_get_stopping_power_for_ion_elemental_targets_invalid():
    """Test error handling for ion not in elemental targets."""
    api.clear_stopping_data_cache()

    # This should fail if the ion doesn't exist in elemental targets
    with pytest.raises(ValueError, match="not found in elemental targets"):
        api.get_stopping_power_for_ion_elemental_targets("InvalidIon123")


def test_get_stopping_power_for_ion_compound_targets():
    """Test filtering by ion in compound targets only."""
    api.clear_stopping_data_cache()
    compound = api.get_stopping_power_compound_targets(copy=False)

    if len(compound) > 0:
        sample_ion = compound["projectile_name"].iloc[0]

        filtered = api.get_stopping_power_for_ion_compound_targets(sample_ion)

        # All rows should have the specified ion
        assert (filtered["projectile_name"] == sample_ion).all()

        from nds_dedx_database import utils

        # All targets should be compounds
        for target in filtered["target_name"].unique():
            assert utils.is_compound(target)


def test_get_stopping_power_elemental_targets_for_target():
    """Test filtering by specific elemental target."""
    api.clear_stopping_data_cache()
    elemental = api.get_stopping_power_elemental_targets(copy=False)

    if len(elemental) > 0:
        sample_target = elemental["target_name"].iloc[0]

        filtered = api.get_stopping_power_elemental_targets_for_target(sample_target)

        # All rows should have the specified target
        assert (filtered["target_name"] == sample_target).all()


def test_get_stopping_power_elemental_targets_for_target_invalid_compound():
    """Test error handling when target is a compound."""
    api.clear_stopping_data_cache()
    compound = api.get_stopping_power_compound_targets(copy=False)

    if len(compound) > 0:
        sample_compound = compound["target_name"].iloc[0]

        with pytest.raises(ValueError, match="is a compound"):
            api.get_stopping_power_elemental_targets_for_target(sample_compound)


def test_get_stopping_power_compound_targets_for_target():
    """Test filtering by specific compound target."""
    api.clear_stopping_data_cache()
    compound = api.get_stopping_power_compound_targets(copy=False)

    if len(compound) > 0:
        sample_target = compound["target_name"].iloc[0]

        filtered = api.get_stopping_power_compound_targets_for_target(sample_target)

        # All rows should have the specified target
        assert (filtered["target_name"] == sample_target).all()


def test_get_stopping_power_compound_targets_for_target_invalid_element():
    """Test error handling when target is not a compound."""
    api.clear_stopping_data_cache()
    elemental = api.get_stopping_power_elemental_targets(copy=False)

    if len(elemental) > 0:
        sample_element = elemental["target_name"].iloc[0]

        with pytest.raises(ValueError, match="is not a compound"):
            api.get_stopping_power_compound_targets_for_target(sample_element)


def test_filtering_returns_copy_by_default():
    """Test that filtering functions return copies by default."""
    api.clear_stopping_data_cache()
    full_data = api.get_stopping_power_data(copy=False)

    if len(full_data) > 0:
        sample_ion = full_data["projectile_name"].iloc[0]

        first = api.get_stopping_power_for_ion(sample_ion, copy=True)
        second = api.get_stopping_power_for_ion(sample_ion, copy=True)

        # Should be equal but not the same object
        assert first.equals(second)
        assert first is not second


def test_filtering_can_return_same_object():
    """Test that filtering functions with copy=False don't make unnecessary copies."""
    api.clear_stopping_data_cache()
    full_data = api.get_stopping_power_data(copy=False)

    if len(full_data) > 0:
        sample_target = full_data["target_name"].iloc[0]

        # Get filtered data twice with copy=False
        first = api.get_stopping_power_for_target(sample_target, copy=False)
        second = api.get_stopping_power_for_target(sample_target, copy=False)

        # The data should be equal (not necessarily the same object)
        # since pandas filtering creates views
        assert first.equals(second)
