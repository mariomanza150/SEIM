#!/usr/bin/env python
"""Keep generated requirements*.txt in sync with pyproject.toml.

``pyproject.toml`` is the single source of truth for Python pins.
``requirements.txt``, ``requirements-dev.txt``, and ``requirements-test.txt``
are generated artifacts for Docker and ``pip install -r``.

Check (CI / ``make check-deps``)::

    python scripts/check_python_deps.py

Regenerate after editing pins in pyproject.toml::

    python scripts/check_python_deps.py --write
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
REQ_RUNTIME = ROOT / "requirements.txt"
REQ_DEV = ROOT / "requirements-dev.txt"
REQ_TEST = ROOT / "requirements-test.txt"

GENERATED_HEADER = """\
# Generated from pyproject.toml. Do not edit by hand.
# Edit pins in pyproject.toml, then run: python scripts/check_python_deps.py --write
"""

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


def _pins_from_req_file(path: Path) -> list[str]:
    pins: list[str] = []
    if not path.is_file():
        return pins
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        pins.append(line)
    return pins


def _load_pyproject_pins() -> tuple[list[str], list[str], list[str], list[str]]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project = data.get("project", {})
    runtime = list(project.get("dependencies") or [])
    optional = project.get("optional-dependencies") or {}
    dev = list(optional.get("dev") or [])
    test = list(optional.get("test") or [])
    dynamic = [item.lower() for item in project.get("dynamic", [])]
    return runtime, dev, test, dynamic


def _render_runtime(runtime: list[str]) -> str:
    body = "\n".join(runtime)
    return f"{GENERATED_HEADER}\n{body}\n"


def _render_extra(extra: list[str]) -> str:
    body = "\n".join(extra)
    return f"{GENERATED_HEADER}\n-r requirements.txt\n\n{body}\n"


def write_requirements(runtime: list[str], dev: list[str], test: list[str]) -> None:
    REQ_RUNTIME.write_text(_render_runtime(runtime), encoding="utf-8", newline="\n")
    REQ_DEV.write_text(_render_extra(dev), encoding="utf-8", newline="\n")
    REQ_TEST.write_text(_render_extra(test), encoding="utf-8", newline="\n")


def _pin_mismatch(label: str, expected: list[str], actual: list[str]) -> list[str]:
    errors: list[str] = []
    expected_norm = {_normalize(pin) for pin in expected}
    actual_norm = {_normalize(pin) for pin in actual}
    missing = sorted(expected_norm - actual_norm)
    extra = sorted(actual_norm - expected_norm)
    if missing:
        errors.append(f"{label} missing vs pyproject.toml: {', '.join(missing)}")
    if extra:
        errors.append(f"{label} extra vs pyproject.toml: {', '.join(extra)}")
    return errors


def _overlap_version_errors(dev: list[str], test: list[str]) -> list[str]:
    """Shared extra packages must use the same pin in [dev] and [test]."""
    dev_map = {_normalize(pin).split("==", 1)[0]: _normalize(pin) for pin in dev}
    test_map = {_normalize(pin).split("==", 1)[0]: _normalize(pin) for pin in test}
    errors: list[str] = []
    for name in sorted(set(dev_map) & set(test_map)):
        if dev_map[name] != test_map[name]:
            errors.append(
                f"overlapping extra {name} differs: dev={dev_map[name]} "
                f"test={test_map[name]}"
            )
    return errors


def check(runtime: list[str], dev: list[str], test: list[str], dynamic: list[str]) -> list[str]:
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
    if not dev:
        errors.append("pyproject.toml [project.optional-dependencies.dev] is empty")
    if not test:
        errors.append("pyproject.toml [project.optional-dependencies.test] is empty")
    if "django" not in _requirement_names(runtime):
        errors.append("pyproject.toml runtime dependencies do not list Django")

    errors.extend(_overlap_version_errors(dev, test))

    for path in (REQ_RUNTIME, REQ_DEV, REQ_TEST):
        if not path.is_file():
            errors.append(f"missing generated {path.relative_to(ROOT)}")
        elif GENERATED_HEADER.splitlines()[0] not in path.read_text(encoding="utf-8"):
            errors.append(
                f"{path.relative_to(ROOT)} is not generated; "
                "run python scripts/check_python_deps.py --write"
            )

    errors.extend(_pin_mismatch("requirements.txt", runtime, _pins_from_req_file(REQ_RUNTIME)))
    errors.extend(_pin_mismatch("requirements-dev.txt extras", dev, _pins_from_req_file(REQ_DEV)))
    errors.extend(
        _pin_mismatch("requirements-test.txt extras", test, _pins_from_req_file(REQ_TEST))
    )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate requirements*.txt from pyproject.toml",
    )
    args = parser.parse_args([] if argv is None else argv)

    runtime, dev, test, dynamic = _load_pyproject_pins()

    if args.write:
        if "dependencies" in dynamic or "optional-dependencies" in dynamic:
            print(
                "Cannot generate: pyproject.toml still uses dynamic dependencies.",
                file=sys.stderr,
            )
            return 1
        if not runtime or not dev or not test:
            print(
                "Cannot generate: pyproject.toml is missing dependencies or extras.",
                file=sys.stderr,
            )
            return 1
        overlap = _overlap_version_errors(dev, test)
        if overlap:
            print("Cannot generate: overlapping extras disagree:")
            for item in overlap:
                print(f"  - {item}")
            return 1
        write_requirements(runtime, dev, test)
        print(
            f"Wrote {REQ_RUNTIME.name}, {REQ_DEV.name}, {REQ_TEST.name} "
            f"({len(runtime)} runtime, {len(dev)} dev, {len(test)} test)."
        )
        return 0

    errors = check(runtime, dev, test, dynamic)
    if errors:
        print("Dependency check failed:")
        for item in errors:
            print(f"  - {item}")
        print("Fix: edit pyproject.toml, then python scripts/check_python_deps.py --write")
        return 1

    print(
        f"OK: {len(runtime)} runtime packages; {len(dev)} dev extras; "
        f"{len(test)} test extras. pyproject.toml is the source of truth."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
