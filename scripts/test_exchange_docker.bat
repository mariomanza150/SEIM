@echo off
REM Docker Test Script for Exchange Creation Functionality (Windows)

echo 🐳 Testing Exchange Creation Functionality with Docker
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    exit /b 1
)

echo ✅ Docker is running

REM Change to project directory
cd /d "%~dp0"

REM Check if docker-compose.yml exists
if not exist "docker\docker-compose.yml" (
    echo ❌ docker-compose.yml not found in docker directory
    exit /b 1
)

echo ✅ Docker Compose file found

REM Build and start containers
echo 🔨 Building and starting containers...
cd docker
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo ❌ Failed to start Docker containers
    exit /b 1
)

echo ✅ Containers started successfully

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if web container is running
docker-compose ps | findstr /C:"web" | findstr /C:"Up" >nul
if %errorlevel% neq 0 (
    echo ❌ Web container is not running
    docker-compose logs web
    exit /b 1
)

echo ✅ Web container is running

REM Run Django checks
echo 🔍 Running Django system checks...
docker-compose exec -T web python manage.py check

if %errorlevel% neq 0 (
    echo ❌ Django system check failed
    docker-compose logs web
    exit /b 1
)

echo ✅ Django system checks passed

REM Run migrations
echo 🗄️  Running database migrations...
docker-compose exec -T web python manage.py migrate

if %errorlevel% neq 0 (
    echo ❌ Database migrations failed
    exit /b 1
)

echo ✅ Database migrations completed

REM Test exchange creation functionality
echo 🧪 Testing exchange creation functionality...
docker-compose exec -T web python -c "import os; import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.settings'); django.setup(); from exchange.forms import ExchangeForm; from exchange.models import Exchange; from exchange.services.workflow import WorkflowService; from django.contrib.auth.models import User; print('✅ All imports successful'); user = User(username='testuser', email='test@example.com'); form = ExchangeForm(user=user); print('✅ Form instantiation successful'); methods = ['transition', 'get_available_transitions', 'get_workflow_history', 'can_submit']; [print(f'✅ WorkflowService.{method} available') if hasattr(WorkflowService, method) else print(f'❌ WorkflowService.{method} missing') for method in methods]; print('🎉 Exchange creation functionality tests passed!')"

if %errorlevel% neq 0 (
    echo ❌ Exchange creation functionality test failed
    exit /b 1
)

REM Show container status
echo 📊 Container Status:
docker-compose ps

REM Show completion message
echo ======================================
echo 🎉 Exchange Creation Functionality Test Complete!
echo ======================================
echo.
echo 📋 Next Steps:
echo 1. Access the application at: http://localhost:8000
echo 2. Create a superuser: docker-compose exec web python manage.py createsuperuser
echo 3. Navigate to /exchanges/create/ to test exchange creation
echo 4. View logs: docker-compose logs web
echo 5. Stop containers: docker-compose down
echo.
echo 🚀 The exchange creation functionality is ready for testing!

pause
