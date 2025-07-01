"""
Management command to create performance optimization migration.
"""
from django.core.management.base import BaseCommand
from django.db import models
import os


class Command(BaseCommand):
    help = 'Creates a migration file for performance indexes'

    def handle(self, *args, **options):
        # Get the latest migration number
        migrations_dir = '/app/exchange/migrations'
        migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and f != '__init__.py']
        migration_files.sort()
        
        if migration_files:
            latest_migration = migration_files[-1].replace('.py', '')
            next_number = int(migration_files[-1].split('_')[0]) + 1
        else:
            latest_migration = 'initial'
            next_number = 1
            
        migration_name = f"{next_number:04d}_add_performance_indexes.py"
        migration_path = os.path.join(migrations_dir, migration_name)
        
        migration_content = f'''# Generated migration for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '{latest_migration}'),
    ]

    operations = [
        # Indexes for Exchange model
        migrations.AddIndex(
            model_name='exchange',
            index=models.Index(fields=['status', 'created_at'], name='exchange_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='exchange',
            index=models.Index(fields=['student', 'status'], name='exchange_student_status_idx'),
        ),
        migrations.AddIndex(
            model_name='exchange',
            index=models.Index(fields=['destination_university', 'status'], name='exchange_uni_status_idx'),
        ),
        migrations.AddIndex(
            model_name='exchange',
            index=models.Index(fields=['start_date', 'end_date'], name='exchange_date_range_idx'),
        ),
        
        # Indexes for Document model
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['exchange', 'document_type'], name='document_exchange_type_idx'),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['status', 'created_at'], name='document_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['file_hash'], name='document_hash_idx'),
        ),
        
        # Indexes for Timeline model
        migrations.AddIndex(
            model_name='timeline',
            index=models.Index(fields=['exchange', 'status'], name='timeline_exchange_status_idx'),
        ),
        migrations.AddIndex(
            model_name='timeline',
            index=models.Index(fields=['created_at'], name='timeline_created_idx'),
        ),
        
        # Indexes for Comment model
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['exchange', 'created_at'], name='comment_exchange_created_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['user', 'created_at'], name='comment_user_created_idx'),
        ),
        
        # Indexes for Course model
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['exchange', 'status'], name='course_exchange_status_idx'),
        ),
        
        # Composite indexes for common queries
        migrations.AddIndex(
            model_name='exchange',
            index=models.Index(fields=['status', 'destination_country', 'created_at'], 
                              name='exchange_status_country_idx'),
        ),
    ]
'''
        
        with open(migration_path, 'w') as f:
            f.write(migration_content)
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created migration: {migration_name}')
        )
        self.stdout.write('Run "python manage.py migrate" to apply the indexes.')
