"""Tests for CMS same-origin href rewriting."""

from cms.templatetags.cms_urls import localhost_url_to_path


def test_localhost_url_to_path_strips_host_and_port():
    assert localhost_url_to_path("http://localhost:8000/programas/") == "/programas/"
    assert localhost_url_to_path("https://127.0.0.1:8020/seim/login/") == "/seim/login/"
    assert localhost_url_to_path("http://localhost:8000/") == "/"
    assert localhost_url_to_path("http://localhost:8000") == "/"


def test_localhost_url_to_path_leaves_other_urls_alone():
    assert localhost_url_to_path("/programas/") == "/programas/"
    assert (
        localhost_url_to_path("https://www.uadec.mx/") == "https://www.uadec.mx/"
    )
    assert localhost_url_to_path("") == ""
