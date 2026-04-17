"""
Early warning filters for test/dev runs.

Python automatically imports ``sitecustomize`` (if present on sys.path) during startup,
before pytest plugin imports. We use this to suppress unavoidable third-party warnings
that currently trigger too early for pytest.ini filters to catch reliably.
"""

from __future__ import annotations

import warnings


# dateutil emits a DeprecationWarning at import time (datetime.utcfromtimestamp deprecation)
# inside its tz module. This is third-party and not actionable inside SEIM.
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"dateutil\.tz\..*",
)

# Fallback: match the deprecation message regardless of module/stacklevel.
warnings.filterwarnings(
    "ignore",
    message=r"datetime\.datetime\.utcfromtimestamp\(\) is deprecated.*",
    category=DeprecationWarning,
)

