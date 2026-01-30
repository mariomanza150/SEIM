# SEIM Developer Guide

## Introduction
This guide is for developers working on SEIM (Student Exchange Information Manager). The application is production-ready with a complete Django backend and Bootstrap 5 frontend.

---

## 🏗️ Project Structure

### **Core Apps:**
- **`exchange/`**: Student exchange workflows (applications, programs, workflow logic)
- **`notifications/`**: Email and in-app notification logic
- **`documents/`**: Document processing, upload, and validation
- **`accounts/`**: Custom user management and authentication
- **`application_forms/`**: Dynamic form builder and management
- **`grades/`**: Grade translation system for international students
- **`core/`**: Shared utilities, base models, and project-wide logic
- **`analytics/`**: Dashboards, metrics, and reporting
- **`api/`**: RESTful endpoints and third-party integrations
- **`dashboard/`**: Admin and user dashboards (UI/UX)
- **`plugins/`**: Modular plugin system for custom workflows
- **`frontend/`**: Django-based frontend with Bootstrap 5

### **Key Models:**
- **User**: Custom user model with email verification, lockout policy
- **Program**: Exchange programs with eligibility criteria (GPA, language)
- **Application**: Student applications with workflow states
- **Document**: File uploads with validation and resubmission
- **TimelineEvent**: Audit log for all critical actions
- **DynamicForm**: Dynamic application forms using django-dynforms

### **Dynamic Form Builder:**
- **Enhanced Form Builder**: Visual drag-and-drop interface at `/api/application-forms/builder/`
- **Field Types**: Text, textarea, email, number, date, select, checkbox, radio, file upload (9 types)
- **Real-time Preview**: See forms as you build them
- **JSON Schema Storage**: Standards-based storage in PostgreSQL
- **Field Configuration**: Labels, placeholders, required flags, help text, options
- **Integration**: Forms can be attached to exchange programs
- **Documentation**: See [Form Builder Guide](documentation/form_builder_guide.md)

---

## 🚀 Development Environment

### **Primary Development (Docker - Required)**

> **⚠️ Core development outside Docker is not supported. All backend development, testing, and documentation generation must be performed inside Docker containers to avoid host OS issues.**

### **Quick Start:**
```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create demo data
docker-compose exec web python manage.py create_demo_data

# Access the application
# Web: http://localhost:8000/
# Admin: http://localhost:8000/admin/
# API Docs: http://localhost:8000/api/docs/
```

### **Admin Access:**
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@seim.local`

---

## 🐍 Virtual Environment Setup (E2E Testing & Local Development)

> **⚠️ Virtual environments are required for Selenium E2E tests and some local development tools that run from the host OS.**

### **Virtual Environment Setup:**

#### **1. Create Virtual Environment (One-time setup):**
```bash
# Windows PowerShell
python -m venv .venv

# Linux/macOS
python3 -m venv .venv
```

#### **2. Activate Virtual Environment:**
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

#### **3. Install Development Dependencies:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install all development dependencies
pip install -r requirements-dev.txt
```

#### **4. Verify Installation:**
```bash
# Check if Django and other key packages are available
python -c "import django; print(f'Django {django.get_version()}')"
python -c "import selenium; print(f'Selenium {selenium.__version__}')"
```

### **When to Use Virtual Environment:**

#### **✅ Required for:**
- **Selenium E2E Tests**: Browser automation tests that run from host OS
- **Local Development Tools**: Code quality checks, documentation generation
- **Frontend Testing**: Jest tests and frontend build tools
- **CI/CD Scripts**: Local testing of deployment scripts

#### **❌ Not Required for:**
- **Backend Development**: Use Docker containers instead
- **Database Operations**: Use `docker-compose exec web` commands
- **Django Management Commands**: Use `docker-compose exec web python manage.py`

### **Virtual Environment Workflow:**

#### **For E2E Testing:**
```bash
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Ensure Django server is running in Docker
docker-compose up -d

# 3. Run Selenium E2E tests
make test-selenium

# 4. Deactivate when done
deactivate
```

#### **For Local Development Tools:**
```bash
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Run code quality checks
make quality-check

# 3. Run frontend tests
npx jest --config=jest.config.js

# 4. Generate documentation
python manage.py generate_docs

# 5. Deactivate when done
deactivate
```

### **Troubleshooting Virtual Environment:**

#### **Common Issues:**
```bash
# Issue: "No module named 'celery'" or similar import errors
# Solution: Ensure virtual environment is activated and dependencies are installed
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# Issue: Permission errors on Windows
# Solution: Run PowerShell as Administrator or use:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Issue: Virtual environment not found
# Solution: Recreate the virtual environment
rm -rf .venv
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

---

## 💻 Development Workflow

### **Code Standards:**
- **Python**: PEP 8 compliance, type hints where appropriate
- **JavaScript**: ES6+ standards, consistent formatting
- **CSS**: Bootstrap 5 utilities, custom CSS in `static/css/`
- **Templates**: Django template best practices

### **Git Workflow:**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create pull request
git push origin feature/your-feature-name
```

### **Testing:**
```bash
# Run all tests (Docker)
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test exchange

# Run with coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report

# Run Selenium E2E tests (Virtual Environment Required)
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1
# 2. Run tests
make test-selenium
# 3. Deactivate
deactivate
```

---

## 🧹 Code Quality, Pre-commit Hooks, and Frontend Testing

### **Code Quality Workflow**
- All code must pass formatting (Black, isort), linting (flake8, pylint), type checking (mypy), security (bandit, safety), and complexity checks (radon).
- Use the Makefile for all code quality commands (inside Docker):

```bash
make quality-check        # Run all code quality checks
make quality-analysis     # Run comprehensive analysis and generate a report
```

### **Pre-commit Hooks**
- Pre-commit hooks are configured to run formatting, lint, type, and security checks before each commit.
- Install hooks (once per clone):

```bash
make pre-commit-install
```

- Run hooks manually on all files:

```bash
make pre-commit-run
```

### **Frontend Testing with Jest**
- Frontend JavaScript logic is tested using Jest and jsdom.
- Tests are located in `tests/frontend/` and cover `static/js/` code.
- Run tests and view coverage (Virtual Environment Required):

```bash
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Run tests
npx jest --config=jest.config.js
npx jest --config=jest.config.js --coverage

# 3. Deactivate
deactivate
```

- Coverage reports are generated in `coverage/frontend/`.
- All new frontend code should include or update corresponding Jest tests.

---

## 🔧 Frontend Development

### **Template Structure:**
```
templates/frontend/
├── base.html              # Main layout
├── dashboard.html         # Role-based dashboard
├── auth/                  # Authentication pages
├── programs/              # Program management
├── applications/          # Application workflow
├── documents/             # Document management
└── admin/                 # Admin interfaces
```

### **JavaScript Architecture:**
- **`static/js/main.js`**: Core utilities and functions
- **`static/js/auth.js`**: Authentication logic
- **SweetAlert2**: Modern notifications
- **JWT Management**: Token handling and refresh

### **CSS Guidelines:**
- Use Bootstrap 5 utilities first
- Custom CSS in `static/css/main.css`
- Mobile-first responsive design
- Consistent color scheme and spacing

### **Dynamic Forms (django-dynforms):**
- **Official Package**: Uses official django-dynforms templates, JS, and CSS
- **No Overrides**: Do not override official templates unless absolutely necessary
- **Dark Mode**: Custom dark mode styles in `static/css/dynforms-dark-mode.css`
- **Template Blocks**: Uses `{% block pre_js %}` for JavaScript injection
- **Static Files**: Official package static files are used (no local copies)
- **Testing**: Selenium tests verify form builder functionality

---

## 🔌 API Development

### **Endpoint Structure:**
```
/api/
├── accounts/              # User management
├── programs/              # Exchange programs
├── applications/          # Student applications
├── documents/             # Document management
├── notifications/         # Notification system
├── analytics/             # Reporting and metrics
└── token/                 # JWT authentication
```

### **API Standards:**
- RESTful design principles
- Consistent response formats
- Proper HTTP status codes
- Comprehensive error handling
- Role-based permissions

### **Testing API Endpoints:**
```bash
# Test with curl
curl -X GET http://localhost:8000/api/programs/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test with Django shell
python manage.py shell
>>> from django.test import Client
>>> client = Client()
>>> response = client.get('/api/programs/')
```

---

## 🗄️ Database Development

### **Model Guidelines:**
- Use UUID primary keys for security
- Implement proper relationships
- Add comprehensive field validation
- Use Django's built-in features (TimeStampedModel)

### **Migration Workflow:**
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

### **Database Queries:**
- Use select_related() and prefetch_related() for efficiency
- Implement proper indexing
- Monitor query performance
- Use database transactions for data integrity

---

## 🔒 Security Development

### **Authentication:**
- JWT token-based authentication
- Automatic token refresh
- Role-based access control
- Account lockout policy

### **Data Protection:**
- Input validation and sanitization
- CSRF protection
- XSS prevention
- SQL injection protection via ORM

### **File Upload Security:**
- File type validation
- Size limits
- Virus scanning (stub implementation)
- Secure file storage

---

## 📊 Service Layer Development

### **Service Pattern:**
```python
class ApplicationService:
    @staticmethod
    @transaction.atomic
    def submit_application(application, user):
        # Business logic with validation
        # Timeline event creation
        # Notification sending
        return application
```

### **Service Guidelines:**
- Business logic in services, not views
- Use @transaction.atomic for data integrity
- Comprehensive error handling
- Proper delegation to other services

---

## 🧪 Testing Strategy

### **Test Types:**
- **Unit Tests**: Individual components and functions
- **Integration Tests**: API endpoints and workflows
- **Frontend Tests**: User interface components
- **End-to-End Tests**: Complete user workflows

### **Test Structure:**
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   ├── test_workflows.py
│   └── test_auth.py
├── frontend/
│   ├── test_components.py
│   └── test_forms.py
└── e2e/
    └── test_user_workflows.py
```

---

## 🚀 Deployment Development

### **Environment Configuration:**
- Use environment variables for sensitive data
- Separate settings for development/production
- Docker containerization
- Health checks and monitoring

### **Performance Optimization:**
- Database query optimization
- Caching strategies
- Static file optimization
- API response optimization

---

## 📚 Documentation Generation (Docker Only)

All documentation (API, code, Sphinx HTML) should be generated inside Docker containers for consistency.

- **API Docs (Swagger/OpenAPI):**
  ```bash
  make docs-api
  # or for all docs:
  make docs-workflow
  ```
- **Sphinx HTML Docs:**
  ```bash
  make docs-sphinx-docker
  # Open documentation/sphinx/build/html/index.html
  ```
- **Full Workflow:**
  ```bash
  make docs-workflow
  ```

See the [README](../README.md) and [documentation/README.md](README.md) for more details.

---

## 📚 Development Resources

### **Documentation:**
- **[Architecture](architecture.md)** - System design overview
- **[Business Rules](business_rules.md)** - Business logic reference
- **[API Documentation](http://localhost:8000/api/docs/)** - Interactive API docs
- **[Wireframes](wireframes/)** - UI/UX reference

### **Tools:**
- **Django Debug Toolbar**: Development debugging
- **Django Extensions**: Development utilities
- **Postman/Insomnia**: API testing
- **Chrome DevTools**: Frontend debugging

---

## 🐛 Debugging

### **Common Issues:**
- **Database Issues**: Check migrations and connections
- **API Errors**: Verify authentication and permissions
- **Frontend Issues**: Check browser console and network
- **Email Problems**: Test with console backend

### **Debug Commands:**
```bash
# Django shell
python manage.py shell

# Check configuration
python manage.py check --deploy

# View logs
docker-compose logs -f web
```

---

## 📝 Code Review Guidelines

### **Review Checklist:**
- [ ] Code follows project standards
- [ ] Proper error handling implemented
- [ ] Security considerations addressed
- [ ] Tests included for new features
- [ ] Documentation updated
- [ ] Performance impact considered

### **Review Process:**
1. Create pull request with clear description
2. Request review from team members
3. Address feedback and make changes
4. Ensure all tests pass
5. Merge after approval

---

**For additional development resources, see the [Architecture](architecture.md) and [Business Rules](business_rules.md) documentation.** 

## API Response Caching & Redis

### Overview
- SEIM uses Redis as the default cache backend for high-performance API response caching.
- API GET responses are cached automatically via `core.cache.APICacheMiddleware`.
- Caching is enabled for all `/api/` endpoints by default.

### Redis Setup
- Redis is included as a service in `docker-compose.yml`.
- The Django cache backend is configured in `seim/settings/base.py` to use Redis.
- Redis runs on `redis://redis:6379/1` in Docker.

### Cache Middleware
- `core.cache.APICacheMiddleware` is added to the Django `MIDDLEWARE` stack.
- It caches GET requests to `/api/` endpoints and serves cached responses when available.
- Cache keys are user-aware for authenticated requests.

### Cache Decorators
- Use `@cache_api_response` for function-based API views to enable fine-grained caching.
- Use `@cache_user_data` for user-specific data caching.
- See `core/cache.py` for usage examples.

### Cache Invalidation
- Use `invalidate_cache_pattern` decorator or utility to clear cache after data changes.
- Cache is automatically invalidated for updated/deleted resources.
- Manual invalidation can be triggered via management commands or admin actions.

### Monitoring & Debugging
- Cache statistics and hit/miss rates are tracked in `core/cache.py`.
- Use Django shell or management commands to inspect cache performance.
- Redis CLI (`docker exec -it seim-redis redis-cli`) can be used for advanced debugging.

### Best Practices
- Only cache safe (GET) API responses.
- Avoid caching sensitive or user-specific data unless using user-aware cache keys.
- Invalidate cache after any data mutation (POST, PUT, DELETE).
- Monitor cache size and performance regularly. 

## Cache Performance Monitoring & Invalidation

### Monitoring Cache Performance
- Use the management command to view live Redis cache statistics:
  ```sh
  python manage.py test_cache --stats
  ```
- This displays:
  - Redis version, memory usage, and uptime
  - Number of keys in the cache
  - Hit/miss rates and hit rate percentage
  - Evicted and expired keys
  - Cache connectivity status
- For advanced debugging, you can also use the Redis CLI:
  ```sh
  docker exec -it seim-redis redis-cli INFO
  ```

### Cache Invalidation
- **Automatic Invalidation:**
  - The cache is automatically invalidated for updated or deleted resources via cache decorators and service logic.
  - The `invalidate_cache_pattern` utility in `core/cache.py` can be used to clear cache entries matching a pattern after data changes.
- **Manual Invalidation:**
  - Use the management command to clear all cache:
    ```sh
    python manage.py test_cache --clear
    ```
  - You can also invalidate specific patterns in code:
    ```python
    from core.cache import invalidate_cache_pattern
    invalidate_cache_pattern('programs')  # Example: clear all program-related cache
    ```
- **Best Practices:**
  - Always invalidate cache after any data mutation (POST, PUT, DELETE) that affects cached GET endpoints.
  - Use pattern-based invalidation for related resources (e.g., all programs, all applications for a user).
  - Monitor cache hit/miss rates regularly to ensure optimal performance. 

## Hybrid JWT/Session Authentication Approach

SEIM uses a hybrid authentication model:
- **All authentication is handled via JWT tokens** (stored in localStorage) and API endpoints.
- **Django views/templates do not use session authentication**; `request.user.is_authenticated` is not used for frontend access control.
- **Protected pages** (dashboard, profile, etc.) render a minimal shell and use JavaScript to check for a valid JWT, fetch user info, and populate the UI. If no valid JWT is present, the user is redirected to `/login/`.
- **Navigation and UI elements** are shown/hidden via JavaScript based on JWT auth state and user role, not Django session state.
- **Login, registration, and logout** are all handled via API endpoints and JavaScript, not Django forms or session views.

### Extending This Pattern
- To protect a new page, render a minimal shell and use JS to check JWT and fetch user info.
- To add role-based UI, use JS to show/hide elements based on the user's role from the API.
- Do not use Django's `@login_required` or `request.user` in templates for frontend access control.

See `static/js/auth.js` and the dashboard template for examples. 

## Frontend Build Process (Webpack)

The SEIM frontend uses [Webpack](https://webpack.js.org/) for JavaScript and CSS bundling, minification, and cache-busting. This ensures all static assets are optimized for production and that browsers always load the latest versions.

### Entry Points
- `dashboard.js`
- `applications.js`
- `programs.js`
- `documents.js`
- `auth_entry.js`

Each entry point corresponds to a major page or feature and imports only the modules needed for that page.

### Output
- Bundled and minified files are output to `static/dist/` as `[name].[contenthash].js` and `[name].[contenthash].css`.
- Content hashes ensure cache-busting: when the file changes, the filename changes.

### How to Build
1. Install dependencies (first time only):
   ```sh
   npm install
   # or
   yarn install
   ```
2. Build for production:
   ```sh
   npm run build
   # or
   yarn build
   ```
3. For development with auto-rebuild:
   ```sh
   npm run dev
   # or
   yarn dev
   ```

### Referencing Assets in Django Templates
- Use `{% static 'dist/dashboard.[hash].js' %}` (replace `[hash]` with the actual hash from the build output).
- For automated injection of hashed filenames, consider using [django-webpack-loader](https://github.com/django-webpack/django-webpack-loader).

### Notes
- All ES6+ modules are transpiled via Babel for browser compatibility.
- CSS can be imported into JS entry points and will be extracted/minified.
- The build process cleans the output directory before each build.

See `webpack.config.js` and `package.json` for configuration details. 

## UI Module Structure and Best Practices

The UI logic is now split into focused modules for maintainability and clarity:

- `ui/loading.js`: Loading spinners and overlays (page/section loading, button loading states)
- `ui/auth_ui.js`: Authenticated/non-authenticated UI toggling, user/role-based UI updates
- `ui/bootstrap_helpers.js`: Bootstrap tooltips and modals initialization

The main `ui.js` file re-exports all functions from these submodules for backward compatibility, so existing imports will continue to work:

```js
// Backward compatible import (works as before)
import { showPageLoading, updateAuthUI, initializeTooltips } from './modules/ui.js';

// Recommended: Import only what you need from the focused submodules
import { showPageLoading } from './modules/ui/loading.js';
import { updateAuthUI } from './modules/ui/auth_ui.js';
import { initializeTooltips } from './modules/ui/bootstrap_helpers.js';
```

**Best Practices:**
- For new code, import only the functions you need from the relevant submodule.
- This improves tree-shaking and keeps your bundles smaller.
- The split makes it easier to maintain and extend UI logic as the project grows. 

## Bootstrap Utility Class Overrides for Theming

This project overrides Bootstrap's `.bg-*` and `.text-*` utility classes to use CSS custom properties (theme variables) for consistent theming and dark mode support.

**How it works:**
- `.bg-primary`, `.bg-secondary`, `.bg-success`, `.bg-danger`, `.bg-warning`, `.bg-info`, `.bg-light`, `.bg-dark` are redefined in `static/css/utilities/colors.css` to use `var(--primary-color)`, etc.
- `.text-primary`, `.text-secondary`, `.text-success`, `.text-danger`, `.text-warning`, `.text-info`, `.text-light`, `.text-dark` are redefined in `static/css/utilities/typography.css` to use theme variables.
- These variables change automatically in dark mode or when the theme is switched, ensuring all UI elements adapt correctly.

**Why:**
- Ensures backgrounds and text always match the current theme (light/dark/custom).
- Prevents color mismatches between Bootstrap defaults and the custom theme.
- Enables seamless dark mode and future theme expansion.

**How to use:**
- Use `.bg-primary`, `.bg-secondary`, etc. and `.text-primary`, `.text-secondary`, etc. in your HTML as usual.
- The color will always match the current theme.

**Note:**
- If you add new theme colors, update the utility classes in `colors.css` and `typography.css` accordingly.
- Avoid using raw Bootstrap color classes if you want full theme consistency. 

## Selenium E2E/Integration Test Setup (Windows Host)

SEIM's Selenium-based tests are configured to run from the HOST OS, not Docker containers. This is because Selenium requires direct access to the browser and display system. The tests connect to a Chrome browser running on your host OS.

### Steps to Run Selenium Tests:

1. **Install Chrome and ChromeDriver on Windows:**
   - Download and install Google Chrome (if not already installed).
   - Download the matching version of ChromeDriver from https://chromedriver.chromium.org/downloads and place it in your PATH.

2. **Run Selenium Standalone Server:**
   - Download Selenium Standalone Server (https://www.selenium.dev/downloads/).
   - Start the server in a terminal:
     ```
     java -jar selenium-server-4.x.x.jar standalone
     ```
   - By default, this will listen on `http://localhost:4444/wd/hub`.

3. **Set the SELENIUM_HOST environment variable (if needed):**
   - By default, the tests use `host.docker.internal` to connect from Docker to your Windows host.
   - If this does not work, set the environment variable `SELENIUM_HOST` to your Windows host IP address.

4. **Run the tests as usual (from Docker):**
   - The tests will connect to the Selenium server on your host and control Chrome there.

### Notes
- You must keep the Selenium Standalone Server running while tests execute.
- You can run Chrome in headless mode by uncommenting the `--headless` option in the test setup.
- This setup is required because Docker containers cannot install Chrome/Chromedriver in this environment. 

## Program Creation Flow (2025 Update)

- Admins can add new exchange programs via the "Add Program" button on the program list page.
- This opens a dedicated creation page (`/programs/create/`) with a form for all program details.
- Admins can select a dynamic application form (powered by django-dynforms) to associate with the program.
- The dynamic form builder is available at `/dynforms/` for creating and editing forms.
- After creation, the program appears in the list and is linked to its application form.

## Dynamic Forms Integration (django-dynforms)

SEIM uses the official django-dynforms package for dynamic form creation and management. The integration follows these principles:

### **Template Usage**
- **Official Templates**: Use the official dynforms templates from the package, not custom ones
- **Authentication Wrapper**: Wrap official dynforms views with authentication mixins for access control
- **Template Inheritance**: Extend the main base template and adjust block names as needed

### **JavaScript Integration**
- **Official JS**: Use the official dynforms JavaScript files (`dynforms.min.js`, `df-toasts.min.js`)
- **No Custom Overrides**: Avoid custom JavaScript that overrides official dynforms functionality
- **CSS Customization**: Dark mode and theming are handled via CSS-only customizations

### **URL Configuration**
```python
# Include official dynforms URLs first
urlpatterns = [
    path('dynforms/', include('dynforms.urls')),
    # Then override specific views with authenticated versions
    path('dynforms/', AuthenticatedDynformsView.as_view(), name='dynforms-authenticated'),
]
```

### **Dark Mode Support**
- Dark mode styling is implemented via CSS customizations in `static/css/dark-mode.css` and `static/css/dynforms-dark-mode.css`
- The implementation is CSS-only and doesn't modify dynforms JavaScript or templates
- See `documentation/dark-mode-implementation.md` for detailed implementation

### **Best Practices**
- Always use official dynforms templates and JavaScript
- Customize appearance via CSS only
- Wrap views with authentication mixins for access control
- Test form builder functionality after any dynforms-related changes 

## Cleaning Up Demo Data
To remove all demo data created for demonstration or testing, run:
    docker-compose exec web python manage.py cleanup_demo_data 

### **Backend Dependencies and Tools**
- File type detection for document uploads uses python-magic, with pylibmagic providing the required libmagic library for Python 3.12+ compatibility. The previous dependency python-magic-bin has been replaced. Ensure pylibmagic is installed for file type validation to work on all platforms. 