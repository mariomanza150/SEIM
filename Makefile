# SEIM Makefile
# Development and documentation automation

.PHONY: help docs docs-api docs-code docs-db docs-all clean-docs enhance-docs test migrate collectstatic runserver shell cache-test cache-status cache-clear clean clean-all setup format lint type-check security-check quality-check build-prod deploy-prod deploy-prod-update prod-setup prod-secrets prod-backup prod-restore prod-logs prod-shell prod-status prod-health prod-stop prod-clean

# Default target
help:
	@echo "SEIM Development & Production Commands"
	@echo "======================================"
	@echo ""
	@echo "Documentation:"
	@echo "  docs-api           - Generate API documentation only (Docker)"
	@echo "  docs-code          - Generate code documentation only (Docker)"
	@echo "  docs-db            - Generate database documentation only (Docker)"
	@echo "  docs-sphinx-docker - Build Sphinx HTML docs inside Docker container"
	@echo "  docs-all           - Generate all documentation (Docker, includes Sphinx)"
	@echo "  enhance-docs       - Enhance docstrings in codebase (Docker)"
	@echo "  clean-docs         - Clean generated documentation"
	@echo ""
	@echo "Development:"
	@echo "  migrate            - Run database migrations (Docker)"
	@echo "  collectstatic      - Collect static files (Docker)"
	@echo "  runserver          - Start development server (Docker)"
	@echo "  shell              - Start Django shell (Docker)"
	@echo "  test               - Run all tests (comprehensive)"
	@echo "  test-quick         - Run quick test suite"
	@echo "  test-unit          - Run unit tests (backend + frontend)"
	@echo "  test-integration   - Run integration tests (backend + frontend)"
	@echo "  test-e2e           - Run E2E tests"
	@echo "  test-coverage      - Run tests with coverage"
	@echo "  test-frontend      - Run frontend tests (Jest)"
	@echo "  test-selenium      - Run Selenium tests (host OS)"
	@echo "  test-all           - Run complete test suite"
	@echo "  test-workflow      - Run test workflow (quick + frontend + selenium setup)"
	@echo ""
	@echo "Playwright E2E Tests:"
	@echo "  e2e-setup          - Setup Playwright E2E environment"
	@echo "  e2e-test           - Run E2E tests (headless)"
	@echo "  e2e-test-headed    - Run E2E tests (visible browser)"
	@echo "  e2e-docker         - Run E2E tests in Docker"
	@echo "  vue-e2e-seed       - Seed Vue E2E data inside web container"
	@echo "  vue-e2e            - Seed in container + run Vue UI E2E tests (BASE_URL=5173, API_URL=8001)"
	@echo "  e2e-video-demos    - Generate video demo walkthroughs"
	@echo "  e2e-visual         - Run visual regression tests"
	@echo "  e2e-accessibility  - Run accessibility tests"
	@echo "  e2e-report         - Open E2E test report"
	@echo "  e2e-clean          - Clean E2E test artifacts"
	@echo ""
	@echo "Production Deployment:"
	@echo "  build-prod         - Build production Docker images"
	@echo "  deploy-prod        - Deploy to production environment"
	@echo "  deploy-prod-update - Update production deployment"
	@echo "  prod-setup         - Setup production environment"
	@echo "  prod-secrets       - Generate production secrets"
	@echo "  prod-backup        - Backup production database and files"
	@echo "  prod-restore       - Restore production from backup"
	@echo "  prod-logs          - View production logs"
	@echo "  prod-shell         - Open shell in production web container"
	@echo "  prod-status        - Show production service status"
	@echo "  prod-health        - Check production health"
	@echo "  prod-stop          - Stop production services"
	@echo "  prod-clean         - Clean production environment"
	@echo ""
	@echo "Caching:"
	@echo "  cache-test         - Test cache performance and functionality (Docker)"
	@echo "  cache-status       - Show cache configuration and status (Docker)"
	@echo "  cache-clear        - Clear all cache (Docker)"
	@echo "  cache-stats        - Show cache statistics (Docker)"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean              - Clean Python cache files and generated files"
	@echo "  clean-all          - Clean everything including Docker volumes"
	@echo ""
	@echo "Code Quality:"
	@echo "  format             - Format code with Black and isort (Docker)"
	@echo "  lint               - Run linting checks (Docker)"
	@echo "  type-check         - Run type checking with mypy (Docker)"
	@echo "  security-check     - Run security analysis (Docker)"
	@echo "  quality-check      - Run all code quality checks (Docker)"
	@echo ""
	@echo "Docker:"
	@echo "  docker-setup       - Setup Docker environment (creates .env, builds, starts)"
	@echo "  docker-up          - Start all services"
	@echo "  docker-down        - Stop all services"
	@echo "  docker-reset       - Reset Docker environment (WARNING: deletes all data)"
	@echo "  docker-logs        - View logs"
	@echo "  docker-shell       - Open shell in web container"
	@echo "  docker-db-shell    - Open shell in database container"
	@echo ""
	@echo "Setup:"
	@echo "  setup              - Setup development environment (Docker)"
	@echo "  setup-test-env     - Setup test environment (all test types)"
	@echo ""

# Documentation targets
docs-api:
	@echo "📚 Generating API documentation..."
	docker-compose exec web python manage.py generate_docs --format openapi

docs-code:
	@echo "📝 Generating code documentation..."
	docker-compose exec web python manage.py generate_docs --include-code

docs-db:
	@echo "🗄️ Generating database documentation..."
	docker-compose exec web python manage.py generate_docs --include-db

docs-sphinx-docker:
	@echo "📖 Building Sphinx HTML documentation inside Docker..."
	docker-compose exec web python -m sphinx -b html documentation/sphinx/source documentation/sphinx/build/html

docs-all:
	@echo "🚀 Generating all documentation..."
	docker-compose exec web python manage.py generate_docs --include-code --include-db --format openapi
	$(MAKE) docs-sphinx-docker

enhance-docs:
	@echo "🔧 Enhancing docstrings..."
	docker-compose exec web python manage.py enhance_docstrings --force

clean-docs:
	@echo "🧹 Cleaning generated documentation..."
	rm -rf documentation/generated/
	rm -f api_schema.yaml

# Development targets
migrate:
	@echo "🗄️ Running migrations..."
	docker-compose exec web python manage.py migrate

collectstatic:
	@echo "📦 Collecting static files..."
	docker-compose exec web python manage.py collectstatic --noinput

runserver:
	@echo "🚀 Starting development server..."
	docker-compose exec web python manage.py runserver 0.0.0.0:8000

shell:
	@echo "🐍 Starting Django shell..."
	docker-compose exec web python manage.py shell

# Testing targets
test:
	@echo "🧪 Running all tests..."
	./scripts/run_tests.sh all

test-docker:
	@echo "🧪 Running tests in dedicated test container..."
	docker-compose --profile test run --rm test

test-quick:
	@echo "🧪 Running quick test suite..."
	./scripts/run_tests.sh quick

test-unit:
	@echo "🧪 Running unit tests..."
	./scripts/run_tests.sh backend unit && ./scripts/run_tests.sh frontend unit

test-integration:
	@echo "🧪 Running integration tests..."
	./scripts/run_tests.sh backend integration && ./scripts/run_tests.sh frontend integration

test-e2e:
	@echo "🧪 Running end-to-end tests..."
	./scripts/run_tests.sh selenium e2e

# Frontend tests (HOST OS)
test-frontend:
	@echo "🧪 Running frontend tests..."
	./scripts/test_frontend.sh all

test-frontend-unit:
	@echo "🧪 Running frontend unit tests..."
	./scripts/test_frontend.sh unit

test-frontend-integration:
	@echo "🧪 Running frontend integration tests..."
	./scripts/test_frontend.sh integration

test-frontend-e2e:
	@echo "🧪 Running frontend E2E tests..."
	./scripts/test_frontend.sh e2e

test-frontend-coverage:
	@echo "🧪 Running frontend tests with coverage..."
	./scripts/test_frontend.sh all true

# Selenium E2E tests (HOST OS ONLY - not Docker)
test-selenium:
	@echo "🧪 Running Selenium E2E tests from HOST OS..."
	./scripts/test_selenium.sh all

test-selenium-e2e:
	@echo "🧪 Running Selenium E2E tests..."
	./scripts/test_selenium.sh e2e

test-selenium-standalone:
	@echo "🧪 Running standalone Selenium tests from HOST OS..."
	./scripts/test_selenium.sh standalone

test-selenium-setup:
	@echo "🧪 Testing Selenium setup from HOST OS..."
	./scripts/test_selenium.sh setup

test-coverage:
	@echo "🧪 Running tests with coverage..."
	./scripts/run_tests.sh ci

test-coverage-xml:
	@echo "🧪 Running tests with XML coverage..."
	docker-compose exec web pytest --cov=. --cov-report=xml:coverage.xml

test-fast:
	@echo "🧪 Running fast tests (no slow markers)..."
	./scripts/run_tests.sh quick

test-models:
	@echo "🧪 Running model tests..."
	docker-compose exec web pytest -m models

test-api:
	@echo "🧪 Running API tests..."
	docker-compose exec web pytest -m api

test-auth:
	@echo "🧪 Running authentication tests..."
	docker-compose exec web pytest -m auth

test-accounts:
	@echo "🧪 Running accounts app tests..."
	docker-compose exec web pytest tests/unit/accounts/ -v

test-exchange:
	@echo "🧪 Running exchange app tests..."
	docker-compose exec web pytest tests/unit/exchange/ -v

test-documents:
	@echo "🧪 Running documents app tests..."
	docker-compose exec web pytest tests/unit/documents/ -v

test-notifications:
	@echo "🧪 Running notifications app tests..."
	docker-compose exec web pytest tests/unit/notifications/ -v

test-analytics:
	@echo "🧪 Running analytics app tests..."
	docker-compose exec web pytest tests/unit/analytics/ -v

test-core:
	@echo "🧪 Running core app tests..."
	docker-compose exec web pytest tests/unit/core/ -v

test-parallel:
	@echo "🧪 Running tests in parallel..."
	docker-compose exec web pytest -n auto

test-watch:
	@echo "🧪 Running tests in watch mode..."
	docker-compose exec web pytest-watch

test-debug:
	@echo "🧪 Running tests with debug output..."
	docker-compose exec web pytest -s -v

test-failed:
	@echo "🧪 Running only failed tests..."
	docker-compose exec web pytest --lf

test-last-failed:
	@echo "🧪 Running last failed tests..."
	docker-compose exec web pytest --ff

# Legacy Django test command (for compatibility)
test-django:
	@echo "🧪 Running Django tests..."
	docker-compose exec web python manage.py test

# Code Quality targets
format:
	@echo "🎨 Formatting code with ruff and isort..."
	docker-compose exec web ruff format .
	docker-compose exec web isort .

format-check:
	@echo "🔍 Checking code formatting..."
	docker-compose exec web ruff format --check .
	docker-compose exec web isort --check-only .

lint:
	@echo "🔍 Running linting checks..."
	docker-compose exec web ruff check .
	docker-compose exec web flake8 .
	docker-compose exec web pylint --rcfile=pyproject.toml .

lint-fix:
	@echo "🔧 Auto-fixing linting issues..."
	docker-compose exec web ruff check --fix .
	docker-compose exec web ruff format .

type-check:
	@echo "🔍 Running type checking..."
	docker-compose exec web mypy . --ignore-missing-imports

security-check:
	@echo "🔒 Running security analysis..."
	docker-compose exec web bandit -r . -f json -o bandit-report.json
	docker-compose exec web safety check

complexity-check:
	@echo "📊 Analyzing code complexity..."
	docker-compose exec web radon cc . -a
	docker-compose exec web radon mi . -a

quality-check: format-check lint type-check security-check complexity-check
	@echo "✅ All code quality checks completed!"

quality-analysis:
	@echo "🔍 Running comprehensive code quality analysis..."
	docker-compose exec web python scripts/code_quality.py --check all

pre-commit-install:
	@echo "🔧 Installing pre-commit hooks..."
	docker-compose exec web pre-commit install

pre-commit-run:
	@echo "🔍 Running pre-commit hooks..."
	docker-compose exec web pre-commit run --all-files

# Cache management targets
cache-test:
	@echo "🧪 Testing cache performance..."
	docker-compose exec web python manage.py test_cache --test

cache-status:
	@echo "🔍 Showing cache status..."
	docker-compose exec web python manage.py test_cache --status

cache-clear:
	@echo "🧹 Clearing all cache..."
	docker-compose exec web python manage.py test_cache --clear

cache-stats:
	@echo "📊 Showing cache statistics..."
	docker-compose exec web python manage.py test_cache --stats

# Cleanup targets
clean:
	@echo "🧹 Cleaning Python cache files and generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name "*.pyd" -delete 2>/dev/null || true
	rm -rf documentation/generated/ 2>/dev/null || true
	rm -rf documentation/sphinx/build/ 2>/dev/null || true
	rm -f api_schema.yaml 2>/dev/null || true
	rm -rf staticfiles/ 2>/dev/null || true
	@echo "✅ Cleanup completed!"

clean-all: clean
	@echo "🧹 Cleaning Docker volumes and containers..."
	docker-compose down -v 2>/dev/null || true
	docker system prune -f 2>/dev/null || true
	@echo "✅ Full cleanup completed!"

# Docker targets
docker-up:
	@echo "🐳 Starting all services..."
	docker-compose up -d

docker-down:
	@echo "🛑 Stopping all services..."
	docker-compose down

docker-logs:
	@echo "📋 Viewing logs..."
	docker-compose logs -f

docker-setup:
	@echo "🔧 Setting up Docker environment..."
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp env.example .env; \
		echo "✅ .env file created. Please review and update if needed."; \
	else \
		echo "✅ .env file already exists."; \
	fi
	@echo "🐳 Building and starting services..."
	docker-compose up -d --build
	@echo "⏳ Waiting for services to be ready..."
	@echo "📋 Check logs with: make docker-logs"
	@echo "🌐 Application will be available at: http://localhost:8001"

docker-reset:
	@echo "🔄 Resetting Docker environment (WARNING: This will delete all data)..."
	docker-compose down -v
	docker-compose up -d --build
	@echo "✅ Docker environment reset complete!"

docker-shell:
	@echo "🐍 Opening shell in web container..."
	docker-compose exec web bash

docker-db-shell:
	@echo "🗄️ Opening shell in database container..."
	docker-compose exec db psql -U seimuser -d seim

# Setup targets
setup:
	@echo "🔧 Setting up SEIM development environment..."
	docker-compose up -d
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py create_initial_data
	docker-compose exec web python manage.py collectstatic --noinput
	@echo "✅ Setup complete! Access the application at http://localhost:8001"

setup-test-env:
	@echo "🔧 Setting up SEIM test environment..."
	./scripts/setup_test_environment.sh

# Documentation workflow
docs-workflow: enhance-docs docs-all
	@echo "✅ Documentation workflow completed!"
	@echo "📁 Generated files:"
	@ls -la documentation/generated/ 2>/dev/null || echo "No generated files found"
	@echo "📖 Sphinx HTML docs: documentation/sphinx/build/html/index.html"

# Cache workflow
cache-workflow: cache-status cache-test
	@echo "✅ Cache workflow completed!"
	@echo "📊 Cache performance tested and verified"

# Test workflow
test-workflow: test-quick test-frontend-unit test-selenium-setup
	@echo "✅ Test workflow completed!"
	@echo "📊 Quick tests, frontend unit tests, and Selenium setup verified"

# Full test suite
test-all: test test-frontend test-selenium
	@echo "✅ Complete test suite completed!"
	@echo "📊 Backend, frontend, and Selenium tests all executed"

# Full development workflow
dev-workflow: docker-up migrate collectstatic docs-workflow cache-workflow test-workflow
	@echo "✅ Development workflow completed!"
	@echo "🌐 Application available at: http://localhost:8001"
	@echo "📚 API docs available at: http://localhost:8001/api/docs/"
	@echo "🔧 Admin interface at: http://localhost:8001/seim/admin/" 

# Host OS test setup
setup-selenium-host:
	@echo "🔧 Setting up Selenium environment on HOST OS..."
	@echo "Installing Python dependencies for Selenium..."
	pip install selenium webdriver-manager pytest-selenium requests
	@echo "✅ Selenium dependencies installed"
	@echo "📋 Next steps:"
	@echo "  1. Install Chrome browser on your host OS"
	@echo "  2. Start Django server: docker-compose up web"
	@echo "  3. Run tests: make test-selenium"

# Production deployment targets
build-prod:
	@echo "🏗️ Building production Docker images..."
	@if [ ! -f .env.prod ]; then \
		echo "❌ Production environment file .env.prod not found!"; \
		echo "📝 Please copy env.prod.example to .env.prod and configure it."; \
		exit 1; \
	fi
	docker-compose -f docker-compose.prod.yml build --no-cache
	@echo "✅ Production images built successfully!"

deploy-prod: build-prod quality-check
		@echo "🚀 Deploying to production..."
	@echo "🚀 Deploying to production..."
	@if [ ! -f .env.prod ]; then \
		echo "❌ Production environment file .env.prod not found!"; \
		echo "📝 Please copy env.prod.example to .env.prod and configure it."; \
		exit 1; \
	fi
	@if [ ! -d secrets ]; then \
		echo "❌ Secrets directory not found!"; \
		echo "📝 Please run 'make prod-secrets' to generate secrets."; \
		exit 1; \
	fi
	$(MAKE) build-prod
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production deployment completed!"
	@echo "🌐 Application should be available at: http://localhost"
	@echo "📋 Check status with: make prod-status"
	@echo "📋 View logs with: make prod-logs"

deploy-prod-update:
	@echo "🔄 Updating production deployment..."
	docker-compose -f docker-compose.prod.yml pull
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "✅ Production update completed!"

prod-setup:
	@echo "🔧 Setting up production environment..."
	@if [ ! -f .env.prod ]; then \
		echo "📝 Creating .env.prod from template..."; \
		cp env.prod.example .env.prod; \
		echo "✅ .env.prod created. Please review and update values."; \
	else \
		echo "✅ .env.prod already exists."; \
	fi
	@echo "📁 Creating necessary directories..."
	mkdir -p secrets nginx/ssl nginx/conf.d backups
	@echo "✅ Production environment setup completed!"
	@echo "📋 Next steps:"
	@echo "  1. Review and update .env.prod"
	@echo "  2. Run 'make prod-secrets' to generate secrets"
	@echo "  3. Run 'make deploy-prod' to deploy"

prod-secrets:
	@echo "🔐 Generating production secrets..."
	@mkdir -p secrets
	@if [ ! -f secrets/django_secret_key.txt ]; then \
		echo "📝 Generating Django secret key..."; \
		python -c "import secrets; print(secrets.token_urlsafe(50))" > secrets/django_secret_key.txt; \
		echo "✅ Django secret key generated"; \
	else \
		echo "✅ Django secret key already exists"; \
	fi
	@if [ ! -f secrets/db_password.txt ]; then \
		echo "📝 Generating database password..."; \
		python -c "import secrets; print(secrets.token_urlsafe(32))" > secrets/db_password.txt; \
		echo "✅ Database password generated"; \
	else \
		echo "✅ Database password already exists"; \
	fi
	@if [ ! -f secrets/redis_password.txt ]; then \
		echo "📝 Generating Redis password..."; \
		python -c "import secrets; print(secrets.token_urlsafe(32))" > secrets/redis_password.txt; \
		echo "✅ Redis password generated"; \
	else \
		echo "✅ Redis password already exists"; \
	fi
	@echo "📝 Please manually create the following secret files:"
	@echo "  - secrets/aws_access_key_id.txt (your AWS access key)"
	@echo "  - secrets/aws_secret_access_key.txt (your AWS secret key)"
	@echo "  - secrets/email_host_user.txt (your email username)"
	@echo "  - secrets/email_host_password.txt (your email password)"
	@echo "✅ Secrets generation completed!"

prod-backup:
	@echo "💾 Creating production backup..."
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	BACKUP_DIR=backups/$(shell date +%Y%m%d_%H%M%S); \
	docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U seimuser seim > $$BACKUP_DIR/database.sql; \
	docker cp seim-web-prod:/app/media $$BACKUP_DIR/; \
	echo "✅ Backup created in $$BACKUP_DIR"

prod-restore:
	@echo "🔄 Restoring from backup..."
	@echo "⚠️  This will overwrite current data!"
	@read -p "Enter backup directory path: " backup_dir; \
	if [ ! -d "$$backup_dir" ]; then \
		echo "❌ Backup directory not found: $$backup_dir"; \
		exit 1; \
	fi; \
	docker-compose -f docker-compose.prod.yml exec -T db psql -U seimuser -d seim < $$backup_dir/database.sql; \
	docker cp $$backup_dir/media seim-web-prod:/app/; \
	echo "✅ Restore completed from $$backup_dir"

prod-logs:
	@echo "📋 Viewing production logs..."
	docker-compose -f docker-compose.prod.yml logs -f

prod-shell:
	@echo "🐍 Opening shell in production web container..."
	docker-compose -f docker-compose.prod.yml exec web bash

prod-status:
	@echo "📊 Production service status:"
	docker-compose -f docker-compose.prod.yml ps

prod-health:
	@echo "🏥 Checking production health..."
	@echo "Web service health:"
	docker-compose -f docker-compose.prod.yml exec web curl -f http://localhost:8000/health/ || echo "❌ Web service unhealthy"
	@echo "Database health:"
	docker-compose -f docker-compose.prod.yml exec db pg_isready -U seimuser -d seim || echo "❌ Database unhealthy"
	@echo "Redis health:"
	docker-compose -f docker-compose.prod.yml exec redis redis-cli ping || echo "❌ Redis unhealthy"
	@echo "ClamAV health:"
	docker-compose -f docker-compose.prod.yml exec clamav clamdscan --ping || echo "❌ ClamAV unhealthy"

prod-stop:
	@echo "🛑 Stopping production services..."
	docker-compose -f docker-compose.prod.yml down
	@echo "✅ Production services stopped!"

prod-clean:
	@echo "🧹 Cleaning production environment..."
	docker-compose -f docker-compose.prod.yml down -v
	docker system prune -f
	@echo "⚠️  WARNING: This will delete all production data!"
	@echo "✅ Production environment cleaned!"

# Playwright E2E testing targets
e2e-setup:
	@echo "🎭 Setting up Playwright E2E testing environment..."
	pip install -r requirements-test.txt
	playwright install chromium firefox webkit --with-deps
	@echo "✅ Playwright E2E environment setup complete!"

e2e-test:
	@echo "🎭 Running E2E tests (headless)..."
	pytest tests/e2e_playwright/ -v --headed=false --base-url=http://localhost:8001

e2e-test-headed:
	@echo "🎭 Running E2E tests (headed - visible browser)..."
	pytest tests/e2e_playwright/ -v --headed=true --slowmo=100 --base-url=http://localhost:8001

e2e-test-slow:
	@echo "🎭 Running E2E tests (slow motion for debugging)..."
	pytest tests/e2e_playwright/ -v --headed=true --slowmo=500 --base-url=http://localhost:8001

e2e-docker:
	@echo "🎭 Running E2E tests in Docker..."
	docker-compose -f docker-compose.e2e.yml --profile e2e up --build --abort-on-container-exit e2e_playwright
	docker-compose -f docker-compose.e2e.yml --profile e2e down
	@echo "✅ E2E tests completed!"

vue-e2e-seed:
	@echo "🌱 Seeding Vue E2E data (draft, document, notifications) in web container..."
	docker compose exec web python manage.py seed_vue_e2e
	@echo "✅ Vue E2E seed done."

vue-e2e: vue-e2e-seed
	@echo "🎭 Running Vue UI E2E tests (expect Vue at localhost:5173, API at localhost:8001)..."
	BASE_URL=http://localhost:5173 API_URL=http://localhost:8001 pytest tests/e2e_playwright/test_vue_ui.py -v -m vue --browser=chromium
	@echo "✅ Vue E2E tests done."

e2e-video-demos:
	@echo "🎬 Generating video demo walkthroughs..."
	@mkdir -p tests/e2e_playwright/videos
	@docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_video_demos.py -v --browser=chromium --base-url=http://web:8000 -m video_demo --tb=short
	@echo ""
	@echo "✅ Video demos complete! Check tests/e2e_playwright/videos/"

e2e-docker-shell:
	@echo "🎭 Opening shell in E2E container..."
	docker-compose -f docker-compose.e2e.yml run e2e_playwright bash

e2e-visual:
	@echo "🎭 Running visual regression tests..."
	pytest tests/e2e_playwright/test_visual_regression.py -v --base-url=http://localhost:8001

e2e-visual-update:
	@echo "🎭 Updating visual regression baselines..."
	pytest tests/e2e_playwright/test_visual_regression.py -v --update-baseline --base-url=http://localhost:8001

e2e-accessibility:
	@echo "🎭 Running accessibility tests..."
	pytest tests/e2e_playwright/test_accessibility.py -v --base-url=http://localhost:8001

e2e-auth:
	@echo "🎭 Running authentication workflow tests..."
	pytest tests/e2e_playwright/test_auth_workflows.py -v --base-url=http://localhost:8001

e2e-student:
	@echo "🎭 Running student workflow tests..."
	pytest tests/e2e_playwright/test_student_workflows.py -v --base-url=http://localhost:8001

e2e-coordinator:
	@echo "🎭 Running coordinator workflow tests..."
	pytest tests/e2e_playwright/test_coordinator_workflows.py -v --base-url=http://localhost:8001

e2e-admin:
	@echo "🎭 Running admin workflow tests..."
	pytest tests/e2e_playwright/test_admin_workflows.py -v --base-url=http://localhost:8001

e2e-parallel:
	@echo "🎭 Running E2E tests in parallel..."
	pytest tests/e2e_playwright/ -v -n auto --base-url=http://localhost:8001

e2e-smoke:
	@echo "🎭 Running E2E smoke tests..."
	pytest tests/e2e_playwright/ -v -m smoke --base-url=http://localhost:8001

e2e-report:
	@echo "📊 Opening E2E test report..."
	@if [ -f tests/e2e_playwright/reports/report.html ]; then \
		open tests/e2e_playwright/reports/report.html || xdg-open tests/e2e_playwright/reports/report.html || start tests/e2e_playwright/reports/report.html; \
	else \
		echo "❌ No test report found. Run tests first with 'make e2e-test'"; \
	fi

e2e-clean:
	@echo "🧹 Cleaning E2E test artifacts..."
	rm -rf tests/e2e_playwright/screenshots/*.png 2>/dev/null || true
	rm -rf tests/e2e_playwright/videos/*.webm 2>/dev/null || true
	rm -rf tests/e2e_playwright/reports/*.html 2>/dev/null || true
	rm -rf tests/e2e_playwright/visual/diffs/*.png 2>/dev/null || true
	@echo "✅ E2E test artifacts cleaned!"

e2e-clean-all: e2e-clean
	@echo "🧹 Cleaning E2E baselines and snapshots..."
	rm -rf tests/e2e_playwright/visual/snapshots/*.png 2>/dev/null || true
	@echo "✅ All E2E test data cleaned!" 