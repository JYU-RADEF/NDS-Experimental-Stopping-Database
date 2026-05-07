"""Tests for the data access API."""

from __future__ import annotations

import pandas as pd

from nds_dedx_database import api


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
