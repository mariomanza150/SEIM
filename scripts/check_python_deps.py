#!/usr/bin/env python
"""Validate pyproject.toml as the single Python dependency source.

Install extras from the project file (do not add requirements*.txt)::

    pip install -e ".[dev]"
    pip install -e ".[test]"
    pip install -e ".[docs]"

Check (CI / ``make check-deps``)::

    python scripts/check_python_deps.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"

# Deleted on purpose. pyproject.toml is the only pin list.
LEGACY_REQUIREMENT_FILES = (
    ROOT / "requirements.txt",
    ROOT / "requirements-dev.txt",
    ROOT / "requirements-test.txt",
    ROOT / "dev-requirements-frozen.txt",
    ROOT / "requirements" / "dev.txt",
)

PKG_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)")


def _requirement_names(pins: list[str]) -> set[str]:
    names: set[str] = set()
    for raw in pins:
        match = PKG_RE.match(raw.strip())
        if match:
            names.add(match.group(1).lower().replace("_", "-"))
    return names


def _normalize(pin: str) -> str:
    pin = pin.strip()
    match = PKG_RE.match(pin)
    if not match:
        return pin.lower()
    name = match.group(1).lower().replace("_", "-")
    return name + pin[match.end() :]


def _load_pyproject_pins() -> tuple[list[str], dict[str, list[str]], list[str]]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project = data.get("project", {})
    runtime = list(project.get("dependencies") or [])
    optional = {
        name: list(pins or [])
        for name, pins in (project.get("optional-dependencies") or {}).items()
    }
    dynamic = [item.lower() for item in project.get("dynamic", [])]
    return runtime, optional, dynamic


def _overlap_version_errors(*extras: list[str]) -> list[str]:
    """Shared extra packages must use the same pin across extras."""
    maps: list[dict[str, str]] = []
    for extra in extras:
        maps.append(
            {_normalize(pin).split("==", 1)[0]: _normalize(pin) for pin in extra}
        )
    errors: list[str] = []
    names: set[str] = set()
    for mapping in maps:
        names.update(mapping)
    for name in sorted(names):
        pins = {mapping[name] for mapping in maps if name in mapping}
        if len(pins) > 1:
            errors.append(
                f"overlapping extra {name} differs: {', '.join(sorted(pins))}"
            )
    return errors


def _legacy_file_errors() -> list[str]:
    errors: list[str] = []
    for path in LEGACY_REQUIREMENT_FILES:
        if path.is_file():
            errors.append(
                f"legacy {path.relative_to(ROOT)} must be deleted; "
                'install from pyproject.toml (pip install -e ".[dev]")'
            )
    return errors


def check(
    runtime: list[str],
    optional: dict[str, list[str]],
    dynamic: list[str],
) -> list[str]:
    errors: list[str] = []
    if not PYPROJECT.is_file():
        return [f"missing {PYPROJECT.relative_to(ROOT)}"]

    if "dependencies" in dynamic or "optional-dependencies" in dynamic:
        errors.append(
            "pyproject.toml must declare static [project.dependencies] and "
            "[project.optional-dependencies]; do not use dynamic deps"
        )
    if not runtime:
        errors.append("pyproject.toml [project.dependencies] is empty")
    for extra in ("dev", "test", "docs"):
        if not optional.get(extra):
            errors.append(
                f"pyproject.toml [project.optional-dependencies.{extra}] is empty"
            )
    if "django" not in _requirement_names(runtime):
        errors.append("pyproject.toml runtime dependencies do not list Django")

    errors.extend(
        _overlap_version_errors(
            optional.get("dev") or [],
            optional.get("test") or [],
            optional.get("docs") or [],
        )
    )
    errors.extend(_legacy_file_errors())
    return errors


def _remove_legacy_files() -> list[Path]:
    removed: list[Path] = []
    for path in LEGACY_REQUIREMENT_FILES:
        if path.is_file():
            path.unlink()
            removed.append(path)
    leftover_dir = ROOT / "requirements"
    if leftover_dir.is_dir() and not any(leftover_dir.iterdir()):
        leftover_dir.rmdir()
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="No-op compatibility flag. Removes leftover requirements*.txt if present.",
    )
    args = parser.parse_args([] if argv is None else argv)

    runtime, optional, dynamic = _load_pyproject_pins()

    if args.write:
        removed = _remove_legacy_files()
        errors = check(runtime, optional, dynamic)
        if errors:
            print("Dependency check failed:")
            for item in errors:
                print(f"  - {item}")
            return 1
        if removed:
            print("Removed leftover requirement files:")
            for path in removed:
                print(f"  - {path.relative_to(ROOT)}")
        print(
            f"OK: pyproject.toml is the only pin list "
            f"({len(runtime)} runtime, {len(optional.get('dev') or [])} dev, "
            f"{len(optional.get('test') or [])} test, "
            f"{len(optional.get('docs') or [])} docs). "
            'Install with pip install -e ".[dev]".'
        )
        return 0

    errors = check(runtime, optional, dynamic)
    if errors:
        print("Dependency check failed:")
        for item in errors:
            print(f"  - {item}")
        print('Fix: edit pyproject.toml and install with pip install -e ".[dev]"')
        return 1

    print(
        f"OK: {len(runtime)} runtime packages; "
        f"{len(optional.get('dev') or [])} dev extras; "
        f"{len(optional.get('test') or [])} test extras; "
        f"{len(optional.get('docs') or [])} docs extras. "
        "pyproject.toml is the source of truth."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
