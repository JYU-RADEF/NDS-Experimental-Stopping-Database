"""Tests for the notebook CLI entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from nds_dedx_database import notebook_entrypoint


def test_main_builds_default_run_command(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    monkeypatch.setattr(
        notebook_entrypoint,
        "_get_notebook_path",
        lambda: Path("/tmp/notebook_app.py"),
    )

    def fake_run_command(command: list[str]) -> int:
        calls.append(command)
        return 0

    monkeypatch.setattr(notebook_entrypoint, "_run_command", fake_run_command)

    exit_code = notebook_entrypoint.main(["--port", "2718"])

    assert exit_code == 0
    assert calls == [
        [
            sys.executable,
            "-m",
            "marimo",
            "run",
            "/tmp/notebook_app.py",
            "--port",
            "2718",
        ]
    ]


def test_main_supports_explicit_edit_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    monkeypatch.setattr(
        notebook_entrypoint,
        "_get_notebook_path",
        lambda: Path("/tmp/notebook_app.py"),
    )

    def fake_run_command(command: list[str]) -> int:
        calls.append(command)
        return 0

    monkeypatch.setattr(notebook_entrypoint, "_run_command", fake_run_command)

    exit_code = notebook_entrypoint.main(["edit", "--port", "2720"])

    assert exit_code == 0
    assert calls == [
        [
            sys.executable,
            "-m",
            "marimo",
            "edit",
            "/tmp/notebook_app.py",
            "--port",
            "2720",
        ]
    ]


def test_main_propagates_subprocess_exit_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        notebook_entrypoint,
        "_get_notebook_path",
        lambda: Path("/tmp/notebook_app.py"),
    )
    monkeypatch.setattr(notebook_entrypoint, "_run_command", lambda _command: 3)

    assert notebook_entrypoint.main([]) == 3
