from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from importlib.resources import files
from pathlib import Path


def _get_notebook_path() -> Path:
    return Path(str(files("nds_dedx_database").joinpath("notebook_app.py")))


def _build_marimo_command(args: Sequence[str]) -> list[str]:
    notebook_path = _get_notebook_path()

    mode = "run"
    forwarded = list(args)
    if forwarded and forwarded[0] in {"run", "edit"}:
        mode = forwarded.pop(0)

    return [sys.executable, "-m", "marimo", mode, str(notebook_path), *forwarded]


def _run_command(command: list[str]) -> int:
    return subprocess.call(command)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    command = _build_marimo_command(args)
    return _run_command(command)


if __name__ == "__main__":
    raise SystemExit(main())
