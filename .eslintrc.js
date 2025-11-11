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
        'plugin:security/recommended',
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
        'no-alert': 'error',
        'no-eval': 'error',
        'no-implied-eval': 'error',
        'no-new-func': 'error',
        'no-script-url': 'error',
        'no-unsafe-finally': 'error',
        'no-unsafe-negation': 'error',
        'no-unsafe-optional-chaining': 'error',
        'no-unsafe-unary-negation': 'error',
        'no-unsafe-regex': 'error',
        'no-unsafe-assignment': 'error',
        'no-unsafe-call': 'error',
        'no-unsafe-member-access': 'error',
        'no-unsafe-return': 'error',
        
        // **Code Quality**
        'complexity': ['error', 10],
        'max-depth': ['error', 4],
        'max-lines': ['error', 300],
        'max-lines-per-function': ['error', 50],
        'max-nested-callbacks': ['error', 3],
        'max-params': ['error', 5],
        'max-statements': ['error', 20],
        'no-magic-numbers': ['error', { ignore: [0, 1, -1, 2, 10, 100, 1000] }],
        'prefer-const': 'error',
        'no-var': 'error',
        'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
        'no-undef': 'error',
        'no-redeclare': 'error',
        'no-shadow': 'error',
        'no-shadow-restricted-names': 'error',
        
        // **Best Practices**
        'eqeqeq': ['error', 'always'],
        'curly': ['error', 'all'],
        'brace-style': ['error', '1tbs'],
        'comma-dangle': ['error', 'never'],
        'comma-spacing': ['error', { before: false, after: true }],
        'comma-style': ['error', 'last'],
        'indent': ['error', 4, { SwitchCase: 1 }],
        'key-spacing': ['error', { beforeColon: false, afterColon: true }],
        'keyword-spacing': ['error', { before: true, after: true }],
        'linebreak-style': ['error', 'unix'],
        'no-multiple-empty-lines': ['error', { max: 2, maxEOF: 1 }],
        'no-trailing-spaces': 'error',
        'object-curly-spacing': ['error', 'always'],
        'quotes': ['error', 'single', { avoidEscape: true }],
        'semi': ['error', 'always'],
        'space-before-blocks': 'error',
        'space-before-function-paren': ['error', 'never'],
        'space-in-parens': ['error', 'never'],
        'space-infix-ops': 'error',
        'spaced-comment': ['error', 'always'],
        
        // **ES6+ Features**
        'arrow-spacing': ['error', { before: true, after: true }],
        'no-duplicate-imports': 'error',
        'no-useless-constructor': 'error',
        'prefer-arrow-callback': 'error',
        'prefer-destructuring': ['error', {
            array: true,
            object: true
        }, {
            enforceForRenamedProperties: false
        }],
        'prefer-template': 'error',
        'template-curly-spacing': ['error', 'never'],
        
        // **Security Rules**
        'security/detect-object-injection': 'error',
        'security/detect-non-literal-regexp': 'error',
        'security/detect-unsafe-regex': 'error',
        'security/detect-buffer-noassert': 'error',
        'security/detect-child-process': 'error',
        'security/detect-disable-mustache-escape': 'error',
        'security/detect-eval-with-expression': 'error',
        'security/detect-no-csrf-before-method-override': 'error',
        'security/detect-non-literal-fs-filename': 'error',
        'security/detect-non-literal-require': 'error',
        'security/detect-possible-timing-attacks': 'error',
        'security/detect-pseudoRandomBytes': 'error',
        
        // **Import Rules**
        'import/no-unresolved': 'error',
        'import/named': 'error',
        'import/default': 'error',
        'import/namespace': 'error',
        'import/no-duplicates': 'error',
        'import/order': ['error', {
            groups: [
                'builtin',
                'external',
                'internal',
                'parent',
                'sibling',
                'index'
            ],
            'newlines-between': 'always',
            alphabetize: {
                order: 'asc',
                caseInsensitive: true
            }
        }],
        
        // **Promise Rules**
        'promise/always-return': 'error',
        'promise/no-return-wrap': 'error',
        'promise/param-names': 'error',
        'promise/catch-or-return': 'error',
        'promise/no-new-statics': 'error',
        'promise/no-return-in-finally': 'error',
        'promise/valid-params': 'error',
        
        // **Unicorn Rules**
        'unicorn/better-regex': 'error',
        'unicorn/catch-error-name': 'error',
        'unicorn/consistent-destructuring': 'error',
        'unicorn/consistent-function-scoping': 'error',
        'unicorn/custom-error-definition': 'error',
        'unicorn/error-message': 'error',
        'unicorn/escape-case': 'error',
        'unicorn/expiring-todo-comments': 'error',
        'unicorn/explicit-length-check': 'error',
        'unicorn/filename-case': ['error', { case: 'kebabCase' }],
        'unicorn/new-for-builtins': 'error',
        'unicorn/no-array-instanceof': 'error',
        'unicorn/no-console-spaces': 'error',
        'unicorn/no-for-loop': 'error',
        'unicorn/no-hex-escape': 'error',
        'unicorn/no-lonely-if': 'error',
        'unicorn/no-new-buffer': 'error',
        'unicorn/no-process-exit': 'error',
        'unicorn/no-unreadable-array-destructuring': 'error',
        'unicorn/no-unsafe-regex': 'error',
        'unicorn/no-unused-properties': 'error',
        'unicorn/no-useless-undefined': 'error',
        'unicorn/number-literal-case': 'error',
        'unicorn/prefer-add-event-listener': 'error',
        'unicorn/prefer-array-find': 'error',
        'unicorn/prefer-array-flat-map': 'error',
        'unicorn/prefer-array-index-of': 'error',
        'unicorn/prefer-array-some': 'error',
        'unicorn/prefer-date-now': 'error',
        'unicorn/prefer-default-parameters': 'error',
        'unicorn/prefer-includes': 'error',
        'unicorn/prefer-math-trunc': 'error',
        'unicorn/prefer-modern-dom-apis': 'error',
        'unicorn/prefer-negative-index': 'error',
        'unicorn/prefer-number-properties': 'error',
        'unicorn/prefer-optional-catch-binding': 'error',
        'unicorn/prefer-prototype-methods': 'error',
        'unicorn/prefer-query-selector': 'error',
        'unicorn/prefer-reflect-apply': 'error',
        'unicorn/prefer-regexp-test': 'error',
        'unicorn/prefer-set-has': 'error',
        'unicorn/prefer-spread': 'error',
        'unicorn/prefer-string-replace-all': 'error',
        'unicorn/prefer-string-slice': 'error',
        'unicorn/prefer-string-starts-ends-with': 'error',
        'unicorn/prefer-string-trim-start-end': 'error',
        'unicorn/prefer-ternary': 'error',
        'unicorn/prefer-type-error': 'error',
        'unicorn/throw-new-error': 'error',
        
        // **JSDoc Rules**
        'jsdoc/check-alignment': 'error',
        'jsdoc/check-examples': 'off',
        'jsdoc/check-indentation': 'error',
        'jsdoc/check-param-names': 'error',
        'jsdoc/check-syntax': 'error',
        'jsdoc/check-tag-names': 'error',
        'jsdoc/check-types': 'error',
        'jsdoc/implements-on-classes': 'error',
        'jsdoc/match-description': 'error',
        'jsdoc/newline-after-description': 'error',
        'jsdoc/no-types': 'off',
        'jsdoc/no-undefined-types': 'off',
        'jsdoc/require-description': 'error',
        'jsdoc/require-description-complete-sentence': 'error',
        'jsdoc/require-example': 'off',
        'jsdoc/require-file-overview': 'off',
        'jsdoc/require-hyphen-before-param-description': 'error',
        'jsdoc/require-jsdoc': ['error', {
            publicOnly: true,
            require: {
                FunctionDeclaration: true,
                MethodDefinition: true,
                ClassDeclaration: true
            }
        }],
        'jsdoc/require-param': 'error',
        'jsdoc/require-param-description': 'error',
        'jsdoc/require-param-name': 'error',
        'jsdoc/require-param-type': 'error',
        'jsdoc/require-returns': 'error',
        'jsdoc/require-returns-description': 'error',
        'jsdoc/require-returns-type': 'error',
        'jsdoc/valid-types': 'error',
        
        // **Prettier Integration**
        'prettier/prettier': ['error', {
            singleQuote: true,
            trailingComma: 'none',
            printWidth: 100,
            tabWidth: 4,
            useTabs: false,
            semi: true,
            bracketSpacing: true,
            arrowParens: 'avoid'
        }]
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