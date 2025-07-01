import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import RequestFactory
from django.contrib.admin.sites import AdminSite
from SEIM.exchange.admin.academic import CourseAdmin
from SEIM.exchange.admin.exchange import ExchangeAdmin
from SEIM.exchange.models.applications.course import Course
from SEIM.exchange.models.applications.exchange import Exchange

User = get_user_model()

@pytest.mark.django_db
def test_course_admin_permissions(client):
    user = User.objects.create_user(username='student', password='pass')
    staff = User.objects.create_user(username='staff', password='pass', is_staff=True)
    exchange_manager = User.objects.create_user(username='manager', password='pass')
    group = Group.objects.create(name='Exchange Managers')
    exchange_manager.groups.add(group)
    exchange = Exchange.objects.create(student=user)
    course = Course.objects.create(course_code='C101', course_name='Test', exchange=exchange, host_university='TestU', department='Dept', credits=3, status='PLANNED')
    admin = CourseAdmin(Course, AdminSite())
    # Simulate requests with different users
    factory = RequestFactory()
    for test_user, should_allow in [
        (staff, True),
        (exchange_manager, True),
        (user, True),
    ]:
        req = factory.get('/')
        req.user = test_user
        assert admin.has_view_permission(req, course) is should_allow

@pytest.mark.django_db
def test_exchange_admin_queryset(client):
    staff = User.objects.create_user(username='staff', password='pass', is_staff=True)
    student = User.objects.create_user(username='student', password='pass')
    exchange = Exchange.objects.create(student=student)
    admin = ExchangeAdmin(Exchange, AdminSite())
    factory = RequestFactory()
    req_staff = factory.get('/')
    req_staff.user = staff
    qs = admin.get_queryset(req_staff)
    assert exchange in qs
    req_student = factory.get('/')
    req_student.user = student
    qs = admin.get_queryset(req_student)
    assert exchange in qs 