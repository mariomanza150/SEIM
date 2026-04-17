from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.utils.dateparse import parse_date

from exchange.models import EligibilityRuleSet


@dataclass(frozen=True)
class EligibilityCriteriaOverrides:
    """
    Scalar eligibility criteria overrides applied on top of a Program.

    This is intentionally narrow: it overrides only the fields used by the
    eligibility engine's scalar checks (window, GPA, language, age).
    """

    application_open_date: Any | None = None
    application_deadline: Any | None = None
    min_gpa: float | None = None
    required_language: str | None = None
    min_language_level: str | None = None
    min_age: int | None = None
    max_age: int | None = None


class ProgramEligibilityProxy:
    """
    Wrap a Program but override selected scalar eligibility fields.

    This lets the existing code-defined engine evaluate against "effective" criteria
    without changing its implementation.
    """

    def __init__(self, program, overrides: EligibilityCriteriaOverrides):
        self._program = program
        self._ov = overrides

    def __getattr__(self, item):
        return getattr(self._program, item)

    @property
    def application_open_date(self):
        return self._ov.application_open_date if self._ov.application_open_date is not None else self._program.application_open_date

    @property
    def application_deadline(self):
        return self._ov.application_deadline if self._ov.application_deadline is not None else self._program.application_deadline

    @property
    def min_gpa(self):
        return self._ov.min_gpa if self._ov.min_gpa is not None else self._program.min_gpa

    @property
    def required_language(self):
        return self._ov.required_language if self._ov.required_language is not None else self._program.required_language

    @property
    def min_language_level(self):
        return self._ov.min_language_level if self._ov.min_language_level is not None else self._program.min_language_level

    @property
    def min_age(self):
        return self._ov.min_age if self._ov.min_age is not None else self._program.min_age

    @property
    def max_age(self):
        return self._ov.max_age if self._ov.max_age is not None else self._program.max_age

    def get_application_window_status(self, on_date=None):
        # Temporarily patch scalar fields used by Program.get_application_window_status.
        orig_open = self._program.application_open_date
        orig_deadline = self._program.application_deadline
        try:
            self._program.application_open_date = self.application_open_date
            self._program.application_deadline = self.application_deadline
            return self._program.get_application_window_status(on_date=on_date)
        finally:
            self._program.application_open_date = orig_open
            self._program.application_deadline = orig_deadline


def parse_ruleset_overrides(ruleset: EligibilityRuleSet) -> EligibilityCriteriaOverrides:
    raw = ruleset.rules_json or {}
    prog = raw.get("program_overrides") or {}
    open_raw = prog.get("application_open_date")
    deadline_raw = prog.get("application_deadline")
    open_date = parse_date(open_raw) if isinstance(open_raw, str) else open_raw
    deadline_date = parse_date(deadline_raw) if isinstance(deadline_raw, str) else deadline_raw
    return EligibilityCriteriaOverrides(
        application_open_date=open_date,
        application_deadline=deadline_date,
        min_gpa=prog.get("min_gpa"),
        required_language=prog.get("required_language"),
        min_language_level=prog.get("min_language_level"),
        min_age=prog.get("min_age"),
        max_age=prog.get("max_age"),
    )

