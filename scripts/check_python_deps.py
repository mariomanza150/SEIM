#!/usr/bin/env python
"""Verify Python install files cannot drift from pyproject.toml.

Convention: requirements.txt is the pinned runtime set used by Docker and CI.
pyproject.toml must declare those same packages via setuptools dynamic
dependencies (file = requirements.txt). Optional extras stay in
requirements-dev.txt / requirements-test.txt.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parent.parent
REQ_RUNTIME = ROOT / "requirements.txt"
PYPROJECT = ROOT / "pyproject.toml"
PKG_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)")


def _requirement_names(path: Path) -> list[str]:
    names: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = PKG_RE.match(line)
        if match:
            names.append(match.group(1).lower().replace("_", "-"))
    return names


def main() -> int:
    errors: list[str] = []
    if not REQ_RUNTIME.is_file():
        errors.append(f"missing {REQ_RUNTIME.name}")
    if not PYPROJECT.is_file():
        errors.append(f"missing {PYPROJECT.name}")
    if errors:
        print("Dependency check failed:")
        for item in errors:
            print(f"  - {item}")
        return 1

    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project = data.get("project", {})
    dynamic = {item.lower() for item in project.get("dynamic", [])}
    static_deps = project.get("dependencies")
    setuptools_dynamic = data.get("tool", {}).get("setuptools", {}).get("dynamic", {})
    dep_file = setuptools_dynamic.get("dependencies", {}).get("file", [])

    if static_deps:
        errors.append(
            "pyproject.toml [project.dependencies] must stay empty; "
            "runtime pins live in requirements.txt"
        )
    if "dependencies" not in dynamic:
        errors.append('pyproject.toml [project] must set dynamic = ["dependencies"]')
    if "requirements.txt" not in dep_file:
        errors.append(
            "pyproject.toml [tool.setuptools.dynamic] must point "
            "dependencies at requirements.txt"
        )

    names = _requirement_names(REQ_RUNTIME)
    if "django" not in names:
        errors.append("requirements.txt does not list Django")

    if errors:
        print("Dependency check failed:")
        for item in errors:
            print(f"  - {item}")
        return 1

    print(
        f"OK: {len(names)} runtime packages pinned in requirements.txt; "
        "pyproject.toml reads that file as the project dependency source."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
