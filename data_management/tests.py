from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.models import Role, User

from .admin import BulkOperationAdmin, DataOperationLogAdmin
from .models import BulkOperation, DataExport, DataImport, DataOperationLog, DataPermission, DemoDataSet


class DataManagementViewTests(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name='data-manager')
        self.user = User.objects.create_user(
            username='datauser',
            email='data@example.com',
            password='testpass123',
            is_staff=True,
        )
        self.user.roles.add(self.role)
        self.client.force_login(self.user)

        self.bulk_operation = BulkOperation.objects.create(
            name='Deactivate stale users',
            operation_type='USER_DEACTIVATE',
            description='Disable inactive users in bulk.',
        )
        self.export_config = DataExport.objects.create(
            name='Export users',
            model_name='accounts.user',
            format='CSV',
            created_by=self.user,
        )
        self.import_config = DataImport.objects.create(
            name='Import users',
            model_name='accounts.user',
            format='CSV',
            created_by=self.user,
        )
        self.demo_dataset = DemoDataSet.objects.create(
            name='Demo cohort',
            description='Sample data set for demos.',
            created_by=self.user,
        )

    def test_index_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('data_management:index'))
        self.assertEqual(response.status_code, 302)

    def test_index_lists_only_permitted_sections(self):
        self.grant_permission('demo_data', 'VIEW')
        response = self.client.get(reverse('data_management:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('data_management:demo_data_setup'))
        self.assertNotContains(response, reverse('data_management:bulk_operations'))

    def test_index_shows_message_when_no_sections(self):
        response = self.client.get(reverse('data_management:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'do not have permission')

    def grant_permission(self, model_name, permission_type):
        return DataPermission.objects.create(
            role=self.role,
            model_name=model_name,
            permission_type=permission_type,
            is_active=True,
        )

    def test_execute_bulk_operation_queues_log(self):
        self.grant_permission('bulk_operation', 'VIEW')
        self.grant_permission('bulk_operation', 'UPDATE')

        response = self.client.post(
            reverse('data_management:execute_bulk_operation', args=[self.bulk_operation.id])
        )

        self.assertRedirects(response, reverse('data_management:bulk_operations'))
        log = DataOperationLog.objects.get(operation_type='BULK_UPDATE')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.model_name, self.bulk_operation.operation_type)
        self.assertEqual(log.status, 'PENDING')
        self.assertEqual(log.operation_details['operation_id'], str(self.bulk_operation.id))

    def test_execute_export_queues_log(self):
        self.grant_permission('data_export', 'VIEW')
        self.grant_permission('data_export', 'EXPORT')

        response = self.client.post(
            reverse('data_management:execute_export', args=[self.export_config.id])
        )

        self.assertRedirects(response, reverse('data_management:data_exports'))
        log = DataOperationLog.objects.get(operation_type='EXPORT')
        self.assertEqual(log.model_name, self.export_config.model_name)
        self.assertEqual(log.operation_details['export_id'], str(self.export_config.id))

    def test_execute_import_requires_uploaded_file(self):
        self.grant_permission('data_import', 'VIEW')
        self.grant_permission('data_import', 'IMPORT')

        response = self.client.post(
            reverse('data_management:execute_import', args=[self.import_config.id]),
            follow=True,
        )

        self.assertRedirects(response, reverse('data_management:data_imports'))
        self.assertContains(response, 'Please choose a file to import.')
        self.assertFalse(DataOperationLog.objects.filter(operation_type='IMPORT').exists())

    def test_execute_import_queues_log_with_file(self):
        self.grant_permission('data_import', 'VIEW')
        self.grant_permission('data_import', 'IMPORT')

        response = self.client.post(
            reverse('data_management:execute_import', args=[self.import_config.id]),
            {
                'file': SimpleUploadedFile(
                    'users.csv',
                    b'email,username,first_name,last_name,language,language_level,gpa\nalice@example.com,alice, Alice , Student ,English,B2,3.7\n',
                    content_type='text/csv',
                )
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('data_management:data_imports'))
        log = DataOperationLog.objects.get(operation_type='IMPORT')
        self.assertEqual(log.file_path, 'users.csv')
        self.assertEqual(log.operation_details['import_id'], str(self.import_config.id))
        self.assertEqual(log.status, 'COMPLETED')
        self.assertEqual(log.record_count, 1)
        self.assertEqual(log.operation_details['created_count'], 1)
        imported_user = User.objects.get(email='alice@example.com')
        self.assertTrue(imported_user.has_role('student'))
        self.assertEqual(imported_user.first_name, 'Alice')
        self.assertEqual(imported_user.profile.language, 'English')
        self.assertEqual(imported_user.profile.language_level, 'B2')
        self.assertEqual(imported_user.profile.gpa, 3.7)
        self.assertContains(response, 'Student import completed.')

    def test_execute_import_updates_existing_student_by_email(self):
        self.grant_permission('data_import', 'VIEW')
        self.grant_permission('data_import', 'IMPORT')
        student_role, _ = Role.objects.get_or_create(name='student')
        existing_user = User.objects.create_user(
            username='existing-student',
            email='existing@example.com',
            password='testpass123',
        )
        existing_user.roles.add(student_role)

        response = self.client.post(
            reverse('data_management:execute_import', args=[self.import_config.id]),
            {
                'file': SimpleUploadedFile(
                    'students.csv',
                    b'email,first_name,last_name,language,language_level,gpa\nexisting@example.com,Updated,Student,Spanish,C1,3.9\n',
                    content_type='text/csv',
                )
            },
        )

        self.assertRedirects(response, reverse('data_management:data_imports'))
        existing_user.refresh_from_db()
        self.assertEqual(existing_user.first_name, 'Updated')
        self.assertEqual(existing_user.last_name, 'Student')
        self.assertEqual(existing_user.profile.language, 'Spanish')
        self.assertEqual(existing_user.profile.language_level, 'C1')
        self.assertEqual(existing_user.profile.gpa, 3.9)
        log = DataOperationLog.objects.get(operation_type='IMPORT')
        self.assertEqual(log.operation_details['updated_count'], 1)
        self.assertEqual(log.operation_details['created_count'], 0)

    def test_demo_data_setup_queues_log(self):
        self.grant_permission('demo_data', 'VIEW')
        self.grant_permission('demo_data', 'CREATE')

        response = self.client.post(
            reverse('data_management:execute_demo_setup', args=[self.demo_dataset.id])
        )

        self.assertRedirects(response, reverse('data_management:demo_data_setup'))
        log = DataOperationLog.objects.get(operation_type='DEMO_SETUP')
        self.assertEqual(log.operation_details['dataset_id'], str(self.demo_dataset.id))

    def test_database_reset_requires_explicit_confirmation(self):
        self.grant_permission('database', 'VIEW')
        self.grant_permission('database', 'DELETE')

        response = self.client.post(
            reverse('data_management:execute_database_reset'),
            {'confirm': 'NOPE'},
            follow=True,
        )

        self.assertRedirects(response, reverse('data_management:database_reset'))
        self.assertContains(response, 'confirm the database reset request.')
        self.assertFalse(DataOperationLog.objects.filter(operation_type='DB_RESET').exists())

    def test_database_reset_queues_log_when_confirmed(self):
        self.grant_permission('database', 'VIEW')
        self.grant_permission('database', 'DELETE')

        response = self.client.post(
            reverse('data_management:execute_database_reset'),
            {'confirm': 'RESET'},
        )

        self.assertRedirects(response, reverse('data_management:database_reset'))
        log = DataOperationLog.objects.get(operation_type='DB_RESET')
        self.assertEqual(log.model_name, 'database')
        self.assertTrue(log.operation_details['confirmed'])

    def test_cleanup_requires_selection(self):
        self.grant_permission('data_cleanup', 'VIEW')
        self.grant_permission('data_cleanup', 'DELETE')

        response = self.client.post(
            reverse('data_management:execute_data_cleanup'),
            follow=True,
        )

        self.assertRedirects(response, reverse('data_management:data_cleanup'))
        self.assertContains(response, 'Select at least one cleanup operation.')
        self.assertFalse(DataOperationLog.objects.filter(operation_type='CLEANUP').exists())

    def test_cleanup_queues_log_for_selected_operations(self):
        self.grant_permission('data_cleanup', 'VIEW')
        self.grant_permission('data_cleanup', 'DELETE')

        response = self.client.post(
            reverse('data_management:execute_data_cleanup'),
            {'clean_orphaned': 'on', 'clean_invalid': 'on'},
        )

        self.assertRedirects(response, reverse('data_management:data_cleanup'))
        log = DataOperationLog.objects.get(operation_type='CLEANUP')
        self.assertEqual(
            log.operation_details['cleanup_options'],
            {
                'clean_orphaned': True,
                'clean_duplicates': False,
                'clean_invalid': True,
            },
        )


class DataManagementAdminTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.role = Role.objects.create(name='viewer')
        self.user = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='testpass123',
            is_staff=True,
        )
        self.user.roles.add(self.role)
        self.bulk_operation = BulkOperation.objects.create(
            name='Bulk viewer test',
            operation_type='USER_EXPORT',
            description='Visible only with matching permission.',
        )
        self.owned_log = DataOperationLog.objects.create(
            user=self.user,
            operation_type='EXPORT',
            model_name='accounts.user',
            status='PENDING',
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123',
            is_staff=True,
        )
        self.other_log = DataOperationLog.objects.create(
            user=self.other_user,
            operation_type='EXPORT',
            model_name='accounts.user',
            status='PENDING',
        )

    def _request_for(self, user):
        request = self.factory.get('/seim/admin/')
        request.user = user
        return request

    def test_bulk_operation_admin_queryset_requires_view_permission(self):
        model_admin = BulkOperationAdmin(BulkOperation, admin.site)

        queryset = model_admin.get_queryset(self._request_for(self.user))

        self.assertEqual(queryset.count(), 0)

    def test_bulk_operation_admin_queryset_returns_records_with_permission(self):
        DataPermission.objects.create(
            role=self.role,
            model_name='bulk_operation',
            permission_type='VIEW',
            is_active=True,
        )
        model_admin = BulkOperationAdmin(BulkOperation, admin.site)

        queryset = model_admin.get_queryset(self._request_for(self.user))

        self.assertEqual(list(queryset), [self.bulk_operation])

    def test_data_operation_log_admin_only_shows_user_logs(self):
        DataPermission.objects.create(
            role=self.role,
            model_name='bulk_operation',
            permission_type='VIEW',
            is_active=True,
        )
        model_admin = DataOperationLogAdmin(DataOperationLog, admin.site)

        queryset = model_admin.get_queryset(self._request_for(self.user))

        self.assertEqual(list(queryset), [self.owned_log])
