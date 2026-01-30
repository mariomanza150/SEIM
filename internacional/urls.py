"""
URL redirects for old CGRI and Movilidad pages.
Drop-in replacement mapping old UAdeC URLs to new international section.
"""
from django.urls import path
from django.views.generic import RedirectView

app_name = 'internacional'

urlpatterns = [
    # ============================================================================
    # OLD CGRI URL REDIRECTS
    # ============================================================================
    path('cgri/', RedirectView.as_view(
        url='/internacional/institucional/',
        permanent=True
    ), name='cgri_redirect'),
    
    path('cgri/about/', RedirectView.as_view(
        url='/internacional/institucional/mision-vision/',
        permanent=True
    ), name='cgri_about_redirect'),
    
    path('cgri/team/', RedirectView.as_view(
        url='/internacional/institucional/equipo/',
        permanent=True
    ), name='cgri_team_redirect'),
    
    path('cgri/agreements/', RedirectView.as_view(
        url='/internacional/institucional/convenios/',
        permanent=True
    ), name='cgri_agreements_redirect'),
    
    path('cgri/accreditations/', RedirectView.as_view(
        url='/internacional/institucional/acreditaciones/',
        permanent=True
    ), name='cgri_accreditations_redirect'),
    
    path('cgri/contact/', RedirectView.as_view(
        url='/internacional/institucional/contacto/',
        permanent=True
    ), name='cgri_contact_redirect'),
    
    # ============================================================================
    # OLD MOVILIDAD URL REDIRECTS
    # ============================================================================
    path('movilidad/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/',
        permanent=True
    ), name='movilidad_redirect'),
    
    path('movilidad/programs/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/programas/',
        permanent=True
    ), name='movilidad_programs_redirect'),
    
    path('movilidad/apply/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/como-aplicar/',
        permanent=True
    ), name='movilidad_apply_redirect'),
    
    path('movilidad/requirements/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/requisitos/',
        permanent=True
    ), name='movilidad_requirements_redirect'),
    
    path('movilidad/documents/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/documentacion/',
        permanent=True
    ), name='movilidad_documents_redirect'),
    
    path('movilidad/benefits/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/beneficios/',
        permanent=True
    ), name='movilidad_benefits_redirect'),
    
    path('movilidad/calendar/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/calendario/',
        permanent=True
    ), name='movilidad_calendar_redirect'),
    
    path('movilidad/faq/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/preguntas-frecuentes/',
        permanent=True
    ), name='movilidad_faq_redirect'),
]

