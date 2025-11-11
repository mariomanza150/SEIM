"""
URL configuration for core app.
"""
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    # Contact form URLs
    path('contact/', views.ContactFormView.as_view(), name='contact_form'),
    path('contact/submit/', views.ContactFormSubmitView.as_view(), name='contact_form_submit'),
]
