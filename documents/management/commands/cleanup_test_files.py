"""
Management command to clean up test PDF files from the documents directory.
"""

import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Clean up test PDF files from documents directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write("=" * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No files will be deleted"))
        else:
            self.stdout.write(self.style.WARNING("CLEANUP MODE - Files will be deleted"))
        self.stdout.write("=" * 60)
        
        # Get documents directory
        docs_dir = Path(__file__).resolve().parent.parent.parent
        
        # Patterns to match
        patterns = [
            'test*.pdf',
            'old*.pdf',
            'new*.pdf',
        ]
        
        deleted_count = 0
        total_size = 0
        
        for pattern in patterns:
            for pdf_file in docs_dir.glob(pattern):
                file_size = pdf_file.stat().st_size
                size_kb = file_size / 1024
                
                self.stdout.write(
                    f"  {'Would delete' if dry_run else 'Deleting'}: "
                    f"{pdf_file.name} ({size_kb:.1f} KB)"
                )
                
                if not dry_run:
                    pdf_file.unlink()
                
                deleted_count += 1
                total_size += file_size
        
        total_size_mb = total_size / (1024 * 1024)
        
        self.stdout.write("\n" + "=" * 60)
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {'Would clean' if dry_run else 'Cleaned'} {deleted_count} files "
                    f"({total_size_mb:.2f} MB)"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("✓ No test files found"))
        self.stdout.write("=" * 60)
        
        if dry_run:
            self.stdout.write(
                "\nRun without --dry-run to actually delete these files"
            )

