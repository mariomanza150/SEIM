"""Tests for spoken-language catalog resolution and alias matching."""

import pytest

from accounts.language_catalog import (
    canonical_language_name,
    canonicalize_additional_languages,
    languages_match,
    seed_spoken_languages,
)


@pytest.mark.django_db
class TestSpokenLanguageCatalog:
    def test_seed_creates_default_languages(self):
        rows = seed_spoken_languages()
        assert len(rows) >= 2
        assert canonical_language_name("Español") == "Spanish"
        assert canonical_language_name("Ingles") == "English"

    def test_languages_match_across_aliases(self):
        seed_spoken_languages()
        assert languages_match("Español", "Spanish") is True
        assert languages_match("Spanish", "Ingles") is False
        assert languages_match("English", "Ingles") is True
        assert languages_match("French", "") is True

    def test_canonicalize_additional_languages(self):
        seed_spoken_languages()
        rows = canonicalize_additional_languages(
            [{"name": "Español", "level": "B2"}, {"name": "Ingles", "level": "B1"}]
        )
        assert rows == [
            {"name": "Spanish", "level": "B2"},
            {"name": "English", "level": "B1"},
        ]

    def test_unknown_language_returns_none(self):
        seed_spoken_languages()
        assert canonical_language_name("Klingon") is None
