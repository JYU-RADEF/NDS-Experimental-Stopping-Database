"""Tests for the data access API."""

from __future__ import annotations

import pandas as pd
import pytest

from nds_dedx_database import api


def test_refactored_api_exports_expected_names():
    expected = {
        "get_bundled_df",
        "get_references",
        "clear_stopping_data_cache",
        "get_data",
        "get_data_for_ion",
        "get_data_for_target",
        "get_data_for_ion_target",
        "get_data_elemental_targets",
        "get_data_compound_targets",
    }
    for name in expected:
        assert hasattr(api, name), f"Missing API function: {name}"

    removed = {
        "get_stopping_power_data",
        "get_stopping_power_for_ion",
        "get_stopping_power_for_target",
        "get_stopping_power_compound_targets",
        "get_stopping_power_elemental_targets",
    }
    for name in removed:
        assert not hasattr(api, name), f"Legacy API function still present: {name}"


def test_get_data_rejects_invalid_target_type():
    with pytest.raises(ValueError, match="target_type must be one of"):
        api.get_data(target_type="invalid", harmonize_units=False)


def test_normalize_target_supports_atomic_number_and_numeric_string():
    assert api._normalize_target(29) == "Cu"
    assert api._normalize_target("29") == "Cu"


def test_normalize_target_keeps_compound_formula_unchanged():
    assert api._normalize_target("SiO2") == "SiO2"


def test_get_data_for_ion_delegates_to_get_data(monkeypatch: pytest.MonkeyPatch):
    calls: list[dict[str, object]] = []
    expected = pd.DataFrame({"ok": [1]})

    def fake_get_data(**kwargs):
        calls.append(kwargs)
        return expected

    monkeypatch.setattr(api, "get_data", fake_get_data)
    result = api.get_data_for_ion("He", target_type="compound", copy=False)

    assert result is expected
    assert calls == [{"ion": "He", "target_type": "compound", "copy": False}]


def test_get_data_for_target_delegates_to_get_data(monkeypatch: pytest.MonkeyPatch):
    calls: list[dict[str, object]] = []
    expected = pd.DataFrame({"ok": [1]})

    def fake_get_data(**kwargs):
        calls.append(kwargs)
        return expected

    monkeypatch.setattr(api, "get_data", fake_get_data)
    result = api.get_data_for_target("Cu", copy=False)

    assert result is expected
    assert calls == [{"target": "Cu", "copy": False}]


def test_get_data_for_ion_target_delegates_to_get_data(
    monkeypatch: pytest.MonkeyPatch,
):
    calls: list[dict[str, object]] = []
    expected = pd.DataFrame({"ok": [1]})

    def fake_get_data(**kwargs):
        calls.append(kwargs)
        return expected

    monkeypatch.setattr(api, "get_data", fake_get_data)
    result = api.get_data_for_ion_target("He", "Cu", copy=False)

    assert result is expected
    assert calls == [{"ion": "He", "target": "Cu", "copy": False}]


def test_get_data_elemental_targets_delegates_to_get_data(
    monkeypatch: pytest.MonkeyPatch,
):
    calls: list[dict[str, object]] = []
    expected = pd.DataFrame({"ok": [1]})

    def fake_get_data(**kwargs):
        calls.append(kwargs)
        return expected

    monkeypatch.setattr(api, "get_data", fake_get_data)
    result = api.get_data_elemental_targets(copy=False)

    assert result is expected
    assert calls == [{"target_type": "elemental", "copy": False}]


def test_get_data_compound_targets_delegates_to_get_data(
    monkeypatch: pytest.MonkeyPatch,
):
    calls: list[dict[str, object]] = []
    expected = pd.DataFrame({"ok": [1]})

    def fake_get_data(**kwargs):
        calls.append(kwargs)
        return expected

    monkeypatch.setattr(api, "get_data", fake_get_data)
    result = api.get_data_compound_targets(copy=False)

    assert result is expected
    assert calls == [{"target_type": "compound", "copy": False}]


def test_get_data_for_ion_invalid_symbol_raises_value_error():
    with pytest.raises(ValueError, match="not found in the periodic table"):
        api.get_data_for_ion("InvalidIon123")


def test_clear_stopping_data_cache_invokes_cache_clear(monkeypatch: pytest.MonkeyPatch):
    called = {"value": False}

    def fake_cache_clear() -> None:
        called["value"] = True

    monkeypatch.setattr(api._read_csv_lazy, "cache_clear", fake_cache_clear)
    api.clear_stopping_data_cache()

    assert called["value"] is True


class _FakeCollectedFrame:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def to_pandas(self) -> pd.DataFrame:
        return self._df


class _FakeLazyFrame:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def collect(self) -> _FakeCollectedFrame:
        return _FakeCollectedFrame(self._df)


def test_get_bundled_df_returns_copy_by_default(monkeypatch: pytest.MonkeyPatch):
    source = pd.DataFrame({"projectile_name": ["H"], "target_name": ["Cu"]})

    def fake_read_csv_lazy(filename):
        assert filename == "StoppingPower.csv"
        return _FakeLazyFrame(source)

    monkeypatch.setattr(api, "_read_csv_lazy", fake_read_csv_lazy)
    out = api.get_bundled_df(copy=True)

    assert out.equals(source)
    assert out is not source


def test_get_references_returns_copy_by_default(monkeypatch: pytest.MonkeyPatch):
    source = pd.DataFrame({"ref_id": [1], "doi": ["x"], "year": [2020]})

    def fake_read_csv_lazy(filename):
        assert filename == "StoppingPower_refs.csv"
        return _FakeLazyFrame(source)

    monkeypatch.setattr(api, "_read_csv_lazy", fake_read_csv_lazy)
    out = api.get_references(copy=True)

    assert out.equals(source)
    assert out is not source
