"""Regression: Program list queryset must stay deterministically ordered."""

import pytest
from rest_framework.test import APIRequestFactory

from exchange.views import ProgramViewSet
from tests.utils import TestUtils


@pytest.mark.django_db
def test_program_viewset_queryset_has_stable_ordering():
    TestUtils.create_test_program(name="Zulu Program")
    TestUtils.create_test_program(name="Alpha Program")
    factory = APIRequestFactory()
    request = factory.get("/api/programs/")
    view = ProgramViewSet()
    view.action = "list"
    view.request = request
    view.format_kwarg = None

    qs = view.get_queryset()
    assert qs.ordered is True
    assert qs.query.order_by == ("name", "pk")
    names = list(qs.values_list("name", flat=True))
    assert names == sorted(names)
