/**
 * Jest Configuration for SEIM Frontend Testing
 * Comprehensive testing setup for JavaScript modules and components
 */

module.exports = {
    // Test environment
    testEnvironment: 'jsdom',
    
    // Test file patterns
    testMatch: [
        '<rootDir>/tests/frontend/**/*.test.js',
        '<rootDir>/tests/frontend/**/*.spec.js',
        '<rootDir>/static/js/**/*.test.js',
        '<rootDir>/static/js/**/*.spec.js'
    ],
    
    // Test setup files
    setupFilesAfterEnv: [
        '<rootDir>/tests/frontend/setup.js'
    ],
    
    // Module resolution
    moduleDirectories: [
        'node_modules',
        '<rootDir>/static/js',
        '<rootDir>/static/js/modules'
    ],
    
    // Module name mapping
    moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/static/js/$1',
        '^@modules/(.*)$': '<rootDir>/static/js/modules/$1',
        '^@utils/(.*)$': '<rootDir>/static/js/modules/$1',
        '^@components/(.*)$': '<rootDir>/static/js/modules/$1'
    },
    
    // Transform configuration
    transform: {
        '^.+\\.js$': 'babel-jest'
    },
    
    // Transform ignore patterns
    transformIgnorePatterns: [
        'node_modules/(?!(sweetalert2|bootstrap)/)'
    ],
    
    // Coverage configuration
    collectCoverage: true,
    collectCoverageFrom: [
        'static/js/**/*.js',
        'static/js/modules/**/*.js',
        '!static/js/**/*.test.js',
        '!static/js/**/*.spec.js',
        '!static/js/sw.js',
        '!static/js/main.js'
    ],
    coverageDirectory: 'coverage/frontend',
    coverageReporters: [
        'text',
        'text-summary',
        'html',
        'lcov',
        'json'
    ],
    coverageThreshold: {
        global: {
            branches: 70,
            functions: 70,
            lines: 70,
            statements: 70
        }
    },
    
    // Test timeout
    testTimeout: 10000,
    
    // Verbose output
    verbose: true,
    
    // Clear mocks between tests
    clearMocks: true,
    resetMocks: true,
    restoreMocks: true,
    
    // Test environment options
    testEnvironmentOptions: {
        url: 'http://localhost:8000',
        pretendToBeVisual: true,
        resources: 'usable'
    },
    
    // Extensions to treat as modules
    moduleFileExtensions: [
        'js',
        'json',
        'jsx',
        'ts',
        'tsx',
        'node'
    ],
    
    // Test path ignore patterns
    testPathIgnorePatterns: [
        '/node_modules/',
        '/staticfiles/',
        '/media/',
        '/coverage/'
    ],
    
    // Watch plugins
    watchPlugins: [
        'jest-watch-typeahead/filename',
        'jest-watch-typeahead/testname'
    ],
    

    
    // Cache directory
    cacheDirectory: '<rootDir>/.jest-cache',
    
    // Maximum workers
    maxWorkers: '50%',
    
    // Force exit
    forceExit: true,
    
    // Detect open handles
    detectOpenHandles: true,
    

    
    // Test location
    testLocationInResults: true,
    
    // Update snapshots
    updateSnapshot: false,
    
    // Snapshot serializers
    snapshotSerializers: [
        'jest-serializer-html'
    ],
    
    // Custom reporters
    reporters: [
        'default',
        [
            'jest-junit',
            {
                outputDirectory: 'coverage/frontend',
                outputName: 'junit.xml',
                classNameTemplate: '{classname}',
                titleTemplate: '{title}',
                ancestorSeparator: ' › ',
                usePathForSuiteName: true
            }
        ]
    ]
}; 