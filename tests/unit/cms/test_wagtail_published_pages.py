"""Published Wagtail CMS pages (requires Wagtail + cms in INSTALLED_APPS)."""

import pytest
from django.conf import settings


@pytest.mark.django_db
def test_standard_page_renders_seo_meta_and_a11y_landmarks():
    if "cms" not in settings.INSTALLED_APPS or not any(
        a.startswith("wagtail") for a in settings.INSTALLED_APPS
    ):
        pytest.skip("Wagtail/CMS not in INSTALLED_APPS for this settings module")

    from django.test import Client
    from wagtail.models import Page, Site

    from cms.models import HomePage, StandardPage

    root = Page.get_first_root_node()
    site = Site.objects.get(is_default_site=True)
    home = HomePage(
        title="Home",
        slug="home-cms-test",
        hero_title="T",
        hero_subtitle="S",
    )
    root.add_child(instance=home)
    home.save_revision().publish()
    site.root_page = home
    site.save()

    standard = StandardPage(title="About", slug="about-cms-test", introduction="Hello")
    home.add_child(instance=standard)
    standard.save_revision().publish()

    url = standard.url
    assert url
    response = Client().get(url)
    assert response.status_code == 200
    html = response.content.decode()
    assert 'property="og:title"' in html
    assert 'rel="canonical"' in html
    assert 'id="main-content"' in html
    assert "Ir al contenido" in html
    assert "cms-breadcrumb-bar" in html
