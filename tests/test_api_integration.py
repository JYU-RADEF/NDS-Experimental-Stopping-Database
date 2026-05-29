"""Integration-style tests for `api.get_data` using a small in-memory dataset.

These tests monkeypatch `api._read_csv_lazy` to return a lightweight fake
lazy-frame whose `collect().to_dicts()` returns a list of dicts so the
real `get_data` code path (lazy filtering, collection, and post-filters)
is exercised without loading the full CSV bundle.
"""

from __future__ import annotations

import pandas as pd
import pytest

from nds_dedx_database import api, utils


class _Collected:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def to_dicts(self) -> list[dict]:
        return list(self._rows)


class _FakeLazy:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def filter(self, *args, **kwargs):
        # This fake is simplistic: return self (filters are applied in Python)
        return self

    def collect(self) -> _Collected:
        return _Collected(self._rows)

    def with_columns(self, *args, **kwargs):
        # This fake ignores with_columns since the real code applies target normalization in Python after collection
        return self


def _make_rows() -> list[dict]:
    return [
        {
            "projectile_name": "H",
            "ion_isotope": 1.008,
            "target_name": "Cu",
            "phase": "solid",
            "energy": 10.0,
            "energy_unit": "MeV",
            "stopping_power": 5.0,
            "stopping_unit": "MeV/(mg/cm2)",
            "target_mass": 63.546,
            "target_mass_atom_ratio": 1.0,
        },
        {
            "projectile_name": "He",
            "ion_isotope": 4.0026,
            "target_name": "SiO2",
            "phase": "solid",
            "energy": 20.0,
            "energy_unit": "keV/u",
            "stopping_power": 6.0,
            "stopping_unit": "MeV/(mg/cm2)",
            "target_mass": 60.08,
            "target_mass_atom_ratio": 1.0,
        },
    ]


def test_get_data_filters_and_target_type(monkeypatch: pytest.MonkeyPatch):
    rows = _make_rows()

    def fake_read_csv_lazy(filename):
        assert filename == "StoppingPower.csv"
        return _FakeLazy(rows)

    monkeypatch.setattr(api, "_read_csv_lazy", fake_read_csv_lazy)

    # Request elemental targets only (should return the Cu row)
    df_elem = api.get_data(target_type="elemental", harmonize_units=False)
    assert len(df_elem) == 1
    assert df_elem.iloc[0]["target_name"] == "Cu"

    # Request compound targets only (should return the SiO2 row)
    df_comp = api.get_data(target_type="compound", harmonize_units=False)
    assert len(df_comp) == 1
    assert df_comp.iloc[0]["target_name"] == "SiO2"


def test_get_data_filters_by_ion_and_target_and_harmonizes(
    monkeypatch: pytest.MonkeyPatch,
):
    rows = _make_rows()

    def fake_read_csv_lazy(filename):
        return _FakeLazy(rows)

    monkeypatch.setattr(api, "_read_csv_lazy", fake_read_csv_lazy)

    # Filter by ion symbol
    df = api.get_data(ion="H", target_type="any", harmonize_units=True)
    assert (df["projectile_name"] == "H").all()

    # Filter by atomic number (uses utils.get_symbol path)
    df2 = api.get_data(ion=2, target_type="any", harmonize_units=False)
    # 2 maps to Helium/He so we expect at least one projectile_name 'He'
    assert any(df2["projectile_name"] == utils.get_symbol(2))


def test_get_data_raises_when_filtered_empty(monkeypatch: pytest.MonkeyPatch):
    rows = _make_rows()

    def fake_read_csv_lazy(filename):
        return _FakeLazy(rows)

    monkeypatch.setattr(api, "_read_csv_lazy", fake_read_csv_lazy)

    with pytest.raises(ValueError, match="not found in the periodic table"):
        api.get_data(ion="Xx")


def test_get_data_he_sn_matches_bundled_slice():
    bundled = api.get_bundled_df(copy=False)
    expected = bundled[
        (bundled["projectile_name"] == "He") & (bundled["target_name"] == "Sn")
    ].reset_index(drop=True)

    data = api.get_data(ion="He", target="Sn", harmonize_units=False).reset_index(
        drop=True
    )

    pd.testing.assert_frame_equal(data, expected)
