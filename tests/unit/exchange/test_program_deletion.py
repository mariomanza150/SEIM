"""Unit tests for program deletion impact preview."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from exchange.program_deletion import get_program_deletion_impact


class _FakeMeta:
    def __init__(self, label_lower, verbose_name_plural="Items", verbose_name="Item"):
        self.label_lower = label_lower
        self.verbose_name_plural = verbose_name_plural
        self.verbose_name = verbose_name


class _FakeModel:
    def __init__(self, label_lower, verbose_name_plural="Items"):
        self._meta = _FakeMeta(label_lower, verbose_name_plural=verbose_name_plural)


def test_get_program_deletion_impact_counts_related_objects():
    from exchange.models import Program

    program = SimpleNamespace(pk="prog-1", name="Cascade Program", __class__=Program)

    app_model = _FakeModel("exchange.application", "Applications")
    host_model = _FakeModel("exchange.hostinstitution", "Host institutions")

    collector = MagicMock()
    collector.model_objs = {
        Program: [program],
        app_model: [object(), object()],
        host_model: [object()],
    }
    collector.protected = []

    with (
        patch("exchange.program_deletion.NestedObjects", return_value=collector),
        patch("exchange.program_deletion.router.db_for_write", return_value="default"),
    ):
        impact = get_program_deletion_impact(program)

    assert impact["program"] == {"id": "prog-1", "name": "Cascade Program"}
    assert impact["can_delete"] is True
    models = {row["model"]: row["count"] for row in impact["related"]}
    assert models["exchange.application"] == 2
    assert models["exchange.hostinstitution"] == 1
    assert impact["total_related"] == 3
    assert "exchange.program" not in models
    collector.collect.assert_called_once_with([program])


def test_get_program_deletion_impact_reports_protected_objects():
    from exchange.models import Program

    program = SimpleNamespace(pk="prog-2", name="Blocked Program", __class__=Program)

    class Locked:
        _meta = _FakeMeta("exchange.something", verbose_name="Something")

        def __str__(self):
            return "locked-row"

    collector = MagicMock()
    collector.model_objs = {Program: [program]}
    collector.protected = [Locked()]

    with (
        patch("exchange.program_deletion.NestedObjects", return_value=collector),
        patch("exchange.program_deletion.router.db_for_write", return_value="default"),
    ):
        impact = get_program_deletion_impact(program)

    assert impact["can_delete"] is False
    assert impact["related"] == []
    assert impact["protected"][0]["repr"] == "locked-row"
    assert impact["protected"][0]["model"] == "exchange.something"
