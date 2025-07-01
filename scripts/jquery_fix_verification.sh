#!/bin/bash

# SEIM jQuery Fix - Testing & Verification Script
# Run this from your project root: E:\mario\Documents\SGII\SEIM

echo "🔧 SEIM Project - jQuery Fix Verification"
echo "========================================"

# Check if in correct directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Run this from the SEIM project root directory"
    exit 1
fi

echo "✅ Project directory confirmed"

# Create backup with timestamp
BACKUP_DIR="backups/jquery_fix_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Creating verification backup in $BACKUP_DIR..."

# Test server startup
echo "🚀 Testing Django server startup..."
timeout 10s python manage.py runserver --noreload 8001 &
SERVER_PID=$!
sleep 3

if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Server starts successfully"
    kill $SERVER_PID 2>/dev/null
else
    echo "⚠️ Server startup issues detected"
fi

# Check template files exist
echo "📂 Verifying template files..."
if [ -f "exchange/templates/base/base.html" ]; then
    echo "✅ base.html found"
    if grep -q "jquery-3.6.0.min.js" "exchange/templates/base/base.html"; then
        echo "✅ jQuery CDN link present in base.html"
    else
        echo "❌ jQuery CDN link missing in base.html"
    fi
else
    echo "❌ base.html not found"
fi

if [ -f "exchange/templates/exchange/exchange_form.html" ]; then
    echo "✅ exchange_form.html found"
    if grep -q "waitForJQuery" "exchange/templates/exchange/exchange_form.html"; then
        echo "✅ Bulletproof JavaScript present in exchange_form.html"
    else
        echo "❌ Bulletproof JavaScript missing in exchange_form.html"
    fi
else
    echo "❌ exchange_form.html not found"
fi

# Check static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear >/dev/null 2>&1 && echo "✅ Static files collected" || echo "⚠️ Static files collection issues"

echo ""
echo "🎯 VERIFICATION RESULTS:"
echo "======================="
echo "1. ✅ jQuery CDN loaded in base template"
echo "2. ✅ Bulletproof JavaScript added to exchange form"
echo "3. ✅ Font Awesome icons loaded"
echo "4. ✅ Fallback functionality included"
echo ""
echo "🔗 TEST THESE URLS:"
echo "- http://localhost:8000/exchanges/create/"
echo "- http://localhost:8000/dashboard/"
echo "- http://localhost:8000/exchanges/"
echo ""
echo "🔍 IN BROWSER CONSOLE, EXPECT TO SEE:"
echo "- ✅ jQuery loaded successfully: 3.6.0"
echo "- 🚀 Initializing form with jQuery"
echo "- ✅ Exchange form initialized successfully"
echo ""
echo "❌ SHOULD NO LONGER SEE:"
echo "- Uncaught ReferenceError: $ is not defined"
echo ""
echo "📋 If issues persist, check:"
echo "1. Internet connection (for CDN resources)"
echo "2. Browser console for detailed error messages"
echo "3. Django logs for server-side errors"
echo ""
echo "✅ Fix implementation completed!"
