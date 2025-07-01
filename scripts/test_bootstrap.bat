@echo off
REM SGII Bootstrap 5.3.5 Implementation Testing Script
REM This script helps you test the complete Bootstrap implementation

echo 🎉 SGII Bootstrap 5.3.5 Testing Script
echo ======================================
echo.

REM Check if we're in the right directory
if not exist "manage.py" (
    echo ❌ Error: Please run this script from the SEIM directory (where manage.py is located)
    pause
    exit /b 1
)

echo 🔍 Checking implementation files...

REM Check if key files exist
set "files_exist=1"
set "files_to_check=exchange\templates\base\base.html exchange\static\css\custom-variables.css exchange\static\css\style.css exchange\static\js\seim-components.js exchange\templates\exchange\dashboard.html exchange\templates\exchange\exchange_list.html exchange\templates\authentication\login.html templates\404.html templates\500.html"

for %%f in (%files_to_check%) do (
    if exist "%%f" (
        echo ✅ %%f
    ) else (
        echo ❌ %%f - MISSING
        set "files_exist=0"
    )
)

if "%files_exist%"=="0" (
    echo.
    echo ❌ Missing files detected. Please ensure all files are in place.
    pause
    exit /b 1
)

echo.
echo ✅ All implementation files present!
echo.

REM Check Django settings
echo 🔧 Checking Django configuration...

python manage.py check --deploy >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Django configuration is valid
) else (
    echo ⚠️  Django configuration has issues. Running basic check...
    python manage.py check
)

REM Collect static files
echo.
echo 📦 Collecting static files...
python manage.py collectstatic --noinput --clear >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ Static files collected successfully
) else (
    echo ❌ Error collecting static files
    pause
    exit /b 1
)

REM Test database connection
echo.
echo 🗄️  Testing database connection...
python manage.py showmigrations >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Database connection successful
) else (
    echo ❌ Database connection failed
    pause
    exit /b 1
)

REM Create test user if needed
echo.
echo 👤 Checking for test users...
python -c "import os; import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.settings'); django.setup(); from django.contrib.auth.models import User; from exchange.models import UserProfile; user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', first_name='Test', last_name='User') if not User.objects.filter(username='testuser').exists() else None; profile, created = UserProfile.objects.get_or_create(user=User.objects.get(username='testuser'), defaults={'role': 'STUDENT', 'institution': 'Test University'}) if User.objects.filter(username='testuser').exists() else (None, False); print('✅ Test user ready: testuser / testpass123')"

echo.
echo 🚀 Starting development server...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🎯 TEST URLS TO VISIT:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🏠 Home:          http://127.0.0.1:8000/
echo 🔐 Login:         http://127.0.0.1:8000/login/
echo 📊 Dashboard:     http://127.0.0.1:8000/dashboard/
echo 📋 Exchanges:     http://127.0.0.1:8000/exchanges/
echo 👤 Profile:       http://127.0.0.1:8000/profile/
echo ❌ 404 Test:      http://127.0.0.1:8000/nonexistent/
echo.
echo 🔑 Test Credentials: testuser / testpass123
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🧪 TESTING CHECKLIST:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo □ Theme switcher works (Light/Dark/Auto)
echo □ Navigation is responsive on mobile
echo □ Cards display with hover effects
echo □ Forms use floating labels
echo □ Tables are responsive
echo □ Icons display from Bootstrap Icons
echo □ Error pages work (visit /nonexistent/)
echo □ Dark mode transitions smoothly
echo □ Mobile navigation collapses properly
echo □ All buttons have loading states
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Press Ctrl+C to stop the server when testing is complete
echo.

REM Start the development server
python manage.py runserver

pause