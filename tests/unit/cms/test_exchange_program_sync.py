from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Page

from cms.exchange_program_sync import (
    create_draft_program_page_for_program,
    get_program_index_page,
    sync_program_page_operational_fields_and_publish,
)
from cms.models import ProgramIndexPage, ProgramPage
from exchange.models import Program


class ExchangeProgramSyncTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="staff", password="x")
        self.user.is_staff = True
        self.user.save()

        self.root = Page.get_first_root_node()
        self.index = ProgramIndexPage(
            title="Programs",
            slug="programs-sync-test",
            introduction="<p>Index</p>",
        )
        self.root.add_child(instance=self.index)
        self.index.save_revision().publish()

        today = timezone.localdate()
        self.program = Program.objects.create(
            name="Nordic Exchange",
            description="A" * 600,
            start_date=today,
            end_date=today + timedelta(days=120),
            application_deadline=today + timedelta(days=30),
            required_language="Swedish",
            is_active=True,
        )

    def test_get_program_index_page_prefers_live(self):
        self.assertEqual(get_program_index_page().pk, self.index.pk)

    def test_create_draft_links_program_and_sets_operational_fields(self):
        page = create_draft_program_page_for_program(self.program, user=self.user)
        self.assertIsInstance(page, ProgramPage)
        self.assertFalse(page.live)
        self.assertEqual(page.program_id, self.program.pk)
        self.assertEqual(page.title, "Nordic Exchange")
        self.assertEqual(len(page.introduction), 500)
        self.assertEqual(page.language, "Swedish")
        self.assertEqual(page.application_deadline, self.program.application_deadline)

    def test_create_draft_raises_when_already_linked(self):
        create_draft_program_page_for_program(self.program, user=self.user)
        with self.assertRaises(ValueError):
            create_draft_program_page_for_program(self.program, user=self.user)

    def test_sync_updates_and_publishes_when_live(self):
        page = ProgramPage(
            title="Old",
            slug="nordic",
            introduction="old intro",
            body=[],
            program=self.program,
        )
        self.index.add_child(instance=page)
        page.save_revision(user=self.user).publish()

        self.program.name = "Nordic Exchange (Updated)"
        self.program.description = "New body summary text"
        self.program.save()

        status, updated_page = sync_program_page_operational_fields_and_publish(
            self.program, user=self.user
        )
        self.assertEqual(status, "updated")
        updated_page.refresh_from_db()
        self.assertTrue(updated_page.live)
        self.assertEqual(updated_page.title, "Nordic Exchange (Updated)")
        self.assertEqual(updated_page.introduction, "New body summary text"[:500])

    def test_sync_missing_returns_missing(self):
        other = Program.objects.create(
            name="Orphan",
            description="x",
            start_date=self.program.start_date,
            end_date=self.program.end_date,
        )
        status, page = sync_program_page_operational_fields_and_publish(other, user=self.user)
        self.assertEqual(status, "missing")
        self.assertIsNone(page)

    def test_wagtail_edit_url_resolves(self):
        page = create_draft_program_page_for_program(self.program, user=self.user)
        url = reverse("wagtailadmin_pages:edit", args=[page.id])
        self.assertTrue(url.startswith("/"))
