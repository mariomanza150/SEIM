<!--
File: docs/CODE_STYLE.md
Title: Code Style Guide
Purpose: Define and enforce consistent coding standards for the SEIM project across all languages and frameworks.
-->

# Code Style Guide

## Purpose
This document outlines the coding standards and best practices for the SEIM project to ensure code quality, maintainability, and consistency across the codebase.

## Revision History
| Date       | Author      | Description                      |
|------------|-------------|----------------------------------|
| 2025-05-31 | Documentation Team | Added template compliance, title, purpose, and revision history. |

## Python Style Guide

### General Rules
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 79 characters
- Use descriptive variable and function names
- Add docstrings to all modules, classes, and functions

### Naming Conventions
```python
# Classes use CamelCase
class ExchangeApplication:
    pass

# Functions and variables use snake_case
def process_application(student_id):
    application_status = "submitted"
    return application_status

# Constants use UPPER_SNAKE_CASE
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_TIMEOUT = 30
```

### Docstrings
```python
def calculate_gpa(grades: List[float]) -> float:
    """
    Calculate the Grade Point Average from a list of grades.
    
    Args:
        grades: List of numerical grades (0.0 to 4.0 scale)
    
    Returns:
        The calculated GPA as a float
    
    Raises:
        ValueError: If grades list is empty or contains invalid values
    
    Example:
        >>> calculate_gpa([3.5, 4.0, 3.0])
        3.5
    """
    if not grades:
        raise ValueError("Grades list cannot be empty")
    return sum(grades) / len(grades)
```

### Imports
```python
# Standard library imports first
import os
import sys
from datetime import datetime

# Third-party imports
import django
from rest_framework import serializers

# Local application imports
from exchange.models import Exchange
from exchange.services.workflow import WorkflowEngine
```

## Django Specific Guidelines

### Models
```python
class Exchange(models.Model):
    """Exchange application model."""
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exchanges'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exchange Application'
        verbose_name_plural = 'Exchange Applications'
    
    def __str__(self):
        return f"{self.student.username} - {self.status}"
```

### Views
```python
class ExchangeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Exchange operations.
    
    Provides CRUD operations and custom actions for exchange applications.
    """
    
    queryset = Exchange.objects.all()
    serializer_class = ExchangeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        if user.is_student:
            return self.queryset.filter(student=user)
        return self.queryset
    
    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """Perform workflow transition."""
        exchange = self.get_object()
        new_status = request.data.get('status')
        # Implementation...
```

### Serializers
```python
class ExchangeSerializer(serializers.ModelSerializer):
    """Serializer for Exchange model."""
    
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    available_transitions = serializers.SerializerMethodField()
    
    class Meta:
        model = Exchange
        fields = [
            'id', 'student', 'student_name', 'status',
            'created_at', 'available_transitions'
        ]
        read_only_fields = ['created_at']
    
    def get_available_transitions(self, obj):
        """Get available workflow transitions."""
        return obj.get_available_transitions()
```

### Services
```python
class WorkflowService:
    """Service for handling workflow operations."""
    
    def __init__(self, exchange: Exchange):
        self.exchange = exchange
    
    def transition_to(self, new_status: str, user: User) -> bool:
        """
        Transition exchange to new status.
        
        Args:
            new_status: Target status
            user: User performing the transition
        
        Returns:
            Success status
        
        Raises:
            PermissionDenied: If user lacks permission
            ValidationError: If transition is invalid
        """
        if not self.can_transition_to(new_status, user):
            raise PermissionDenied("Invalid transition")
        
        self.exchange.status = new_status
        self.exchange.save()
        self.log_transition(new_status, user)
        return True
```

## JavaScript/TypeScript Style Guide

### General Rules
- Use 2 spaces for indentation
- Use semicolons
- Use single quotes for strings
- Use `const` and `let`, avoid `var`
- Use arrow functions where appropriate

### Naming Conventions
```javascript
// Constants use UPPER_CASE
const MAX_RETRIES = 3;
const API_TIMEOUT = 5000;

// Classes use PascalCase
class ExchangeForm {
  constructor() {
    this.fields = [];
  }
}

// Functions and variables use camelCase
function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

const userEmail = 'user@example.com';
```

### Modern JavaScript
```javascript
// Use destructuring
const { name, email } = user;

// Use template literals
const message = `Welcome, ${name}!`;

// Use async/await
async function fetchUserData(userId) {
  try {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}

// Use arrow functions
const doubleNumbers = numbers.map(n => n * 2);

// Use default parameters
function greetUser(name = 'Guest') {
  return `Hello, ${name}!`;
}
```

### React/JSX Guidelines
```jsx
// Component names use PascalCase
function ExchangeList({ exchanges, onSelect }) {
  return (
    <div className="exchange-list">
      {exchanges.map(exchange => (
        <ExchangeItem
          key={exchange.id}
          exchange={exchange}
          onClick={() => onSelect(exchange)}
        />
      ))}
    </div>
  );
}

// Use functional components with hooks
function ExchangeForm() {
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/exchanges', formData);
      // Handle success
    } catch (error) {
      setErrors(error.response.data);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}
```

## CSS/SCSS Style Guide

### General Rules
- Use kebab-case for class names
- Use meaningful class names
- Keep specificity low
- Mobile-first approach
- Use CSS variables for theme values

### Example
```scss
// Variables
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --border-radius: 4px;
  --spacing-unit: 8px;
}

// Component styles
.exchange-card {
  border: 1px solid #ddd;
  border-radius: var(--border-radius);
  padding: calc(var(--spacing-unit) * 2);
  
  &__header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--spacing-unit);
  }
  
  &__title {
    font-size: 1.25rem;
    font-weight: bold;
    color: var(--primary-color);
  }
  
  &__status {
    padding: 4px 8px;
    border-radius: var(--border-radius);
    background-color: var(--secondary-color);
    color: white;
    
    &--approved {
      background-color: #28a745;
    }
    
    &--rejected {
      background-color: #dc3545;
    }
  }
}

// Responsive design
@media (max-width: 768px) {
  .exchange-card {
    &__header {
      flex-direction: column;
    }
  }
}
```

## Git Commit Guidelines

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(exchange): add workflow transition API

- Implement transition endpoint
- Add permission checks
- Update workflow service
- Add tests for transitions

Closes #123

---

fix(auth): resolve JWT token expiration issue

Token expiration was not properly handled in the refresh endpoint.
This commit fixes the issue by checking token validity before refresh.

Fixes #456

---

docs(api): update exchange endpoint documentation

- Add new transition endpoint docs
- Update response examples
- Fix typos in descriptions
```

## Code Review Guidelines

### Before Submitting PR
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Code has been self-reviewed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No console.log or debug statements

### Review Focus
1. **Logic and Functionality**: Does it work correctly?
2. **Code Quality**: Is it readable and maintainable?
3. **Performance**: Are there optimization opportunities?
4. **Security**: Any vulnerabilities?
5. **Testing**: Adequate test coverage?
6. **Documentation**: Clear and updated?

### Reviewer Guidelines
- Be constructive and respectful
- Explain the reasoning behind suggestions
- Suggest alternatives when rejecting
- Acknowledge good practices
- Consider the bigger picture

## Linting and Formatting

### Python
```bash
# Run flake8
flake8 exchange/

# Run black formatter
black exchange/

# Run isort for imports
isort exchange/
```

### JavaScript
```bash
# Run ESLint
eslint src/

# Run Prettier
prettier --write src/
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.14.0
    hooks:
      - id: eslint
```

## Exceptions and Error Handling

### Python
```python
class ExchangeError(Exception):
    """Base exception for exchange-related errors."""
    pass

class WorkflowError(ExchangeError):
    """Raised when workflow operations fail."""
    pass

def process_application(exchange_id):
    try:
        exchange = Exchange.objects.get(id=exchange_id)
        workflow = WorkflowService(exchange)
        workflow.transition_to('submitted')
    except Exchange.DoesNotExist:
        logger.error(f"Exchange {exchange_id} not found")
        raise ExchangeError("Exchange not found")
    except WorkflowError as e:
        logger.error(f"Workflow error: {e}")
        raise
    except Exception as e:
        logger.exception("Unexpected error processing application")
        raise ExchangeError("Processing failed") from e
```

### JavaScript
```javascript
class APIError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

async function submitApplication(data) {
  try {
    const response = await api.post('/exchanges', data);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new APIError(
        error.response.data.message,
        error.response.status
      );
    }
    throw new Error('Network error');
  }
}
```

## Performance Guidelines

### Database Queries
```python
# Bad: N+1 queries
exchanges = Exchange.objects.all()
for exchange in exchanges:
    print(exchange.student.email)  # Extra query for each exchange

# Good: Eager loading
exchanges = Exchange.objects.select_related('student').all()
for exchange in exchanges:
    print(exchange.student.email)  # No extra queries

# Good: Prefetch for many-to-many
exchanges = Exchange.objects.prefetch_related('documents').all()
```

### Caching
```python
from django.core.cache import cache

def get_exchange_stats(user_id):
    cache_key = f'exchange_stats_{user_id}'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = calculate_expensive_stats(user_id)
        cache.set(cache_key, stats, timeout=3600)  # 1 hour
    
    return stats
```

## Security Guidelines

### Input Validation
```python
# Always validate user input
serializer = ExchangeSerializer(data=request.data)
if not serializer.is_valid():
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

# Use Django forms for additional validation
form = ExchangeForm(request.POST)
if form.is_valid():
    form.save()
```

### SQL Injection Prevention
```python
# Bad: String concatenation
query = f"SELECT * FROM exchanges WHERE status = '{status}'"

# Good: Parameterized queries
Exchange.objects.filter(status=status)

# Good: Raw queries with params
Exchange.objects.raw(
    "SELECT * FROM exchanges WHERE status = %s",
    [status]
)
```

### XSS Prevention
```python
# In templates, Django auto-escapes
{{ user_input }}

# For manual escaping
from django.utils.html import escape
safe_input = escape(user_input)

# In JavaScript
const safeHtml = DOMPurify.sanitize(userHtml);
```

## Accessibility Guidelines

### HTML
```html
<!-- Use semantic HTML -->
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/exchanges">Exchanges</a></li>
    <li><a href="/documents">Documents</a></li>
  </ul>
</nav>

<!-- Add ARIA labels -->
<button aria-label="Close dialog" onclick="closeModal()">
  <span aria-hidden="true">&times;</span>
</button>

<!-- Form labels -->
<label for="email">Email Address</label>
<input type="email" id="email" name="email" required>
```

### Color Contrast
- Ensure text has sufficient contrast (WCAG AA compliance)
- Don't rely on color alone to convey information
- Test with color blindness simulators

## Documentation Standards

### Code Comments
```python
# Good: Explains why, not what
# We need to check user permissions here because managers
# can view all exchanges, but students can only see their own
if not user.has_perm('exchange.view_all'):
    queryset = queryset.filter(student=user)

# Bad: Redundant comment
# Increment counter by 1
counter += 1
```

### README Files
Every major directory should have a README explaining:
- Purpose of the directory
- Key files and their roles
- How to use or extend the code
- Dependencies or requirements

## Testing Standards

### Test Naming
```python
def test_student_can_only_view_own_exchanges():
    """Test that students can only access their own exchange applications."""
    pass

def test_manager_can_view_all_exchanges():
    """Test that managers have access to all exchange applications."""
    pass
```

### Test Structure
```python
class TestExchangeWorkflow(TestCase):
    """Test suite for exchange workflow transitions."""
    
    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user('student@test.com')
        self.manager = User.objects.create_user(
            'manager@test.com',
            is_manager=True
        )
    
    def test_valid_transition(self):
        """Test valid status transition."""
        # Arrange
        exchange = Exchange.objects.create(
            student=self.student,
            status='draft'
        )
        
        # Act
        result = exchange.transition_to('submitted')
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(exchange.status, 'submitted')
    
    def tearDown(self):
        """Clean up test data."""
        Exchange.objects.all().delete()
        User.objects.all().delete()
```

## Continuous Integration

### GitHub Actions
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest
    - name: Run linting
      run: |
        flake8 exchange/
        black --check exchange/
```

This comprehensive style guide ensures consistency across the SEIM codebase and helps maintain high code quality standards.
