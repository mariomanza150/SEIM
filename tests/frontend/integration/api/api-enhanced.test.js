/**
 * Integration Tests for SEIM Enhanced API Module
 * Comprehensive testing of API functionality, caching, and error handling
 */

import { EnhancedAPI } from '../../../../static/js/modules/api-enhanced.js';
import { TestData } from '../../utils/test-utils.js';

describe('SEIM Enhanced API Integration Tests', () => {
    let api;
    let fetchMock;
    
    beforeEach(() => {
        // Reset API instance
        api = new EnhancedAPI();
        
        // Mock fetch globally
        fetchMock = jest.fn();
        global.fetch = fetchMock;
        
        // Mock AbortSignal.timeout for Node.js test environment
        if (typeof AbortSignal !== 'undefined' && !AbortSignal.timeout) {
            AbortSignal.timeout = jest.fn((timeout) => {
                const controller = new AbortController();
                setTimeout(() => controller.abort(), timeout);
                return controller.signal;
            });
        }
        
        // Clear any existing mocks
        jest.clearAllMocks();
    });
    
    afterEach(() => {
        // Clear cache
        api.clearCache();
        
        // Restore fetch
        global.fetch = undefined;
    });
    
    describe('Request Handling', () => {
        test('should make successful GET request', async () => {
            const mockResponse = TestData.createAPIResponse({ id: 1, name: 'Test' });
            fetchMock.mockResolvedValueOnce({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            const result = await api.get('/api/test');
            
            expect(fetchMock).toHaveBeenCalledWith('/api/test', {
                method: 'GET',
                headers: expect.objectContaining({
                    'Content-Type': 'application/json',
                    'X-Request-ID': expect.any(String)
                }),
                body: undefined,
                signal: expect.any(AbortSignal)
            });
            expect(result).toEqual(mockResponse.data);
        });
        
        test('should make successful POST request with data', async () => {
            const postData = { name: 'Test Item', description: 'Test Description' };
            const mockResponse = TestData.createAPIResponse({ id: 1, ...postData });
            
            fetchMock.mockResolvedValueOnce({
                ok: true,
                status: 201,
                json: async () => mockResponse
            });
            
            const result = await api.post('/api/test', postData);
            
            expect(fetchMock).toHaveBeenCalledWith('/api/test', {
                method: 'POST',
                headers: expect.objectContaining({
                    'Content-Type': 'application/json',
                    'X-Request-ID': expect.any(String)
                }),
                body: JSON.stringify(postData),
                signal: expect.any(AbortSignal)
            });
            expect(result).toEqual(mockResponse.data);
        });
        
        test('should make successful PUT request', async () => {
            const updateData = { name: 'Updated Item' };
            const mockResponse = TestData.createAPIResponse({ id: 1, ...updateData });
            
            fetchMock.mockResolvedValueOnce({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            const result = await api.put('/api/test/1', updateData);
            
            expect(fetchMock).toHaveBeenCalledWith('/api/test/1', {
                method: 'PUT',
                headers: expect.objectContaining({
                    'Content-Type': 'application/json',
                    'X-Request-ID': expect.any(String)
                }),
                body: JSON.stringify(updateData),
                signal: expect.any(AbortSignal)
            });
            expect(result).toEqual(mockResponse.data);
        });
        
        test('should make successful DELETE request', async () => {
            const mockResponse = TestData.createAPIResponse({ success: true });
            
            fetchMock.mockResolvedValueOnce({
                ok: true,
                status: 204,
                json: async () => mockResponse
            });
            
            const result = await api.delete('/api/test/1');
            
            expect(fetchMock).toHaveBeenCalledWith('/api/test/1', {
                method: 'DELETE',
                headers: expect.objectContaining({
                    'Content-Type': 'application/json',
                    'X-Request-ID': expect.any(String)
                }),
                body: undefined,
                signal: expect.any(AbortSignal)
            });
            expect(result).toEqual(mockResponse.data);
        });
    });
    
    describe('Request Deduplication', () => {
        test('should deduplicate concurrent identical requests', async () => {
            const mockResponse = TestData.createAPIResponse({ id: 1, name: 'Test' });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            // Make multiple concurrent requests
            const promises = [
                api.get('/api/test'),
                api.get('/api/test'),
                api.get('/api/test')
            ];
            
            const results = await Promise.all(promises);
            
            // Should only make one actual request
            expect(fetchMock).toHaveBeenCalledTimes(1);
            
            // All results should be the same
            expect(results[0]).toEqual(results[1]);
            expect(results[1]).toEqual(results[2]);
        });
        
        test('should not deduplicate requests with different parameters', async () => {
            const mockResponse = TestData.createAPIResponse({ id: 1, name: 'Test' });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            // Make requests with different parameters
            await api.get('/api/test?page=1');
            await api.get('/api/test?page=2');
            
            // Should make separate requests
            expect(fetchMock).toHaveBeenCalledTimes(2);
        });
    });
    
    describe('Caching', () => {
        test('should cache GET requests', async () => {
            const mockResponse = TestData.createAPIResponse({ id: 1, name: 'Test' });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            // First request
            const result1 = await api.get('/api/test');
            
            // Second request (should be cached)
            const result2 = await api.get('/api/test');
            
            // Should only make one actual request
            expect(fetchMock).toHaveBeenCalledTimes(1);
            expect(result1).toEqual(result2);
        });
        
        test('should respect cache TTL', async () => {
            const mockResponse = TestData.createAPIResponse({ id: 1, name: 'Test' });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            // Set short TTL
            api.setCacheTTL(100); // 100ms
            
            // First request
            await api.get('/api/test');
            
            // Wait for cache to expire
            await new Promise(resolve => setTimeout(resolve, 150));
            
            // Second request (should not be cached)
            await api.get('/api/test');
            
            // Should make two requests
            expect(fetchMock).toHaveBeenCalledTimes(2);
        });
        
        test('should invalidate cache on non-GET requests', async () => {
            const mockResponse = TestData.createAPIResponse({ id: 1, name: 'Test' });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            // Cache a GET request
            await api.get('/api/test');
            
            // Make a POST request (should invalidate cache)
            await api.post('/api/test', { name: 'New Item' });
            
            // Another GET request (should not be cached)
            await api.get('/api/test');
            
            // Should make three requests
            expect(fetchMock).toHaveBeenCalledTimes(3);
        });
    });
    
    describe('Error Handling', () => {
        test('should handle network errors', async () => {
            fetchMock.mockRejectedValueOnce(new Error('Network error'));
            
            await expect(api.get('/api/test')).rejects.toThrow('Network error');
        });
        
        test('should handle HTTP error responses', async () => {
            const errorResponse = TestData.createErrorResponse('Not found', 404);
            fetchMock.mockResolvedValueOnce({
                ok: false,
                status: 404,
                json: async () => errorResponse
            });
            
            await expect(api.get('/api/test')).rejects.toThrow('HTTP 404: Not found');
        });
        
        test('should handle JSON parsing errors', async () => {
            fetchMock.mockResolvedValueOnce({
                ok: true,
                status: 200,
                json: async () => {
                    throw new Error('Invalid JSON');
                }
            });
            
            await expect(api.get('/api/test')).rejects.toThrow('Invalid JSON');
        });
        
        test('should retry failed requests', async () => {
            // First call fails, second succeeds
            fetchMock
                .mockRejectedValueOnce(new Error('Network error'))
                .mockResolvedValueOnce({
                    ok: true,
                    status: 200,
                    json: async () => TestData.createAPIResponse({ id: 1 })
                });
            
            const result = await api.get('/api/test');
            
            expect(fetchMock).toHaveBeenCalledTimes(2);
            expect(result).toEqual({ id: 1 });
        });
        
        test('should respect retry configuration', async () => {
            api.setRetryConfig({ maxRetries: 1, retryDelay: 10 });
            
            fetchMock.mockRejectedValue(new Error('Network error'));
            
            await expect(api.get('/api/test')).rejects.toThrow('Network error');
            
            // Should only retry once (original + 1 retry)
            expect(fetchMock).toHaveBeenCalledTimes(2);
        });
    });
    
    describe('Authentication', () => {
        test('should include authentication headers', async () => {
            const token = 'test-token';
            api.setAuthToken(token);
            
            const mockResponse = TestData.createAPIResponse({ id: 1 });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            await api.get('/api/test');
            
            expect(fetchMock).toHaveBeenCalledWith('/api/test', {
                method: 'GET',
                headers: expect.objectContaining({
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                })
            });
        });
        
        test('should handle authentication errors', async () => {
            api.setAuthToken('invalid-token');
            
            const errorResponse = TestData.createErrorResponse('Unauthorized', 401);
            fetchMock.mockResolvedValue({
                ok: false,
                status: 401,
                json: async () => errorResponse
            });
            
            await expect(api.get('/api/test')).rejects.toThrow('HTTP 401: Unauthorized');
        });
    });
    
    describe('Request Interceptors', () => {
        test('should apply request interceptors', async () => {
            const interceptor = jest.fn((config) => {
                config.headers['X-Custom-Header'] = 'test-value';
                return config;
            });
            
            api.addRequestInterceptor(interceptor);
            
            const mockResponse = TestData.createAPIResponse({ id: 1 });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            await api.get('/api/test');
            
            expect(interceptor).toHaveBeenCalled();
            expect(fetchMock).toHaveBeenCalledWith('/api/test', {
                method: 'GET',
                headers: expect.objectContaining({
                    'X-Custom-Header': 'test-value',
                    'Content-Type': 'application/json'
                })
            });
        });
        
        test('should apply response interceptors', async () => {
            const interceptor = jest.fn((response) => {
                response.data.customField = 'intercepted';
                return response;
            });
            
            api.addResponseInterceptor(interceptor);
            
            const mockResponse = TestData.createAPIResponse({ id: 1 });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            const result = await api.get('/api/test');
            
            expect(interceptor).toHaveBeenCalled();
            expect(result).toHaveProperty('customField', 'intercepted');
        });
    });
    
    describe('Request Queuing', () => {
        test('should queue requests when limit is reached', async () => {
            api.setConcurrencyLimit(1);
            
            const mockResponse = TestData.createAPIResponse({ id: 1 });
            fetchMock.mockImplementation(() => 
                new Promise(resolve => 
                    setTimeout(() => resolve({
                        ok: true,
                        status: 200,
                        json: async () => mockResponse
                    }), 100)
                )
            );
            
            // Start multiple requests
            const promises = [
                api.get('/api/test1'),
                api.get('/api/test2'),
                api.get('/api/test3')
            ];
            
            const results = await Promise.all(promises);
            
            // All should complete successfully
            expect(results).toHaveLength(3);
            expect(results.every(r => r.id === 1)).toBe(true);
        });
        
        test('should handle queue overflow', async () => {
            api.setConcurrencyLimit(1);
            api.setQueueLimit(2);
            
            const mockResponse = TestData.createAPIResponse({ id: 1 });
            fetchMock.mockImplementation(() => 
                new Promise(resolve => 
                    setTimeout(() => resolve({
                        ok: true,
                        status: 200,
                        json: async () => mockResponse
                    }), 200)
                )
            );
            
            // Start more requests than queue can handle
            const promises = [
                api.get('/api/test1'),
                api.get('/api/test2'),
                api.get('/api/test3'),
                api.get('/api/test4') // This should be rejected
            ];
            
            await expect(Promise.all(promises)).rejects.toThrow('Queue limit exceeded');
        });
    });
    
    describe('Performance Monitoring', () => {
        test('should track request performance', async () => {
            const performanceSpy = jest.spyOn(performance, 'now');
            performanceSpy.mockReturnValueOnce(1000).mockReturnValueOnce(1500);
            
            const mockResponse = TestData.createAPIResponse({ id: 1 });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            await api.get('/api/test');
            
            const metrics = api.getPerformanceMetrics();
            expect(metrics.totalRequests).toBe(1);
            expect(metrics.averageResponseTime).toBe(500);
            
            performanceSpy.mockRestore();
        });
        
        test('should track error rates', async () => {
            fetchMock.mockRejectedValue(new Error('Network error'));
            
            try {
                await api.get('/api/test');
            } catch (error) {
                // Expected to fail
            }
            
            const metrics = api.getPerformanceMetrics();
            expect(metrics.totalRequests).toBe(1);
            expect(metrics.errorRate).toBe(1.0);
        });
    });
    
    describe('Cache Management', () => {
        test('should clear specific cache entries', async () => {
            const mockResponse = TestData.createAPIResponse({ id: 1 });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            // Cache two different requests
            await api.get('/api/test1');
            await api.get('/api/test2');
            
            // Clear specific entry
            api.clearCacheEntry('/api/test1');
            
            // Request test1 again (should not be cached)
            await api.get('/api/test1');
            
            // Request test2 again (should be cached)
            await api.get('/api/test2');
            
            // Should make 3 requests total (2 initial + 1 for test1)
            expect(fetchMock).toHaveBeenCalledTimes(3);
        });
        
        test('should clear cache by pattern', async () => {
            const mockResponse = TestData.createAPIResponse({ id: 1 });
            fetchMock.mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            });
            
            // Cache multiple requests
            await api.get('/api/users');
            await api.get('/api/users/1');
            await api.get('/api/programs');
            
            // Clear all user-related cache
            api.clearCacheByPattern('/api/users');
            
            // Request users again (should not be cached)
            await api.get('/api/users');
            
            // Request programs again (should be cached)
            await api.get('/api/programs');
            
            // Should make 4 requests total (3 initial + 1 for users)
            expect(fetchMock).toHaveBeenCalledTimes(4);
        });
    });
}); 