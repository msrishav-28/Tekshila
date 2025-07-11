#!/bin/bash

# Tekshila Diagnostic Script
# Run this to diagnose configuration issues

echo "🔍 Tekshila Configuration Diagnostic"
echo "===================================="
echo

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json not found. Please run this script from the project root."
    exit 1
fi

echo "✅ Project structure looks correct"
echo

# Test API endpoints
echo "🌐 Testing API endpoints..."
echo

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -n "Testing $description ($endpoint)... "
    
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json "$endpoint" 2>/dev/null)
        http_code="${response: -3}"
        
        if [ "$http_code" = "200" ]; then
            echo "✅ OK"
            if [ "$endpoint" = "*config*" ] || [ "$endpoint" = "*health*" ]; then
                echo "   Response: $(cat /tmp/response.json | head -c 200)..."
            fi
        else
            echo "❌ Failed (HTTP $http_code)"
            if [ -f /tmp/response.json ]; then
                echo "   Error: $(cat /tmp/response.json)"
            fi
        fi
    else
        echo "⚠️  curl not available, skipping"
    fi
}

# Get the base URL
if [ -n "$VERCEL_URL" ]; then
    BASE_URL="https://$VERCEL_URL"
elif [ -f ".vercel/project.json" ]; then
    # Try to extract from Vercel config
    BASE_URL="https://$(cat .vercel/project.json | grep -o '"name":"[^"]*"' | cut -d'"' -f4).vercel.app"
else
    echo "⚠️  Cannot determine deployment URL. Please set VERCEL_URL environment variable."
    read -p "Enter your Vercel deployment URL (e.g., https://your-app.vercel.app): " BASE_URL
fi

echo "🌍 Testing against: $BASE_URL"
echo

# Test endpoints
test_endpoint "$BASE_URL/api/health" "Health Check"
test_endpoint "$BASE_URL/api/config" "Configuration"
test_endpoint "$BASE_URL/" "Frontend"
test_endpoint "$BASE_URL/login" "Login Page"

echo
echo "🔧 Environment Check..."

# Check local environment variables
check_env_var() {
    local var_name=$1
    local description=$2
    
    if [ -n "${!var_name}" ]; then
        echo "✅ $description ($var_name) is set"
    else
        echo "❌ $description ($var_name) is not set"
    fi
}

check_env_var "GITHUB_CLIENT_ID" "GitHub Client ID"
check_env_var "GITHUB_CLIENT_SECRET" "GitHub Client Secret"

echo
echo "📋 Common Issues and Solutions:"
echo "1. Environment variables not set in Vercel dashboard"
echo "2. GitHub OAuth app callback URL doesn't match deployment URL"
echo "3. API routes not properly configured in vercel.json"
echo "4. CORS issues preventing frontend from reaching API"
echo
echo "📖 For detailed setup instructions, see ENVIRONMENT_SETUP.md"
echo
echo "🔗 Useful URLs:"
echo "   - Health Check: $BASE_URL/api/health"
echo "   - Configuration: $BASE_URL/api/config"
echo "   - Vercel Dashboard: https://vercel.com/dashboard"
echo "   - GitHub OAuth Apps: https://github.com/settings/developers"

# Cleanup
rm -f /tmp/response.json
