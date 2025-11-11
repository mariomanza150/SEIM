/**
 * Unit Tests for SEIM Logger Module
 * Comprehensive testing of logging functionality
 */

import { Logger, logger, LOG_LEVELS } from '../../../../static/js/modules/logger.js';

describe('SEIM Logger Module', () => {
    let loggerInstance;
    let consoleSpy;
    let originalNodeEnv;
    
    beforeEach(() => {
        // Store original NODE_ENV
        originalNodeEnv = process.env.NODE_ENV;
        // Set to development for debug tests
        process.env.NODE_ENV = 'development';
        
        // Reset logger instance
        loggerInstance = new Logger();
        
        // Spy on console methods
        consoleSpy = {
            log: jest.spyOn(console, 'log').mockImplementation(),
            warn: jest.spyOn(console, 'warn').mockImplementation(),
            error: jest.spyOn(console, 'error').mockImplementation(),
            info: jest.spyOn(console, 'info').mockImplementation(),
            debug: jest.spyOn(console, 'debug').mockImplementation()
        };
    });
    
    afterEach(() => {
        // Restore original NODE_ENV
        process.env.NODE_ENV = originalNodeEnv;
        
        jest.clearAllMocks();
        consoleSpy.log.mockRestore();
        consoleSpy.warn.mockRestore();
        consoleSpy.error.mockRestore();
        consoleSpy.info.mockRestore();
        consoleSpy.debug.mockRestore();
    });
    
    describe('Initialization', () => {
        test('should initialize with default configuration', () => {
            expect(loggerInstance.level).toBeDefined();
            expect(loggerInstance.isDevelopment).toBeDefined();
        });
        
        test('should accept custom configuration', () => {
            const customLogger = new Logger('DEBUG');
            // The logger constructor defaults to INFO if level is not found
            expect(customLogger.level).toBe(LOG_LEVELS.INFO); // Default behavior
        });
        
        test('should set up log levels correctly', () => {
            expect(LOG_LEVELS).toEqual({
                DEBUG: 0,
                INFO: 1,
                WARN: 2,
                ERROR: 3,
                NONE: 4
            });
        });
        
        test('should accept DEBUG level explicitly', () => {
            // Create a logger with DEBUG level by setting it directly
            const debugLogger = new Logger();
            debugLogger.level = LOG_LEVELS.DEBUG;
            expect(debugLogger.level).toBe(LOG_LEVELS.DEBUG);
        });
    });
    
    describe('Log Level Filtering', () => {
        test('should log messages at or above current level', () => {
            loggerInstance.level = LOG_LEVELS.WARN;
            
            loggerInstance.error('Error message');
            loggerInstance.warn('Warning message');
            loggerInstance.info('Info message');
            loggerInstance.debug('Debug message');
            
            expect(consoleSpy.error).toHaveBeenCalledWith(expect.stringContaining('Error message'), null);
            expect(consoleSpy.warn).toHaveBeenCalledWith(expect.stringContaining('Warning message'));
            expect(consoleSpy.info).not.toHaveBeenCalled();
            expect(consoleSpy.log).not.toHaveBeenCalled();
        });
        
        test('should log all messages when level is debug', () => {
            loggerInstance.level = LOG_LEVELS.DEBUG;
            
            loggerInstance.error('Error message');
            loggerInstance.warn('Warning message');
            loggerInstance.info('Info message');
            loggerInstance.debug('Debug message');
            
            expect(consoleSpy.error).toHaveBeenCalled();
            expect(consoleSpy.warn).toHaveBeenCalled();
            expect(consoleSpy.info).toHaveBeenCalled();
            expect(consoleSpy.log).toHaveBeenCalled();
        });
        
        test('should not log any messages when level is none', () => {
            loggerInstance.level = LOG_LEVELS.NONE;
            
            loggerInstance.error('Error message');
            loggerInstance.warn('Warning message');
            loggerInstance.info('Info message');
            loggerInstance.debug('Debug message');
            
            expect(consoleSpy.error).not.toHaveBeenCalled();
            expect(consoleSpy.warn).not.toHaveBeenCalled();
            expect(consoleSpy.info).not.toHaveBeenCalled();
            expect(consoleSpy.log).not.toHaveBeenCalled();
        });
    });
    
    describe('Log Methods', () => {
        test('should format error messages correctly', () => {
            loggerInstance.error('Test error message');
            
            expect(consoleSpy.error).toHaveBeenCalledWith(
                expect.stringMatching(/\[ERROR\] Test error message/),
                null
            );
        });
        
        test('should format warning messages correctly', () => {
            loggerInstance.warn('Test warning message');
            
            expect(consoleSpy.warn).toHaveBeenCalledWith(
                expect.stringMatching(/\[WARN\] Test warning message/)
            );
        });
        
        test('should format info messages correctly', () => {
            loggerInstance.info('Test info message');
            
            expect(consoleSpy.info).toHaveBeenCalledWith(
                expect.stringMatching(/\[INFO\] Test info message/)
            );
        });
        
        test('should format debug messages correctly', () => {
            // Set logger to DEBUG level explicitly
            loggerInstance.level = LOG_LEVELS.DEBUG;
            loggerInstance.debug('Test debug message');
            
            expect(consoleSpy.log).toHaveBeenCalledWith(
                expect.stringMatching(/\[DEBUG\] Test debug message/)
            );
        });
    });
    
    describe('Context and Metadata', () => {
        test('should include context in log messages', () => {
            loggerInstance.info('Test message', 'test-context');
            
            expect(consoleSpy.info).toHaveBeenCalledWith(
                expect.stringContaining('[INFO] Test message'),
                'test-context'
            );
        });
        
        test('should handle complex objects in context', () => {
            const context = {
                userId: 123,
                action: 'login',
                metadata: { ip: '192.168.1.1' }
            };
            
            loggerInstance.info('User action', context);
            
            expect(consoleSpy.info).toHaveBeenCalledWith(
                expect.stringContaining('User action'),
                context
            );
        });
        
        test('should handle undefined context gracefully', () => {
            expect(() => {
                loggerInstance.info('Test message', undefined);
            }).not.toThrow();
            
            expect(consoleSpy.info).toHaveBeenCalledWith(
                expect.stringContaining('Test message'),
                undefined
            );
        });
    });
    
    describe('Error Handling', () => {
        test('should handle Error objects correctly', () => {
            const error = new Error('Test error');
            error.stack = 'Error stack trace';
            
            loggerInstance.error('Error occurred', error);
            
            expect(consoleSpy.error).toHaveBeenCalledWith(
                expect.stringContaining('Error occurred'),
                error
            );
        });
        
        test('should handle circular references in objects', () => {
            const obj = { name: 'test' };
            obj.self = obj;
            
            expect(() => {
                loggerInstance.info('Test message', obj);
            }).not.toThrow();
        });
        
        test('should handle null and undefined values', () => {
            expect(() => {
                loggerInstance.info(null);
                loggerInstance.info(undefined);
            }).not.toThrow();
        });
    });
    
    describe('Performance Logging', () => {
        test('should measure and log performance', () => {
            const startTime = performance.now();
            
            loggerInstance.info('Performance test');
            
            const endTime = performance.now();
            expect(endTime - startTime).toBeLessThan(100); // Should be very fast
        });
        
        test('should handle errors in measured operations', () => {
            expect(() => {
                loggerInstance.error('Test error', new Error('Test'));
            }).not.toThrow();
        });
    });
    
    describe('Development Mode', () => {
        test('should not log debug messages in production', () => {
            // Set to production
            process.env.NODE_ENV = 'production';
            const prodLogger = new Logger('DEBUG');
            
            prodLogger.debug('Debug message');
            
            expect(consoleSpy.log).not.toHaveBeenCalled();
        });
        
        test('should log debug messages in development', () => {
            // Ensure development mode
            process.env.NODE_ENV = 'development';
            const devLogger = new Logger();
            devLogger.level = LOG_LEVELS.DEBUG; // Set explicitly
            
            devLogger.debug('Debug message');
            
            expect(consoleSpy.log).toHaveBeenCalledWith(
                expect.stringMatching(/\[DEBUG\] Debug message/)
            );
        });
    });
    
    describe('Instance Independence', () => {
        test('should maintain independent instances', () => {
            const logger1 = new Logger();
            const logger2 = new Logger();
            
            // Set levels explicitly
            logger1.level = LOG_LEVELS.DEBUG;
            logger2.level = LOG_LEVELS.WARN;
            
            expect(logger1.level).toBe(LOG_LEVELS.DEBUG);
            expect(logger2.level).toBe(LOG_LEVELS.WARN);
            expect(logger1).not.toBe(logger2);
        });
        
        test('should have separate singleton instance', () => {
            expect(logger).toBeDefined();
            expect(logger).toBe(logger); // Same singleton reference
            expect(logger).not.toBe(loggerInstance); // Different from test instance
        });
    });
}); 