"""Document list/retrieve cache keys must vary by user and path."""

from unittest.mock import MagicMock, patch

from documents.views import _document_list_cache_key, _document_retrieve_cache_key


def _request(user_pk, path="/api/documents/", authenticated=True):
    r = MagicMock()
    r.user.is_authenticated = authenticated
    r.user.pk = user_pk
    r.get_full_path.return_value = path
    return r


def test_document_list_cache_key_varies_by_user():
    k1 = _document_list_cache_key(None, _request(1))
    k2 = _document_list_cache_key(None, _request(2))
    assert k1 != k2
    assert "DocumentViewSet.list" in k1


def test_document_list_cache_key_varies_by_query_string():
    k1 = _document_list_cache_key(None, _request(1, "/api/documents/?page=1"))
    k2 = _document_list_cache_key(None, _request(1, "/api/documents/?page=2"))
    assert k1 != k2


def test_document_retrieve_cache_key_varies_by_pk():
    r = _request(10)
    k1 = _document_retrieve_cache_key(None, r, pk="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    k2 = _document_retrieve_cache_key(None, r, pk="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    assert k1 != k2


def test_document_retrieve_cache_key_changes_with_generation():
    r = _request(10)
    pk = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    with patch("documents.views.application_api_cache_generation", return_value="0"):
        k1 = _document_retrieve_cache_key(None, r, pk=pk)
    with patch("documents.views.application_api_cache_generation", return_value="1"):
        k2 = _document_retrieve_cache_key(None, r, pk=pk)
    assert k1 != k2
