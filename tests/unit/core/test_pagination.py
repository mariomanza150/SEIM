from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from core.pagination import StandardResultsSetPagination


def test_page_size_query_param_is_honored_and_capped():
    paginator = StandardResultsSetPagination()
    factory = APIRequestFactory()
    request = Request(factory.get("/api/applications/", {"page_size": "50"}))
    assert paginator.get_page_size(request) == 50

    request = Request(factory.get("/api/applications/", {"page_size": "500"}))
    assert paginator.get_page_size(request) == 100
