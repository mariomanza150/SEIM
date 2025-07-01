import pytest
from django.contrib.auth import get_user_model
from django.apps import apps

Exchange = apps.get_model('exchange', 'Exchange')
User = get_user_model()

@pytest.mark.django_db
def test_exchange_creation_and_status_helpers():
    user = User.objects.create_user(username='student', password='pass')
    exchange = Exchange.objects.create(student=user)
    assert exchange.status == 'DRAFT'
    assert exchange.is_completed() is False
    assert exchange.is_under_review() is False
    assert exchange.is_approved() is False
    assert exchange.is_rejected() is False
    assert exchange.is_cancelled() is False
    # Change status and check helpers
    exchange.status = 'APPROVED'
    assert exchange.is_approved() is True
    exchange.status = 'REJECTED'
    assert exchange.is_rejected() is True
    exchange.status = 'COMPLETED'
    assert exchange.is_completed() is True
    exchange.status = 'CANCELLED'
    assert exchange.is_cancelled() is True

@pytest.mark.django_db
def test_exchange_date_validation():
    user = User.objects.create_user(username='student', password='pass')
    exchange = Exchange(student=user, start_date='2025-01-01', end_date='2024-01-01')
    with pytest.raises(Exception):
        exchange.full_clean() 