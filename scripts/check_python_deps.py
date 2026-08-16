#!/usr/bin/env python
"""Verify Python install files cannot drift from pyproject.toml.

Convention: requirements.txt is the pinned runtime set used by Docker and CI.
pyproject.toml reads that file via setuptools dynamic dependencies.
Dev/test extras are pinned in requirements-dev.txt / requirements-test.txt and
mirrored (without ``-r`` includes) in requirements/dev-extras.txt and
requirements/test-extras.txt so ``pip install seim[dev]`` cannot drift.
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
REQ_DEV = ROOT / "requirements-dev.txt"
REQ_TEST = ROOT / "requirements-test.txt"
EXTRAS_DEV = ROOT / "requirements" / "dev-extras.txt"
EXTRAS_TEST = ROOT / "requirements" / "test-extras.txt"
PYPROJECT = ROOT / "pyproject.toml"
PKG_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)")


def _requirement_names(path: Path) -> set[str]:
    names: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = PKG_RE.match(line)
        if match:
            names.add(match.group(1).lower().replace("_", "-"))
    return names


def main() -> int:
    errors: list[str] = []
    for path in (REQ_RUNTIME, REQ_DEV, REQ_TEST, EXTRAS_DEV, EXTRAS_TEST, PYPROJECT):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        print("Dependency check failed:")
        for item in errors:
            print(f"  - {item}")
        return 1

    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project = data.get("project", {})
    dynamic = {item.lower() for item in project.get("dynamic", [])}
    static_deps = project.get("dependencies")
    static_optional = project.get("optional-dependencies")
    setuptools_dynamic = data.get("tool", {}).get("setuptools", {}).get("dynamic", {})
    dep_file = setuptools_dynamic.get("dependencies", {}).get("file", [])
    opt = setuptools_dynamic.get("optional-dependencies", {})
    dev_file = opt.get("dev", {}).get("file", [])
    test_file = opt.get("test", {}).get("file", [])

    if static_deps:
        errors.append(
            "pyproject.toml [project.dependencies] must stay empty; "
            "runtime pins live in requirements.txt"
        )
    if static_optional:
        errors.append(
            "pyproject.toml [project.optional-dependencies] must stay empty; "
            "use [tool.setuptools.dynamic] optional-dependencies files"
        )
    if "dependencies" not in dynamic or "optional-dependencies" not in dynamic:
        errors.append(
            "pyproject.toml [project] must set dynamic = "
            '["dependencies", "optional-dependencies"]'
        )
    if "requirements.txt" not in dep_file:
        errors.append("pyproject.toml must point dependencies at requirements.txt")
    if "requirements/dev-extras.txt" not in dev_file:
        errors.append(
            "pyproject.toml must point optional-dependencies.dev at "
            "requirements/dev-extras.txt"
        )
    if "requirements/test-extras.txt" not in test_file:
        errors.append(
            "pyproject.toml must point optional-dependencies.test at "
            "requirements/test-extras.txt"
        )

    runtime = _requirement_names(REQ_RUNTIME)
    if "django" not in runtime:
        errors.append("requirements.txt does not list Django")

    if _requirement_names(EXTRAS_DEV) != _requirement_names(REQ_DEV):
        errors.append(
            "requirements/dev-extras.txt packages must match "
            "requirements-dev.txt extras"
        )
    if _requirement_names(EXTRAS_TEST) != _requirement_names(REQ_TEST):
        errors.append(
            "requirements/test-extras.txt packages must match "
            "requirements-test.txt extras"
        )

    if errors:
        print("Dependency check failed:")
        for item in errors:
            print(f"  - {item}")
        return 1

    print(
        f"OK: {len(runtime)} runtime packages; "
        f"{len(_requirement_names(EXTRAS_DEV))} dev extras; "
        f"{len(_requirement_names(EXTRAS_TEST))} test extras "
        "wired through pyproject.toml."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
