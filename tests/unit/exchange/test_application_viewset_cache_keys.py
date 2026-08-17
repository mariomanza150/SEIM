"""Cache key helpers for ApplicationViewSet list/retrieve must vary by user and query."""

from unittest.mock import MagicMock, patch

from exchange.views import (
    _application_list_cache_key,
    _application_retrieve_cache_key,
    _comment_list_cache_key,
)


def _request(user_pk, path="/api/applications/", authenticated=True):
    r = MagicMock()
    r.user.is_authenticated = authenticated
    r.user.pk = user_pk
    r.get_full_path.return_value = path
    return r


def test_application_list_cache_key_varies_by_user():
    k1 = _application_list_cache_key(None, _request(1))
    k2 = _application_list_cache_key(None, _request(2))
    assert k1 != k2


def test_application_list_cache_key_varies_by_query_string():
    k1 = _application_list_cache_key(None, _request(1, "/api/applications/?page=1"))
    k2 = _application_list_cache_key(None, _request(1, "/api/applications/?page=2"))
    assert k1 != k2


def test_application_retrieve_cache_key_varies_by_application_pk():
    r = _request(10)
    k1 = _application_retrieve_cache_key(
        None, r, pk="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    )
    k2 = _application_retrieve_cache_key(
        None, r, pk="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    )
    assert k1 != k2


def test_application_retrieve_cache_key_includes_viewset_prefix():
    key = _application_retrieve_cache_key(
        None, _request(10), pk="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    )
    assert "ApplicationViewSet.retrieve" in key


def test_application_retrieve_cache_key_changes_with_generation():
    r = _request(10)
    pk = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    with patch("exchange.views.application_api_cache_generation", return_value="0"):
        k1 = _application_retrieve_cache_key(None, r, pk=pk)
    with patch("exchange.views.application_api_cache_generation", return_value="1"):
        k2 = _application_retrieve_cache_key(None, r, pk=pk)
    assert k1 != k2


def test_comment_list_cache_key_varies_by_user():
    path = "/api/comments/?application=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    k1 = _comment_list_cache_key(None, _request(1, path))
    k2 = _comment_list_cache_key(None, _request(2, path))
    assert k1 != k2
    assert "CommentViewSet.list" in k1
