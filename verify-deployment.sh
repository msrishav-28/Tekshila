#!/bin/bash

# Deployment Verification Script
# Run this after deploying to verify your endpoints work

echo "🔍 Verifying Tekshila Deployment"
echo "================================="
echo

# Check if URL is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <your-vercel-url>"
    echo "Example: $0 https://your-app.vercel.app"
    exit 1
fi

BASE_URL="$1"
echo "🌍 Testing deployment at: $BASE_URL"
echo

# Function to test endpoint
test_endpoint() {
    local url="$1"
    local name="$2"
    
    echo -n "Testing $name... "
    
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -s -w "%{http_code}" -H "Accept: application/json" "$url" 2>/dev/null)
        body="${response%???}"
        http_code="${response: -3}"
        
        if [ "$http_code" = "200" ]; then
            echo "✅ OK"
            # Show response preview for API endpoints
            if [[ "$url" == *"/api/"* ]]; then
                echo "   Response preview: $(echo "$body" | head -c 100)..."
            fi
        else
            echo "❌ Failed (HTTP $http_code)"
            if [ -n "$body" ]; then
                echo "   Error: $(echo "$body" | head -c 200)"
            fi
        fi
    else
        echo "⚠️  curl not available"
    fi
}

# Test all endpoints
echo "📡 Testing API Endpoints:"
test_endpoint "$BASE_URL/api/health" "Health Check"
test_endpoint "$BASE_URL/api/config" "Configuration"

echo
echo "🌐 Testing Frontend:"
test_endpoint "$BASE_URL/" "Main Page"
test_endpoint "$BASE_URL/login" "Login Page"

echo
echo "🔧 Quick Verification Checklist:"
echo "================================="
echo

echo "1. Visit your login page: $BASE_URL/login"
echo "   ✅ Should show 'Continue with GitHub' button (not disabled)"
echo "   ✅ Should not show 'Configuration not loaded' error"
echo

echo "2. Check browser console:"
echo "   ✅ No red errors in console"
echo "   ✅ Should see 'Configuration loaded successfully'"
echo

echo "3. Test API endpoints directly:"
echo "   Config: $BASE_URL/api/config"
echo "   Health: $BASE_URL/api/health"
echo

echo "4. Verify environment variables in Vercel dashboard:"
echo "   ✅ GITHUB_CLIENT_ID is set"
echo "   ✅ GITHUB_CLIENT_SECRET is set"
echo

echo "If all tests pass, your deployment is working correctly! 🎉"
