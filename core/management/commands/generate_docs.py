"""
Management command to generate comprehensive documentation for SEIM.

This command generates:
1. API documentation (OpenAPI schema)
2. Code documentation (models, views, services)
3. Database schema documentation
4. Endpoint documentation
5. Updates existing documentation files
"""

import os
from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate comprehensive documentation for SEIM project"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default="documentation/generated",
            help="Output directory for generated documentation",
        )
        parser.add_argument(
            "--format",
            choices=["yaml", "json", "html"],
            default="yaml",
            help="Output format for API schema",
        )
        parser.add_argument(
            "--include-code",
            action="store_true",
            help="Include code documentation generation",
        )
        parser.add_argument(
            "--include-db",
            action="store_true",
            help="Include database schema documentation",
        )
        parser.add_argument(
            "--include-apis",
            action="store_true",
            help="Include API documentation generation",
        )
        parser.add_argument(
            "--include-models",
            action="store_true",
            help="Include model documentation generation",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Verbose output",
        )
        parser.add_argument(
            "--force", action="store_true", help="Force regeneration of existing files"
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting SEIM Documentation Generation...")

        output_dir = options["output_dir"]
        os.makedirs(output_dir, exist_ok=True)

        # Generate API documentation
        self.generate_api_docs(output_dir, options)

        # Generate code documentation
        if options["include_code"]:
            self.generate_code_docs(output_dir, options)

        # Generate database documentation
        if options["include_db"]:
            self.generate_db_docs(output_dir, options)

        # Update existing documentation
        self.update_existing_docs(output_dir, options)

        self.stdout.write("✅ Documentation generation completed!")
        self.stdout.write(f"📁 Output directory: {output_dir}")

    def generate_api_docs(self, output_dir, options):
        """Generate API documentation using drf-spectacular."""
        self.stdout.write("📚 Generating API documentation...")

        try:
            # Generate OpenAPI schema
            schema_format = options["format"]
            schema_file = os.path.join(output_dir, f"api_schema.{schema_format}")

            call_command(
                "spectacular",
                "--file",
                schema_file,
                "--format",
                schema_format,
                verbosity=0,
            )

            # Generate API endpoints documentation
            self.generate_endpoints_docs(output_dir)

            self.stdout.write(f"  ✅ API schema: {schema_file}")
            self.stdout.write(f"  ✅ API endpoints: {output_dir}/api_endpoints.md")

        except Exception as e:
            self.stdout.write(f"⚠️ API documentation generation failed: {e}")

    def generate_endpoints_docs(self, output_dir):
        """Generate human-readable API endpoints documentation."""
        endpoints_file = os.path.join(output_dir, "api_endpoints.md")

        with open(endpoints_file, "w") as f:
            f.write("# SEIM API Endpoints\n\n")
            f.write(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

            # Document known API endpoints
            f.write("## Authentication\n\n")
            f.write("- `POST /api/token/` - JWT token generation\n")
            f.write("- `POST /api/token/refresh/` - Token refresh\n")
            f.write("- `POST /api/accounts/register/` - User registration\n")
            f.write("- `POST /api/accounts/verify-email/` - Email verification\n")
            f.write("- `POST /api/accounts/password-reset/` - Password reset\n\n")

            f.write("## Exchange Programs\n\n")
            f.write("- `GET /api/programs/` - List programs\n")
            f.write("- `POST /api/programs/` - Create program\n")
            f.write("- `GET /api/programs/{id}/` - Get program details\n")
            f.write("- `PUT /api/programs/{id}/` - Update program\n")
            f.write("- `DELETE /api/programs/{id}/` - Delete program\n\n")

            f.write("## Applications\n\n")
            f.write("- `GET /api/applications/` - List applications\n")
            f.write("- `POST /api/applications/` - Create application\n")
            f.write("- `GET /api/applications/{id}/` - Get application details\n")
            f.write("- `PUT /api/applications/{id}/` - Update application\n")
            f.write(
                "- `POST /api/applications/{id}/withdraw/` - Withdraw application\n\n"
            )

            f.write("## Documents\n\n")
            f.write("- `GET /api/documents/` - List documents\n")
            f.write("- `POST /api/documents/` - Upload document\n")
            f.write("- `GET /api/documents/{id}/` - Get document details\n")
            f.write("- `PUT /api/documents/{id}/` - Update document\n")
            f.write("- `DELETE /api/documents/{id}/` - Delete document\n\n")

            f.write("## Notifications\n\n")
            f.write("- `GET /api/notifications/` - List notifications\n")
            f.write("- `POST /api/notifications/` - Create notification\n")
            f.write("- `GET /api/notifications/{id}/` - Get notification details\n\n")

            f.write("## Analytics\n\n")
            f.write("- `GET /api/reports/` - List reports\n")
            f.write("- `GET /api/metrics/` - Get metrics\n")
            f.write("- `GET /api/dashboard-configs/` - Get dashboard configs\n\n")

    def generate_code_docs(self, output_dir, options):
        """Generate code documentation for models, views, and services."""
        self.stdout.write("📝 Generating code documentation...")

        code_docs_file = os.path.join(output_dir, "code_documentation.md")

        with open(code_docs_file, "w") as f:
            f.write("# SEIM Code Documentation\n\n")
            f.write(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

            # Document models
            f.write("## Models\n\n")
            for app_config in apps.get_app_configs():
                if app_config.name in settings.INSTALLED_APPS:
                    f.write(f"### {app_config.verbose_name}\n\n")

                    try:
                        models_module = app_config.import_models()
                        for model in models_module:
                            if hasattr(model, "_meta"):
                                f.write(f"#### {model._meta.verbose_name}\n")
                                f.write(
                                    f"- **Model**: `{model.__module__}.{model.__name__}`\n"
                                )

                                if model.__doc__:
                                    f.write(
                                        f"- **Description**: {model.__doc__.strip()}\n"
                                    )

                                # List fields
                                f.write("- **Fields**:\n")
                                for field in model._meta.fields:
                                    f.write(
                                        f"  - `{field.name}`: {field.__class__.__name__}\n"
                                    )

                                f.write("\n")
                    except Exception as e:
                        f.write(f"Error loading models for {app_config.name}: {e}\n\n")

            # Document services
            f.write("## Services\n\n")
            for app_config in apps.get_app_configs():
                if app_config.name in settings.INSTALLED_APPS:
                    try:
                        services_module = app_config.import_models()
                        if hasattr(services_module, "services"):
                            f.write(f"### {app_config.verbose_name} Services\n\n")
                            # Add service documentation here
                    except Exception:
                        pass

        self.stdout.write(f"  ✅ Code documentation: {code_docs_file}")

    def generate_db_docs(self, output_dir, options):
        """Generate database schema documentation."""
        self.stdout.write("🗄️ Generating database documentation...")

        db_docs_file = os.path.join(output_dir, "database_schema.md")

        with open(db_docs_file, "w") as f:
            f.write("# SEIM Database Schema\n\n")
            f.write(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

            # Get database schema information
            from django.db import connection

            with connection.cursor() as cursor:
                # Get table information - handle both SQLite and PostgreSQL
                if connection.vendor == "sqlite":
                    cursor.execute(
                        """
                        SELECT name as table_name
                        FROM sqlite_master
                        WHERE type='table' AND name NOT LIKE 'sqlite_%'
                        ORDER BY name
                    """
                    )
                    tables = [(row[0], "") for row in cursor.fetchall()]
                else:
                    cursor.execute(
                        """
                        SELECT table_name, '' as table_comment
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """
                    )
                    tables = cursor.fetchall()

                for table_name, table_comment in tables:
                    f.write(f"## {table_name}\n\n")
                    if table_comment:
                        f.write(f"{table_comment}\n\n")

                    # Get column information - handle both SQLite and PostgreSQL
                    if connection.vendor == "sqlite":
                        cursor.execute("PRAGMA table_info(?)", [table_name])
                        columns = cursor.fetchall()

                        f.write(
                            "| Column | Type | Not Null | Default | Primary Key |\n"
                        )
                        f.write(
                            "|--------|------|----------|---------|-------------|\n"
                        )

                        for column_info in columns:
                            column_name = column_info[1]
                            data_type = column_info[2]
                            not_null = "YES" if column_info[3] else "NO"
                            default = column_info[4] or ""
                            primary_key = "YES" if column_info[5] else "NO"
                            f.write(
                                f"| {column_name} | {data_type} | {not_null} | {default} | {primary_key} |\n"
                            )
                    else:
                        cursor.execute(
                            """
                            SELECT column_name, data_type, is_nullable, column_default,
                                   '' as column_comment
                            FROM information_schema.columns
                            WHERE table_name = %s AND table_schema = 'public'
                            ORDER BY ordinal_position
                        """,
                            [table_name],
                        )

                        columns = cursor.fetchall()

                        f.write(
                            "| Column | Type | Nullable | Default | Description |\n"
                        )
                        f.write(
                            "|--------|------|----------|---------|-------------|\n"
                        )

                        for (
                            column_name,
                            data_type,
                            is_nullable,
                            column_default,
                            column_comment,
                        ) in columns:
                            f.write(
                                f'| {column_name} | {data_type} | {is_nullable} | {column_default or ""} | {column_comment or ""} |\n'
                            )

                    f.write("\n")

        self.stdout.write(f"  ✅ Database schema: {db_docs_file}")

    def update_existing_docs(self, output_dir, options):
        """Update existing documentation files with generated content."""
        self.stdout.write("📄 Updating existing documentation...")

        # Update API documentation links
        api_docs_file = os.path.join("documentation", "api_documentation.md")
        if os.path.exists(api_docs_file):
            with open(api_docs_file, "a") as f:
                f.write("\n\n## Generated Documentation\n\n")
                f.write(
                    f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                )
                f.write("- [API Schema](generated/api_schema.yaml)\n")
                f.write("- [API Endpoints](generated/api_endpoints.md)\n")
                f.write("- [Code Documentation](generated/code_documentation.md)\n")
                f.write("- [Database Schema](generated/database_schema.md)\n")

        self.stdout.write("  ✅ Existing documentation updated")
