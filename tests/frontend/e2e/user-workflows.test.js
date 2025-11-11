/**
 * E2E Tests for SEIM User Workflows
 * End-to-end testing of complete user journeys
 */

import { TestEnvironment, TestData, DOMUtils, AsyncUtils } from '../utils/test-utils.js';

// NOTE: Browser-dependent E2E tests have been moved to Selenium (see tests/e2e/test_user_workflows.py)
// Only keep tests here that are suitable for Jest/jsdom (unit/integration, not full navigation or real DOM workflows).
// THESE TESTS REQUIRE REAL BROWSER NAVIGATION AND ARE SKIPPED IN JEST

describe.skip('SEIM User Workflows E2E Tests', () => {
    let testEnv;
    let api;
    
    beforeAll(async () => {
        // Setup test environment
        testEnv = new TestEnvironment();
        testEnv.setup();
        
        // Initialize API - Fix the import to use the default export
        const apiModule = await import('../../../static/js/modules/api-enhanced.js');
        api = apiModule.default;
    });
    
    afterAll(async () => {
        // Teardown test environment
        testEnv.teardown();
    });
    
    beforeEach(async () => {
        // Clear DOM
        document.body.innerHTML = `
            <div id="app">
                <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                    <div class="container">
                        <a class="navbar-brand" href="/">SEIM</a>
                        <div class="navbar-nav ms-auto">
                            <a class="nav-link" href="/auth/login" id="login-link">Login</a>
                            <a class="nav-link" href="/auth/register" id="register-link">Register</a>
                        </div>
                    </div>
                </nav>
                <main class="container mt-4">
                    <div id="content"></div>
                </main>
            </div>
        `;
        
        // Clear storage
        localStorage.clear();
        sessionStorage.clear();
        
        // Reset API state
        api.clearCache();
    });
    
    describe('Document Management Workflow', () => {
        test('should complete document upload process', async () => {
            // Mock file upload
            const mockDocument = TestData.createDocument({
                id: 'test-doc-id',
                name: 'test-document.pdf'
            });
            
            global.fetch = jest.fn().mockResolvedValueOnce({
                ok: true,
                status: 201,
                json: async () => TestData.createAPIResponse(mockDocument)
            });
            
            // Navigate to application detail page
            window.location.href = '/applications/test-app-id/';
            
            // Wait for document upload area
            await AsyncUtils.waitForCondition(() => 
                document.querySelector('#document-upload') !== null
            );
            
            // Simulate file upload
            const fileInput = document.querySelector('#document-upload input[type="file"]');
            const file = new File(['test content'], 'test-document.pdf', { type: 'application/pdf' });
            
            DOMUtils.simulateFileUpload(fileInput, file);
            
            // Wait for upload success
            await AsyncUtils.waitForCondition(() => 
                document.querySelector('.alert-success') !== null
            );
            
            // Verify document was uploaded
            const successMessage = document.querySelector('.alert-success');
            expect(successMessage.textContent).toContain('Document uploaded successfully');
        });
        
        test('should handle document upload errors', async () => {
            // Mock upload error
            global.fetch = jest.fn().mockResolvedValueOnce({
                ok: false,
                status: 400,
                json: async () => TestData.createErrorResponse('File size too large', 400)
            });
            
            // Navigate to application detail page
            window.location.href = '/applications/test-app-id/';
            
            // Wait for document upload area
            await AsyncUtils.waitForCondition(() => 
                document.querySelector('#document-upload') !== null
            );
            
            // Simulate file upload with large file
            const fileInput = document.querySelector('#document-upload input[type="file"]');
            const largeFile = new File(['x'.repeat(10 * 1024 * 1024)], 'large-file.pdf', { type: 'application/pdf' });
            
            DOMUtils.simulateFileUpload(fileInput, largeFile);
            
            // Wait for error message
            await AsyncUtils.waitForCondition(() => 
                document.querySelector('.alert-danger') !== null
            );
            
            // Verify error message
            const errorMessage = document.querySelector('.alert-danger');
            expect(errorMessage.textContent).toContain('File size too large');
        });
    });
    
    describe('Application Status Tracking Workflow', () => {
        test('should display application status updates', async () => {
            // Mock application with status updates
            const mockApplication = TestData.createApplication({
                id: 'test-app-id',
                status: 'approved',
                status_history: [
                    { status: 'submitted', date: '2024-01-01' },
                    { status: 'under_review', date: '2024-01-15' },
                    { status: 'approved', date: '2024-01-30' }
                ]
            });
            
            global.fetch = jest.fn().mockResolvedValueOnce({
                ok: true,
                status: 200,
                json: async () => TestData.createAPIResponse(mockApplication)
            });
            
            // Navigate to application detail page
            window.location.href = '/applications/test-app-id/';
            
            // Wait for status display
            await AsyncUtils.waitForCondition(() => 
                document.querySelector('#application-status') !== null
            );
            
            // Verify status is displayed
            const statusElement = document.querySelector('#application-status');
            expect(statusElement.textContent).toContain('approved');
            
            // Verify status history
            const historyElements = document.querySelectorAll('.status-history-item');
            expect(historyElements.length).toBe(3);
        });
        
        test('should handle real-time status updates', async () => {
            // Mock WebSocket or polling for real-time updates
            const mockUpdate = {
                application_id: 'test-app-id',
                new_status: 'approved',
                timestamp: new Date().toISOString()
            };
            
            // Simulate real-time update
            const updateEvent = new CustomEvent('statusUpdate', { detail: mockUpdate });
            document.dispatchEvent(updateEvent);
            
            // Wait for status update
            await AsyncUtils.waitForCondition(() => 
                document.querySelector('#application-status').textContent.includes('approved')
            );
            
            // Verify notification
            const notification = document.querySelector('.notification');
            expect(notification.textContent).toContain('Application approved');
        });
    });
    
    describe('Notification Management Workflow', () => {
        test('should display and handle notifications', async () => {
            // Mock notifications
            const mockNotifications = [
                { id: 1, message: 'Application submitted', type: 'success' },
                { id: 2, message: 'Document uploaded', type: 'info' }
            ];
            
            global.fetch = jest.fn().mockResolvedValueOnce({
                ok: true,
                status: 200,
                json: async () => TestData.createAPIResponse(mockNotifications)
            });
            
            // Navigate to dashboard
            window.location.href = '/dashboard/';
            
            // Wait for notifications
            await AsyncUtils.waitForCondition(() => 
                document.querySelectorAll('.notification').length > 0
            );
            
            // Verify notifications are displayed
            const notifications = document.querySelectorAll('.notification');
            expect(notifications.length).toBe(2);
            
            // Test notification dismissal
            const firstNotification = notifications[0];
            const dismissButton = firstNotification.querySelector('.notification-dismiss');
            dismissButton.click();
            
            // Wait for notification to be removed
            await AsyncUtils.waitForCondition(() => 
                document.querySelectorAll('.notification').length === 1
            );
        });
    });
    
    describe('Error Recovery Workflow', () => {
        test('should handle network errors gracefully', async () => {
            // Mock network error
            global.fetch = jest.fn().mockRejectedValueOnce(new Error('Network error'));
            
            // Navigate to dashboard
            window.location.href = '/dashboard/';
            
            // Wait for error handling
            await AsyncUtils.waitForCondition(() => 
                document.querySelector('#error-display') !== null
            );
            
            // Verify error message is displayed
            const errorDisplay = document.querySelector('#error-display');
            expect(errorDisplay.textContent).toContain('Connection Issue');
            
            // Test retry functionality
            const retryButton = errorDisplay.querySelector('button');
            retryButton.click();
            
            // Wait for retry attempt
            await AsyncUtils.waitForCondition(() => 
                fetch.mock.calls.length > 1
            );
        });
    });
}); 