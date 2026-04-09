"""Cache key helpers for ApplicationViewSet list/retrieve must vary by user and query."""

from unittest.mock import MagicMock

from exchange.views import _application_list_cache_key, _application_retrieve_cache_key


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
    k1 = _application_retrieve_cache_key(None, r, pk="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    k2 = _application_retrieve_cache_key(None, r, pk="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    assert k1 != k2
