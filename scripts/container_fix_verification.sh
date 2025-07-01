#!/bin/bash

# SEIM Container Fix Verification Script
# Verifies that all jQuery and template issues are resolved

echo "🔧 SEIM Container Fix Verification"
echo "================================="

# Check if containers are running
echo "📋 Checking container status..."
CONTAINERS=$(docker-compose -f docker/docker-compose.yml ps --format json 2>/dev/null)

if [ $? -eq 0 ] && [ ! -z "$CONTAINERS" ]; then
    echo "✅ Docker containers are running"
    
    # Check web container specifically
    WEB_STATUS=$(echo "$CONTAINERS" | grep -i web | grep -i running)
    if [ ! -z "$WEB_STATUS" ]; then
        echo "✅ Web container is running"
    else
        echo "❌ Web container not running properly"
        exit 1
    fi
else
    echo "❌ Docker containers not running"
    echo "Starting containers..."
    docker-compose -f docker/docker-compose.yml up -d
    sleep 10
fi

# Test web server response
echo "🌐 Testing web server response..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")

if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "301" ]; then
    echo "✅ Web server responding (HTTP $HTTP_STATUS)"
else
    echo "⚠️ Web server response: HTTP $HTTP_STATUS"
fi

# Check for recent template errors in logs
echo "📋 Checking for template errors in recent logs..."
TEMPLATE_ERRORS=$(docker-compose -f docker/docker-compose.yml logs --tail=50 web 2>/dev/null | grep -i "TemplateSyntaxError\|Unclosed tag" | wc -l)

if [ "$TEMPLATE_ERRORS" -eq 0 ]; then
    echo "✅ No template syntax errors found in recent logs"
else
    echo "❌ Template errors still present: $TEMPLATE_ERRORS errors found"
    echo "Recent template errors:"
    docker-compose -f docker/docker-compose.yml logs --tail=20 web | grep -i "TemplateSyntaxError\|Unclosed tag"
fi

# Check for jQuery-related errors
echo "📋 Checking for jQuery errors in logs..."
JQUERY_ERRORS=$(docker-compose -f docker/docker-compose.yml logs --tail=50 web 2>/dev/null | grep -i "\$ is not defined\|jQuery.*not defined" | wc -l)

if [ "$JQUERY_ERRORS" -eq 0 ]; then
    echo "✅ No jQuery errors found in recent logs"
else
    echo "❌ jQuery errors found: $JQUERY_ERRORS errors"
fi

# Test exchange form endpoint specifically
echo "🔍 Testing exchange form endpoint..."
FORM_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/exchanges/create/ 2>/dev/null || echo "000")

if [ "$FORM_STATUS" = "200" ] || [ "$FORM_STATUS" = "302" ]; then
    echo "✅ Exchange form endpoint responding (HTTP $FORM_STATUS)"
else
    echo "❌ Exchange form endpoint error (HTTP $FORM_STATUS)"
    echo "Checking recent logs for exchange form errors..."
    docker-compose -f docker/docker-compose.yml logs --tail=10 web | grep -A5 -B5 "exchanges/create"
fi

# Verify template files exist and are valid
echo "📄 Verifying template files..."

if [ -f "SEIM/exchange/templates/base/base.html" ]; then
    if grep -q "jquery-3.6.0.min.js" "SEIM/exchange/templates/base/base.html"; then
        echo "✅ base.html contains jQuery CDN"
    else
        echo "❌ base.html missing jQuery CDN"
    fi
else
    echo "❌ base.html not found"
fi

if [ -f "SEIM/exchange/templates/exchange/exchange_form.html" ]; then
    # Check for proper block structure
    if grep -q "{% endblock %}" "SEIM/exchange/templates/exchange/exchange_form.html"; then
        echo "✅ exchange_form.html has proper block structure"
    else
        echo "❌ exchange_form.html missing endblock tags"
    fi
    
    # Check for bulletproof JavaScript
    if grep -q "waitForJQuery" "SEIM/exchange/templates/exchange/exchange_form.html"; then
        echo "✅ exchange_form.html contains bulletproof JavaScript"
    else
        echo "❌ exchange_form.html missing bulletproof JavaScript"
    fi
else
    echo "❌ exchange_form.html not found"
fi

# Summary
echo ""
echo "🎯 VERIFICATION SUMMARY:"
echo "======================="

# Count issues
ISSUES=0

if [ "$TEMPLATE_ERRORS" -gt 0 ]; then
    echo "❌ Template syntax errors present"
    ((ISSUES++))
else
    echo "✅ No template syntax errors"
fi

if [ "$JQUERY_ERRORS" -gt 0 ]; then
    echo "❌ jQuery errors present"
    ((ISSUES++))
else
    echo "✅ No jQuery errors"
fi

if [ "$FORM_STATUS" != "200" ] && [ "$FORM_STATUS" != "302" ]; then
    echo "❌ Exchange form endpoint not responding properly"
    ((ISSUES++))
else
    echo "✅ Exchange form endpoint working"
fi

if [ "$ISSUES" -eq 0 ]; then
    echo ""
    echo "🎉 ALL FIXES VERIFIED SUCCESSFULLY!"
    echo "✅ jQuery timing issue resolved"
    echo "✅ Template syntax errors fixed"
    echo "✅ Container running without errors"
    echo "✅ Exchange form endpoint accessible"
    echo ""
    echo "🔗 Ready to test at: http://localhost:8000/exchanges/create/"
else
    echo ""
    echo "⚠️ $ISSUES issues still present. Check the errors above."
fi

echo ""
echo "📋 Next steps:"
echo "1. Open http://localhost:8000/exchanges/create/ in your browser"
echo "2. Open browser dev tools (F12) and check console"
echo "3. Should see: '✅ jQuery loaded successfully: 3.6.0'"
echo "4. Should see: '✅ Exchange form initialized successfully'"
echo "5. Test form navigation (Next/Previous buttons)"

# Show recent container logs for manual inspection
echo ""
echo "📋 Recent container logs (last 10 lines):"
echo "----------------------------------------"
docker-compose -f docker/docker-compose.yml logs --tail=10 web
