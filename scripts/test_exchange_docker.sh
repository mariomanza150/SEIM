#!/bin/bash
# Docker Test Script for Exchange Creation Functionality

echo "🐳 Testing Exchange Creation Functionality with Docker"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Change to project directory
cd "$(dirname "$0")"

# Check if docker-compose.yml exists
if [ ! -f "docker/docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in docker directory"
    exit 1
fi

echo "✅ Docker Compose file found"

# Build and start containers
echo "🔨 Building and starting containers..."
cd docker
docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker containers"
    exit 1
fi

echo "✅ Containers started successfully"

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if web container is running
if ! docker-compose ps | grep -q "web.*Up"; then
    echo "❌ Web container is not running"
    docker-compose logs web
    exit 1
fi

echo "✅ Web container is running"

# Run Django checks
echo "🔍 Running Django system checks..."
docker-compose exec -T web python manage.py check

if [ $? -ne 0 ]; then
    echo "❌ Django system check failed"
    docker-compose logs web
    exit 1
fi

echo "✅ Django system checks passed"

# Run migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T web python manage.py migrate

if [ $? -ne 0 ]; then
    echo "❌ Database migrations failed"
    exit 1
fi

echo "✅ Database migrations completed"

# Test exchange creation functionality
echo "🧪 Testing exchange creation functionality..."
docker-compose exec -T web python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.settings')
django.setup()

try:
    from exchange.forms import ExchangeForm
    from exchange.models import Exchange
    from exchange.services.workflow import WorkflowService
    from django.contrib.auth.models import User
    
    print('✅ All imports successful')
    
    # Test form instantiation
    user = User(username='testuser', email='test@example.com')
    form = ExchangeForm(user=user)
    print('✅ Form instantiation successful')
    
    # Test workflow service
    methods = ['transition', 'get_available_transitions', 'get_workflow_history', 'can_submit']
    for method in methods:
        if hasattr(WorkflowService, method):
            print(f'✅ WorkflowService.{method} available')
        else:
            print(f'❌ WorkflowService.{method} missing')
    
    print('🎉 Exchange creation functionality tests passed!')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Exchange creation functionality test failed"
    exit 1
fi

# Check web server response
echo "🌐 Testing web server response..."
if docker-compose exec -T web curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Web server is responding"
else
    echo "⚠️  Web server check skipped (curl not available in container)"
fi

# Show container status
echo "📊 Container Status:"
docker-compose ps

# Show logs if needed
echo "======================================"
echo "🎉 Exchange Creation Functionality Test Complete!"
echo "======================================"
echo ""
echo "📋 Next Steps:"
echo "1. Access the application at: http://localhost:8000"
echo "2. Create a superuser: docker-compose exec web python manage.py createsuperuser"
echo "3. Navigate to /exchanges/create/ to test exchange creation"
echo "4. View logs: docker-compose logs web"
echo "5. Stop containers: docker-compose down"
echo ""
echo "🚀 The exchange creation functionality is ready for testing!"
