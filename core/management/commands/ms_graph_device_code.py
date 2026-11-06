"""Obtain a Microsoft Graph refresh token via OAuth2 device code flow.

Prints only the verification URL and user code. Writes the refresh token to a
gitignored file (default ``.ms_graph_refresh_token``) or prints it with
``--print-token``. Never logs the token.
"""

from __future__ import annotations

import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.email.ms_graph import (
    MicrosoftGraphAuthError,
    persist_refresh_token,
    poll_device_code,
    request_device_code,
)

DEFAULT_TOKEN_FILE = ".ms_graph_refresh_token"


def _ensure_graph_settings_from_env() -> None:
    """Populate MS_GRAPH_* on settings from the environment when unset.

    Allows running this command without selecting the Graph EMAIL_BACKEND
    (settings only load Graph vars when that backend is selected).
    """
    mapping = {
        "MS_GRAPH_CLIENT_ID": os.environ.get("MS_GRAPH_CLIENT_ID", ""),
        "MS_GRAPH_CLIENT_SECRET": os.environ.get("MS_GRAPH_CLIENT_SECRET", ""),
        "MS_GRAPH_TENANT": os.environ.get("MS_GRAPH_TENANT", "consumers")
        or "consumers",
    }
    for key, value in mapping.items():
        if not getattr(settings, key, None):
            setattr(settings, key, value)


class Command(BaseCommand):
    help = (
        "Start Microsoft Graph device-code sign-in for a personal Microsoft account "
        "and write the resulting refresh token for MS_GRAPH_REFRESH_TOKEN."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=DEFAULT_TOKEN_FILE,
            help=f"Path to write the refresh token (default: {DEFAULT_TOKEN_FILE}).",
        )
        parser.add_argument(
            "--print-token",
            action="store_true",
            help=(
                "Print the refresh token to stdout instead of writing a file "
                "(avoids clashing with Django's call_command stdout= stream)."
            ),
        )
        parser.add_argument(
            "--no-cache",
            action="store_true",
            help="Do not also persist the refresh token in Django cache.",
        )

    def handle(self, *args, **options):
        _ensure_graph_settings_from_env()

        if not (getattr(settings, "MS_GRAPH_CLIENT_ID", "") or ""):
            raise CommandError(
                "MS_GRAPH_CLIENT_ID is required. Set it in the environment "
                "(Azure app registration as a public client for personal accounts)."
            )

        try:
            device = request_device_code()
        except MicrosoftGraphAuthError as exc:
            raise CommandError(str(exc)) from exc

        verification_uri = (
            device.get("verification_uri")
            or device.get("verification_url")
            or "https://login.microsoft.com/device"
        )
        user_code = device.get("user_code") or ""
        device_code = device.get("device_code") or ""
        if not user_code or not device_code:
            raise CommandError("Device code response missing user_code or device_code")

        self.stdout.write("")
        self.stdout.write(
            self.style.NOTICE("Open this URL in a browser and enter the code:")
        )
        self.stdout.write(f"  URL:  {verification_uri}")
        self.stdout.write(f"  Code: {user_code}")
        self.stdout.write("")
        self.stdout.write(
            "Waiting for sign-in (sign in as the Hotmail mailbox owner)..."
        )

        try:
            tokens = poll_device_code(
                device_code,
                interval=int(device.get("interval") or 5),
                expires_in=int(device.get("expires_in") or 900),
            )
        except MicrosoftGraphAuthError as exc:
            raise CommandError(str(exc)) from exc

        refresh_token = tokens.get("refresh_token") or ""
        if not refresh_token:
            raise CommandError(
                "No refresh_token returned. Ensure the app requests offline_access "
                "and allow public client flows is enabled."
            )

        if not options["no_cache"]:
            persist_refresh_token(refresh_token)

        if options["print_token"]:
            # Operator may pipe into a secret store; still avoid logging.
            self.stdout.write(refresh_token)
            self.stderr.write(
                self.style.SUCCESS("Refresh token written to stdout (not logged).")
            )
            return

        path = Path(options["output"])
        path.write_text(refresh_token + "\n", encoding="utf-8")
        try:
            path.chmod(0o600)
        except OSError:
            pass
        self.stdout.write(
            self.style.SUCCESS(
                f"Refresh token written to {path.resolve()}. "
                "Set MS_GRAPH_REFRESH_TOKEN from this file (do not commit it)."
            )
        )
