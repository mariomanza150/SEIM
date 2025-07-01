#!/bin/bash

# SGII Bootstrap 5.3.5 Implementation Testing Script
# This script helps you test the complete Bootstrap implementation

echo "🎉 SGII Bootstrap 5.3.5 Testing Script"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Please run this script from the SEIM directory (where manage.py is located)"
    exit 1
fi

echo "🔍 Checking implementation files..."

# Check if key files exist
files_to_check=(
    "exchange/templates/base/base.html"
    "exchange/static/css/custom-variables.css"
    "exchange/static/css/style.css"
    "exchange/static/js/seim-components.js"
    "exchange/templates/exchange/dashboard.html"
    "exchange/templates/exchange/exchange_list.html"
    "exchange/templates/authentication/login.html"
    "templates/404.html"
    "templates/500.html"
)

missing_files=()

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo ""
    echo "❌ Missing files detected. Please ensure all files are in place."
    exit 1
fi

echo ""
echo "✅ All implementation files present!"
echo ""

# Check Django settings
echo "🔧 Checking Django configuration..."

if python manage.py check --deploy > /dev/null 2>&1; then
    echo "✅ Django configuration is valid"
else
    echo "⚠️  Django configuration has issues. Running basic check..."
    python manage.py check
fi

# Collect static files
echo ""
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Static files collected successfully"
else
    echo "❌ Error collecting static files"
    exit 1
fi

# Test database connection
echo ""
echo "🗄️  Testing database connection..."
if python manage.py showmigrations > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Create test user if needed
echo ""
echo "👤 Checking for test users..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.settings')
django.setup()

from django.contrib.auth.models import User
from exchange.models import UserProfile

# Create test user if doesn't exist
if not User.objects.filter(username='testuser').exists():
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    
    # Create profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'role': 'STUDENT',
            'institution': 'Test University'
        }
    )
    print('✅ Test user created: testuser / testpass123')
else:
    print('✅ Test user already exists: testuser / testpass123')
"

echo ""
echo "🚀 Starting development server..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 TEST URLS TO VISIT:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏠 Home:          http://127.0.0.1:8000/"
echo "🔐 Login:         http://127.0.0.1:8000/login/"
echo "📊 Dashboard:     http://127.0.0.1:8000/dashboard/"
echo "📋 Exchanges:     http://127.0.0.1:8000/exchanges/"
echo "👤 Profile:       http://127.0.0.1:8000/profile/"
echo "❌ 404 Test:      http://127.0.0.1:8000/nonexistent/"
echo ""
echo "🔑 Test Credentials: testuser / testpass123"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 TESTING CHECKLIST:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "□ Theme switcher works (Light/Dark/Auto)"
echo "□ Navigation is responsive on mobile"
echo "□ Cards display with hover effects"
echo "□ Forms use floating labels"
echo "□ Tables are responsive"
echo "□ Icons display from Bootstrap Icons"
echo "□ Error pages work (visit /nonexistent/)"
echo "□ Dark mode transitions smoothly"
echo "□ Mobile navigation collapses properly"
echo "□ All buttons have loading states"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop the server when testing is complete"
echo ""

# Start the development server
python manage.py runserver