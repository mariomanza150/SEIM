/**
 * SEIM Frontend ESLint Configuration
 * Comprehensive linting rules for code quality and consistency
 */

module.exports = {
    env: {
        browser: true,
        es2021: true,
        node: true,
        jest: true
    },
    extends: [
        'eslint:recommended',
        // Avoid plugin:security/recommended — it triggers ESLint config validation bugs (circular JSON) on some versions.
        'plugin:jsdoc/recommended',
        'plugin:prettier/recommended'
    ],
    plugins: [
        'security',
        'jsdoc',
        'prettier',
        'import',
        'promise',
        'unicorn'
    ],
    parserOptions: {
        ecmaVersion: 2021,
        sourceType: 'module',
        ecmaFeatures: {
            jsx: false
        }
    },
    globals: {
        // SEIM-specific globals
        SEIM_LOGGER: 'readonly',
        SEIM_API: 'readonly',
        SEIM_AUTH: 'readonly',
        SEIM_UI: 'readonly',
        SEIM_ACCESSIBILITY: 'readonly',
        SEIM_UI_ENHANCED: 'readonly',
        
        // Test globals
        TestEnvironment: 'readonly',
        TestData: 'readonly',
        DOMUtils: 'readonly',
        AsyncUtils: 'readonly',
        MockUtils: 'readonly',
        TestUtils: 'readonly',
        
        // Browser globals
        console: 'readonly',
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        fetch: 'readonly',
        performance: 'readonly',
        IntersectionObserver: 'readonly',
        ResizeObserver: 'readonly',
        CustomEvent: 'readonly',
        FormData: 'readonly',
        URLSearchParams: 'readonly',
        Headers: 'readonly',
        Request: 'readonly',
        Response: 'readonly'
    },
    rules: {
        // **Error Prevention**
        'no-console': ['warn', { allow: ['warn', 'error'] }],
        'no-debugger': 'error',
        'no-alert': 'off',
        'no-eval': 'error',
        'no-implied-eval': 'error',
        'no-new-func': 'error',
        'no-script-url': 'error',
        'no-unsafe-finally': 'error',
        'no-unsafe-negation': 'error',
        'no-unsafe-optional-chaining': 'error',
        
        // **Code Quality**
        'complexity': 'off',
        'max-depth': ['error', 4],
        'max-lines': 'off',
        'max-lines-per-function': 'off',
        'max-nested-callbacks': 'off',
        'max-params': 'off',
        'max-statements': 'off',
        'no-magic-numbers': 'off',
        'prefer-const': 'off',
        'no-var': 'error',
        'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
        'no-undef': 'off',
        'no-redeclare': 'error',
        'no-shadow': 'off',
        'no-shadow-restricted-names': 'error',
        
        // **Best Practices**
        'eqeqeq': ['error', 'always'],
        'curly': 'off',
        'brace-style': ['error', '1tbs'],
        'comma-dangle': ['error', 'never'],
        'comma-spacing': ['error', { before: false, after: true }],
        'comma-style': ['error', 'last'],
        'indent': 'off',
        'key-spacing': ['error', { beforeColon: false, afterColon: true }],
        'keyword-spacing': ['error', { before: true, after: true }],
        'linebreak-style': 'off',
        'no-multiple-empty-lines': 'off',
        'no-trailing-spaces': 'off',
        'object-curly-spacing': ['error', 'always'],
        'quotes': 'off',
        'semi': ['error', 'always'],
        'space-before-blocks': 'error',
        'space-before-function-paren': 'off',
        'space-in-parens': ['error', 'never'],
        'space-infix-ops': 'error',
        'spaced-comment': ['error', 'always'],
        
        // **ES6+ Features**
        'arrow-spacing': ['error', { before: true, after: true }],
        'no-duplicate-imports': 'error',
        'no-useless-constructor': 'error',
        'prefer-arrow-callback': 'off',
        'prefer-destructuring': 'off',
        'prefer-template': 'off',
        'template-curly-spacing': ['error', 'never'],
        
        // **Security Rules**
        'security/detect-object-injection': 'off',
        'security/detect-non-literal-regexp': 'off',
        'security/detect-unsafe-regex': 'off',
        'security/detect-buffer-noassert': 'off',
        'security/detect-child-process': 'off',
        'security/detect-disable-mustache-escape': 'off',
        'security/detect-eval-with-expression': 'off',
        'security/detect-no-csrf-before-method-override': 'off',
        'security/detect-non-literal-fs-filename': 'off',
        'security/detect-non-literal-require': 'off',
        'security/detect-possible-timing-attacks': 'off',
        'security/detect-pseudoRandomBytes': 'off',
        
        // **Import Rules**
        'import/no-unresolved': 'error',
        'import/named': 'off',
        'import/default': 'off',
        'import/namespace': 'off',
        'import/no-duplicates': 'error',
        'import/order': 'off',
        
        // **Promise Rules**
        'promise/always-return': 'error',
        'promise/no-return-wrap': 'error',
        'promise/param-names': 'off',
        'promise/catch-or-return': 'error',
        'promise/no-new-statics': 'error',
        'promise/no-return-in-finally': 'error',
        'promise/valid-params': 'error',
        
        // **Unicorn Rules**
        'unicorn/better-regex': 'off',
        'unicorn/catch-error-name': 'off',
        'unicorn/consistent-destructuring': 'off',
        'unicorn/consistent-function-scoping': 'off',
        'unicorn/custom-error-definition': 'off',
        'unicorn/error-message': 'off',
        'unicorn/escape-case': 'off',
        'unicorn/expiring-todo-comments': 'off',
        'unicorn/explicit-length-check': 'off',
        'unicorn/filename-case': 'off',
        'unicorn/new-for-builtins': 'off',
        'unicorn/no-array-instanceof': 'off',
        'unicorn/no-console-spaces': 'off',
        'unicorn/no-for-loop': 'off',
        'unicorn/no-hex-escape': 'off',
        'unicorn/no-lonely-if': 'off',
        'unicorn/no-new-buffer': 'off',
        'unicorn/no-process-exit': 'off',
        'unicorn/no-unreadable-array-destructuring': 'off',
        'unicorn/no-unsafe-regex': 'off',
        'unicorn/no-unused-properties': 'off',
        'unicorn/no-useless-undefined': 'off',
        'unicorn/number-literal-case': 'off',
        'unicorn/prefer-add-event-listener': 'off',
        'unicorn/prefer-array-find': 'off',
        'unicorn/prefer-array-flat-map': 'off',
        'unicorn/prefer-array-index-of': 'off',
        'unicorn/prefer-array-some': 'off',
        'unicorn/prefer-date-now': 'off',
        'unicorn/prefer-default-parameters': 'off',
        'unicorn/prefer-includes': 'off',
        'unicorn/prefer-math-trunc': 'off',
        'unicorn/prefer-modern-dom-apis': 'off',
        'unicorn/prefer-negative-index': 'off',
        'unicorn/prefer-number-properties': 'off',
        'unicorn/prefer-optional-catch-binding': 'off',
        'unicorn/prefer-prototype-methods': 'off',
        'unicorn/prefer-query-selector': 'off',
        'unicorn/prefer-reflect-apply': 'off',
        'unicorn/prefer-regexp-test': 'off',
        'unicorn/prefer-set-has': 'off',
        'unicorn/prefer-spread': 'off',
        'unicorn/prefer-string-replace-all': 'off',
        'unicorn/prefer-string-slice': 'off',
        'unicorn/prefer-string-starts-ends-with': 'off',
        'unicorn/prefer-string-trim-start-end': 'off',
        'unicorn/prefer-ternary': 'off',
        'unicorn/prefer-type-error': 'off',
        'unicorn/throw-new-error': 'off',

        // Allow common legacy patterns in older static JS modules
        'no-case-declarations': 'off',
        'no-useless-escape': 'off',
        
        // **JSDoc Rules**
        'jsdoc/check-alignment': 'off',
        'jsdoc/check-examples': 'off',
        'jsdoc/check-indentation': 'off',
        'jsdoc/check-param-names': 'off',
        'jsdoc/check-syntax': 'off',
        'jsdoc/check-tag-names': 'off',
        'jsdoc/check-types': 'off',
        'jsdoc/implements-on-classes': 'off',
        'jsdoc/match-description': 'off',
        'jsdoc/no-types': 'off',
        'jsdoc/no-undefined-types': 'off',
        'jsdoc/require-description': 'off',
        'jsdoc/require-description-complete-sentence': 'off',
        'jsdoc/require-example': 'off',
        'jsdoc/require-file-overview': 'off',
        'jsdoc/require-hyphen-before-param-description': 'off',
        'jsdoc/require-jsdoc': 'off',
        'jsdoc/require-param': 'off',
        'jsdoc/require-param-description': 'off',
        'jsdoc/require-param-name': 'off',
        'jsdoc/require-param-type': 'off',
        'jsdoc/require-returns': 'off',
        'jsdoc/require-returns-description': 'off',
        'jsdoc/require-returns-type': 'off',
        'jsdoc/valid-types': 'off',
        
        // **Prettier Integration**
        'prettier/prettier': 'off'
    },
    overrides: [
        {
            // Test files
            files: ['**/*.test.js', '**/*.spec.js', 'tests/**/*.js'],
            env: {
                jest: true
            },
            rules: {
                'no-magic-numbers': 'off',
                'max-lines': 'off',
                'max-lines-per-function': 'off',
                'complexity': 'off',
                'jsdoc/require-jsdoc': 'off'
            }
        },
        {
            // Configuration files
            files: ['*.config.js', 'webpack.config.js', 'jest.config.js'],
            rules: {
                'no-magic-numbers': 'off',
                'jsdoc/require-jsdoc': 'off'
            }
        },
        {
            // Build scripts
            files: ['scripts/**/*.js'],
            rules: {
                'no-console': 'off',
                'jsdoc/require-jsdoc': 'off'
            }
        }
    ],
    settings: {
        'import/resolver': {
            node: {
                extensions: ['.js', '.jsx']
            }
        },
        jsdoc: {
            mode: 'jsdoc'
        }
    }
}; 