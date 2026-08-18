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
    assert "http://localhost" not in html
    assert 'id="main-content"' in html
    assert "Ir al contenido" in html
    assert "cms-breadcrumb-bar" in html
    assert 'data-testid="cms-goto-seim"' in html
    assert "Ir a SEIM" in html
    assert "portal SEIM" in html
    assert 'href="/seim/login/"' in html


def _require_cms():
    if "cms" not in settings.INSTALLED_APPS or not any(
        a.startswith("wagtail") for a in settings.INSTALLED_APPS
    ):
        pytest.skip("Wagtail/CMS not in INSTALLED_APPS for this settings module")


def _publish_standard_page():
    from django.test import Client
    from wagtail.models import Page, Site

    from cms.models import HomePage, StandardPage

    root = Page.get_first_root_node()
    site = Site.objects.get(is_default_site=True)
    home = HomePage(
        title="Home",
        slug="home-cms-seim-nav",
        hero_title="T",
        hero_subtitle="S",
    )
    root.add_child(instance=home)
    home.save_revision().publish()
    site.root_page = home
    site.save()

    standard = StandardPage(title="About", slug="about-cms-seim-nav", introduction="Hello")
    home.add_child(instance=standard)
    standard.save_revision().publish()
    return Client(), standard.url


@pytest.mark.django_db
def test_cms_nav_points_authenticated_users_to_seim_dashboard():
    _require_cms()

    from django.contrib.auth import get_user_model

    client, url = _publish_standard_page()
    user = get_user_model().objects.create_user(
        username="cms-student",
        email="cms-student@test.com",
        password="pass12345",
    )
    client.force_login(user)

    response = client.get(url)
    assert response.status_code == 200
    html = response.content.decode()
    assert 'data-testid="cms-goto-seim"' in html
    assert 'href="/seim/dashboard/"' in html
    assert "Ir a SEIM" in html


def test_wagtail_admin_menu_includes_seim_portal_item():
    _require_cms()

    from cms.wagtail_hooks import register_seim_portal_menu_item

    item = register_seim_portal_menu_item()
    assert item.label == "Ir a SEIM"
    assert item.url == "/seim/"


@pytest.mark.django_db
def test_international_home_as_root_uses_same_origin_child_links():
    """Root pageurl is `/`; `{% pageurl %}/child/` would become `//child/` (TLS cert errors)."""
    _require_cms()

    from django.test import Client
    from wagtail.models import Page, Site

    from cms.models import InternationalHomePage

    root = Page.get_first_root_node()
    site = Site.objects.get(is_default_site=True)
    home = InternationalHomePage(
        title="Internacional",
        slug="internacional-root-test",
        hero_title="T",
        hero_subtitle="S",
    )
    root.add_child(instance=home)
    home.save_revision().publish()
    site.root_page = home
    site.save()

    response = Client().get("/")
    assert response.status_code == 200
    html = response.content.decode()
    assert 'href="/movilidad-estudiantil/"' in html
    assert "href=\"//movilidad-estudiantil/\"" not in html
    assert "http://localhost" not in html
    assert 'href="/seim/login/"' in html


def _site_home():
    from wagtail.models import Page, Site

    from cms.models import HomePage

    root = Page.get_first_root_node()
    site = Site.objects.get(is_default_site=True)
    home = HomePage(
        title="Home",
        slug="home-internacional-seed",
        hero_title="T",
        hero_subtitle="S",
    )
    root.add_child(instance=home)
    home.save_revision().publish()
    site.root_page = home
    site.save()
    return home


@pytest.mark.django_db
def test_setup_internacional_creates_missing_cgri_and_movilidad_pages():
    _require_cms()

    from django.core.management import call_command

    from cms.models import CGRIPage, InternationalHomePage, StandardPage

    _site_home()
    call_command("setup_internacional")
    call_command("setup_internacional")  # idempotent

    internacional = InternationalHomePage.objects.get(slug="internacional")
    cgri = CGRIPage.objects.child_of(internacional).get(slug="institucional")
    movilidad = internacional.get_children().get(slug="movilidad-estudiantil")

    expected_cgri = {
        "mision-vision",
        "equipo",
        "organigrama",
        "acreditaciones",
        "centros-de-idiomas",
        "asesoria-consular",
        "asociaciones",
        "contacto",
        "convenios",
    }
    assert expected_cgri <= set(cgri.get_children().values_list("slug", flat=True))

    expected_mov = {
        "programas",
        "como-aplicar",
        "requisitos",
        "documentacion",
        "entrante",
        "saliente",
        "beneficios",
        "calendario",
        "preguntas-frecuentes",
        "testimonios",
    }
    assert expected_mov <= set(movilidad.get_children().values_list("slug", flat=True))
    assert StandardPage.objects.child_of(movilidad).filter(slug="entrante").exists()


@pytest.mark.django_db
def test_populate_internacional_content_renders_official_copy():
    _require_cms()

    from django.core.management import call_command
    from django.test import Client

    from cms.models import ConvenioPage, InternationalHomePage

    _site_home()
    call_command("setup_internacional")
    call_command("populate_internacional_content")

    internacional = InternationalHomePage.objects.get(slug="internacional")
    client = Client()

    mision = client.get(f"{internacional.url}institucional/mision-vision/")
    assert mision.status_code == 200
    mision_html = mision.content.decode()
    assert "dimensión internacional" in mision_html
    assert "lourdesmorales@uadec.edu.mx" in mision_html

    docs = client.get(f"{internacional.url}movilidad-estudiantil/documentacion/")
    assert docs.status_code == 200
    docs_html = docs.content.decode()
    assert "Kárdex" in docs_html
    assert "ConvocatoriaMIEntrante.pdf" in docs_html or "FS-SP.pdf" in docs_html

    entrante = client.get(f"{internacional.url}movilidad-estudiantil/entrante/")
    assert entrante.status_code == 200
    entrante_html = entrante.content.decode()
    assert "Convocatoria" in entrante_html
    assert "forms.cloud.microsoft" in entrante_html

    movilidad = client.get(f"{internacional.url}movilidad-estudiantil/")
    assert movilidad.status_code == 200
    movilidad_html = movilidad.content.decode()
    assert 'href="/seim/register/"' in movilidad_html
    assert 'href="/register/"' not in movilidad_html.replace("/seim/register/", "")
    assert "Kárdex" in movilidad_html

    cgri = client.get(f"{internacional.url}institucional/")
    assert cgri.status_code == 200
    assert "lourdesmorales@uadec.edu.mx" in cgri.content.decode()

    assert any(choice[0] == "conahec" for choice in ConvenioPage.agreement_type.field.choices)


def test_cgri_and_movilidad_legacy_redirects():
    from django.test import Client

    client = Client()
    cases = [
        ("/cgri/organigrama/", "/internacional/institucional/organigrama/"),
        ("/cgri/idiomas/", "/internacional/institucional/centros-de-idiomas/"),
        ("/cgri/consular/", "/internacional/institucional/asesoria-consular/"),
        ("/movilidad/incoming/", "/internacional/movilidad-estudiantil/entrante/"),
        ("/movilidad/outgoing/", "/internacional/movilidad-estudiantil/saliente/"),
    ]
    for source, dest in cases:
        response = client.get(source)
        assert response.status_code == 301, source
        assert response.url == dest
