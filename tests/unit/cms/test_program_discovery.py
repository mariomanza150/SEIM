from datetime import timedelta

import pytest
from django.conf import settings
from django.test import RequestFactory, TestCase

if "wagtail" not in settings.INSTALLED_APPS:
    pytest.skip("Wagtail disabled in test settings", allow_module_level=True)
from django.utils import timezone
from wagtail.models import Page

from cms.models import ProgramIndexPage, ProgramPage
from exchange.models import Program


class ProgramDiscoveryPageTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.root = Page.get_first_root_node()
        self.index_page = ProgramIndexPage(
            title="Programs",
            slug="programs-discovery-test",
            introduction="<p>Browse programs</p>",
        )
        self.root.add_child(instance=self.index_page)
        self.index_page.save_revision().publish()

        today = timezone.localdate()
        self.active_program = Program.objects.create(
            name="Engineering Exchange",
            description="Study engineering abroad",
            start_date=today + timedelta(days=90),
            end_date=today + timedelta(days=210),
            is_active=True,
        )
        self.inactive_program = Program.objects.create(
            name="History Exchange",
            description="Archived history exchange option",
            start_date=today + timedelta(days=120),
            end_date=today + timedelta(days=240),
            is_active=False,
        )

        self.active_page = ProgramPage(
            title="Engineering In Spain",
            slug="engineering-spain",
            introduction="Engineering mobility in Madrid.",
            location="Spain",
            language="Spanish",
            body=[],
            program=self.active_program,
        )
        self.index_page.add_child(instance=self.active_page)
        self.active_page.save_revision().publish()

        self.inactive_page = ProgramPage(
            title="History In France",
            slug="history-france",
            introduction="History mobility in Paris.",
            location="France",
            language="French",
            body=[],
            program=self.inactive_program,
        )
        self.index_page.add_child(instance=self.inactive_page)
        self.inactive_page.save_revision().publish()

    def test_program_index_filters_by_search_and_location(self):
        request = self.factory.get(
            "/programs-discovery-test/",
            {"q": "engineering", "location": "Spain"},
        )

        context = self.index_page.get_context(request)
        programs = list(context["programs"].object_list)

        self.assertEqual(len(programs), 1)
        self.assertEqual(programs[0].title, "Engineering In Spain")
        self.assertEqual(context["search_query"], "engineering")
        self.assertEqual(context["selected_location"], "Spain")

    def test_program_index_active_only_excludes_inactive_linked_programs(self):
        request = self.factory.get(
            "/programs-discovery-test/",
            {"active_only": "1"},
        )

        context = self.index_page.get_context(request)
        programs = list(context["programs"].object_list)

        self.assertEqual(len(programs), 1)
        self.assertEqual(programs[0].title, "Engineering In Spain")
        self.assertTrue(context["active_only"])

    def test_program_index_exposes_filter_options(self):
        request = self.factory.get("/programs-discovery-test/")

        context = self.index_page.get_context(request)

        self.assertIn("Spain", context["available_locations"])
        self.assertIn("France", context["available_locations"])
        self.assertIn("Spanish", context["available_languages"])
        self.assertIn("French", context["available_languages"])
