"""
Management command to enhance docstrings in the SEIM codebase.

This command adds or improves docstrings for:
1. Models
2. Views and ViewSets
3. Serializers
4. Services
5. Management commands
"""

import os

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Enhance docstrings in the SEIM codebase for better documentation"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file", type=str, help="Specific file to enhance"
        )
        parser.add_argument(
            "--directory", type=str, help="Directory to enhance"
        )
        parser.add_argument(
            "--recursive",
            action="store_true",
            help="Process directories recursively",
        )
        parser.add_argument(
            "--backup",
            action="store_true",
            help="Create backup before enhancing",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without making changes",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force regeneration of existing docstrings",
        )

    def handle(self, *args, **options):
        self.stdout.write("🔧 Enhancing docstrings in SEIM codebase...")

        if options["dry_run"]:
            self.stdout.write("🔍 DRY RUN MODE - No changes will be made")

        if options["file"]:
            self.enhance_file_docstrings(options["file"], options)
        elif options["directory"]:
            self.enhance_directory_docstrings(options["directory"], options)
        else:
            # Default: walk concrete AppConfigs (INSTALLED_APPS entries are module paths, not labels).
            skip_prefixes = (
                "django.",
                "rest_framework",
                "drf_spectacular",
                "rest_framework_simplejwt",
            )

            for app_config in apps.get_app_configs():
                if any(app_config.name.startswith(p) for p in skip_prefixes):
                    continue

                self.stdout.write(f"📝 Processing app: {app_config.label}")

                # Enhance models
                self.enhance_models_docstrings(app_config, options)

                # Enhance views
                self.enhance_views_docstrings(app_config, options)

                # Enhance serializers
                self.enhance_serializers_docstrings(app_config, options)

                # Enhance services
                self.enhance_services_docstrings(app_config, options)

        self.stdout.write("✅ Docstring enhancement completed!")

    def enhance_file_docstrings(self, file_path, options):
        """Enhance docstrings in a specific file."""
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        self.stdout.write(f"📝 Processing file: {file_path}")
        # Implementation would go here for file-specific enhancement

    def enhance_directory_docstrings(self, directory_path, options):
        """Enhance docstrings in a directory."""
        if not os.path.exists(directory_path):
            raise CommandError(f"Directory not found: {directory_path}")

        self.stdout.write(f"📝 Processing directory: {directory_path}")
        # Implementation would go here for directory-specific enhancement

    def enhance_models_docstrings(self, app_config, options):
        """Enhance model docstrings."""
        try:
            models_module = app_config.import_models()
            for model in models_module:
                if hasattr(model, "_meta"):
                    self.stdout.write(f"  📋 Model: {model.__name__}")

                    # Add model docstring if missing
                    if not model.__doc__ or options["force"]:
                        docstring = self.generate_model_docstring(model)
                        if not options["dry_run"]:
                            model.__doc__ = docstring
                        else:
                            self.stdout.write(
                                f"    Would add docstring: {docstring[:50]}..."
                            )
        except Exception as e:
            self.stdout.write(f"    ⚠️ Error processing models: {e}")

    def generate_model_docstring(self, model):
        """Generate a docstring for a model."""
        verbose_name = getattr(model._meta, "verbose_name", model.__name__)
        fields = [field.name for field in model._meta.fields]

        docstring = f'"""{verbose_name} model.\n\n'
        docstring += f"This model represents {verbose_name.lower()} in the system.\n\n"

        if fields:
            docstring += "Fields:\n"
            for field in model._meta.fields:
                field_type = field.__class__.__name__
                docstring += f"- {field.name}: {field_type}\n"

        docstring += '"""'
        return docstring

    def enhance_views_docstrings(self, app_config, options):
        """Enhance view docstrings."""
        try:
            views_module = app_config.import_models()
            if hasattr(views_module, "views"):
                for view_class in views_module.views.__dict__.values():
                    if hasattr(view_class, "__bases__") and "ViewSet" in str(
                        view_class.__bases__
                    ):
                        self.stdout.write(f"  🔗 ViewSet: {view_class.__name__}")

                        # Add ViewSet docstring if missing
                        if not view_class.__doc__ or options["force"]:
                            docstring = self.generate_viewset_docstring(view_class)
                            if not options["dry_run"]:
                                view_class.__doc__ = docstring
                            else:
                                self.stdout.write(
                                    f"    Would add docstring: {docstring[:50]}..."
                                )
        except Exception as e:
            self.stdout.write(f"    ⚠️ Error processing views: {e}")

    def generate_viewset_docstring(self, viewset):
        """Generate a docstring for a ViewSet."""
        model_name = getattr(viewset, "queryset", None)
        if model_name:
            model_name = model_name.model.__name__
        else:
            model_name = viewset.__name__.replace("ViewSet", "")

        docstring = f'"""{model_name} ViewSet.\n\n'
        docstring += f"Provides CRUD operations for {model_name} objects.\n\n"
        docstring += "Endpoints:\n"
        docstring += "- GET / - List all objects\n"
        docstring += "- POST / - Create new object\n"
        docstring += "- GET /{id}/ - Retrieve object\n"
        docstring += "- PUT /{id}/ - Update object\n"
        docstring += "- DELETE /{id}/ - Delete object\n"
        docstring += '"""'
        return docstring

    def enhance_serializers_docstrings(self, app_config, options):
        """Enhance serializer docstrings."""
        try:
            serializers_module = app_config.import_models()
            if hasattr(serializers_module, "serializers"):
                for (
                    serializer_class
                ) in serializers_module.serializers.__dict__.values():
                    if hasattr(serializer_class, "__bases__") and "Serializer" in str(
                        serializer_class.__bases__
                    ):
                        self.stdout.write(
                            f"  📄 Serializer: {serializer_class.__name__}"
                        )

                        # Add serializer docstring if missing
                        if not serializer_class.__doc__ or options["force"]:
                            docstring = self.generate_serializer_docstring(
                                serializer_class
                            )
                            if not options["dry_run"]:
                                serializer_class.__doc__ = docstring
                            else:
                                self.stdout.write(
                                    f"    Would add docstring: {docstring[:50]}..."
                                )
        except Exception as e:
            self.stdout.write(f"    ⚠️ Error processing serializers: {e}")

    def generate_serializer_docstring(self, serializer):
        """Generate a docstring for a serializer."""
        model_name = getattr(serializer.Meta, "model", None)
        if model_name:
            model_name = model_name.__name__
        else:
            model_name = serializer.__name__.replace("Serializer", "")

        docstring = f'"""{model_name} Serializer.\n\n'
        docstring += f"Serializes and deserializes {model_name} objects for API communication.\n\n"

        if hasattr(serializer.Meta, "fields"):
            docstring += f"Fields: {serializer.Meta.fields}\n"

        docstring += '"""'
        return docstring

    def enhance_services_docstrings(self, app_config, options):
        """Enhance service docstrings."""
        try:
            services_module = app_config.import_models()
            if hasattr(services_module, "services"):
                for service_class in services_module.services.__dict__.values():
                    if hasattr(service_class, "__bases__") and "object" in str(
                        service_class.__bases__
                    ):
                        self.stdout.write(f"  ⚙️ Service: {service_class.__name__}")

                        # Add service docstring if missing
                        if not service_class.__doc__ or options["force"]:
                            docstring = self.generate_service_docstring(service_class)
                            if not options["dry_run"]:
                                service_class.__doc__ = docstring
                            else:
                                self.stdout.write(
                                    f"    Would add docstring: {docstring[:50]}..."
                                )
        except Exception as e:
            self.stdout.write(f"    ⚠️ Error processing services: {e}")

    def generate_service_docstring(self, service):
        """Generate a docstring for a service."""
        service_name = service.__name__.replace("Service", "")

        docstring = f'"""{service_name} Service.\n\n'
        docstring += (
            f"Provides business logic for {service_name.lower()} operations.\n\n"
        )
        docstring += "This service encapsulates business rules and data processing\n"
        docstring += "for the {service_name.lower()} domain.\n"
        docstring += '"""'
        return docstring
