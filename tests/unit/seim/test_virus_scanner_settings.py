"""Tests for production-like virus scanner settings resolution."""

import logging

import pytest
from django.core.exceptions import ImproperlyConfigured

from seim.settings.virus_scanner import (
    mock_virus_scanner_allowed,
    resolve_virus_scanner_type,
)


def test_mock_allowed_on_development_and_test():
    assert mock_virus_scanner_allowed(deploy_tier="development") is True
    assert mock_virus_scanner_allowed(deploy_tier="test") is True
    assert mock_virus_scanner_allowed(deploy_tier="dev") is True


def test_mock_denied_on_production_without_override():
    assert mock_virus_scanner_allowed(deploy_tier="production") is False
    assert (
        mock_virus_scanner_allowed(deploy_tier="production", allow_mock=True) is True
    )


def test_resolve_defaults_to_mock_on_development():
    assert (
        resolve_virus_scanner_type(deploy_tier="development", environ={}) == "mock"
    )


def test_resolve_requires_type_on_production():
    with pytest.raises(ImproperlyConfigured, match="VIRUS_SCANNER_TYPE must be set"):
        resolve_virus_scanner_type(deploy_tier="production", environ={})


def test_resolve_accepts_clamav_on_production():
    assert (
        resolve_virus_scanner_type(
            deploy_tier="production",
            environ={"VIRUS_SCANNER_TYPE": "clamav"},
        )
        == "clamav"
    )


def test_resolve_rejects_mock_on_production_without_allow():
    with pytest.raises(ImproperlyConfigured, match="VIRUS_SCANNER_ALLOW_MOCK"):
        resolve_virus_scanner_type(
            deploy_tier="production",
            environ={"VIRUS_SCANNER_TYPE": "mock"},
        )


def test_resolve_allows_mock_on_production_with_flag(caplog):
    with caplog.at_level(logging.CRITICAL):
        assert (
            resolve_virus_scanner_type(
                deploy_tier="production",
                environ={
                    "VIRUS_SCANNER_TYPE": "mock",
                    "VIRUS_SCANNER_ALLOW_MOCK": "1",
                },
            )
            == "mock"
        )
    assert any("mock is active" in r.message for r in caplog.records)
