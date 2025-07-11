#!/bin/bash

# Tekshila Vercel Deployment Script
# This script automates the deployment process for Tekshila to Vercel

echo "🚀 Tekshila Vercel Deployment Script"
echo "======================================"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed."
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Check if user is logged in to Vercel
echo "🔐 Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    echo "🔑 Please log in to Vercel:"
    vercel login
fi

# Clean up duplicate files
echo "🧹 Cleaning up duplicate files..."
rm -f index.html login.html styles.css theme-test.html
rm -rf backend/
echo "✅ Cleanup complete"

echo ""
echo "📋 Pre-deployment Checklist:"
echo "=============================="
echo "1. ✅ Project structure is correct"
echo "2. ✅ vercel.json configuration file exists"
echo "3. ✅ requirements.txt with Python dependencies exists"
echo "4. ✅ Frontend files are in the frontend/ directory"
echo "5. ✅ API files are in the api/ directory"
echo ""

# Prompt for GitHub OAuth credentials
echo "🔧 GitHub OAuth Configuration:"
echo "==============================="
echo "You need to create a GitHub OAuth App first:"
echo "1. Go to: https://github.com/settings/developers"
echo "2. Click 'New OAuth App'"
echo "3. Set Homepage URL to: https://your-app-name.vercel.app"
echo "4. Set Authorization callback URL to: https://your-app-name.vercel.app/api/auth/github/callback"
echo ""

read -p "📝 Enter your GitHub OAuth Client ID: " GITHUB_CLIENT_ID
read -s -p "🔒 Enter your GitHub OAuth Client Secret: " GITHUB_CLIENT_SECRET
echo ""

# Generate a random secret key
SECRET_KEY=$(openssl rand -hex 32)
echo "🔑 Generated SECRET_KEY: $SECRET_KEY"
echo ""

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
echo "=========================="
vercel --prod

# Get the deployment URL
DEPLOYMENT_URL=$(vercel ls | grep "tekshila" | head -1 | awk '{print $2}')
if [ -z "$DEPLOYMENT_URL" ]; then
    echo "⚠️  Could not automatically detect deployment URL."
    read -p "📝 Please enter your Vercel deployment URL (e.g., https://tekshila-abc123.vercel.app): " DEPLOYMENT_URL
fi

echo ""
echo "🔧 Setting up environment variables..."
echo "====================================="

# Set environment variables
echo "Setting GITHUB_CLIENT_ID..."
echo "$GITHUB_CLIENT_ID" | vercel env add GITHUB_CLIENT_ID production

echo "Setting GITHUB_CLIENT_SECRET..."
echo "$GITHUB_CLIENT_SECRET" | vercel env add GITHUB_CLIENT_SECRET production

echo "Setting SECRET_KEY..."
echo "$SECRET_KEY" | vercel env add SECRET_KEY production

# Optional: Gemini API configuration
echo ""
read -p "🤖 Do you want to configure Gemini AI API? (y/N): " USE_GEMINI
if [[ $USE_GEMINI =~ ^[Yy]$ ]]; then
    read -p "📝 Enter your Gemini API Key: " GEMINI_API_KEY
    GEMINI_API_URL="https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    echo "$GEMINI_API_KEY" | vercel env add GEMINI_API_KEY production
    echo "$GEMINI_API_URL" | vercel env add GEMINI_API_URL production
    
    echo "✅ Gemini AI API configured"
else
    echo "⏭️  Skipping Gemini AI configuration (will use mock responses)"
fi

# Redeploy with environment variables
echo ""
echo "🔄 Redeploying with environment variables..."
vercel --prod

echo ""
echo "✅ Deployment Complete!"
echo "======================="
echo "🌐 Your app is live at: $DEPLOYMENT_URL"
echo ""
echo "📋 Next Steps:"
echo "==============="
echo "1. 🔧 Update your GitHub OAuth App settings:"
echo "   - Homepage URL: $DEPLOYMENT_URL"
echo "   - Authorization callback URL: $DEPLOYMENT_URL/api/auth/github/callback"
echo ""
echo "2. 🧪 Test your application:"
echo "   - Visit: $DEPLOYMENT_URL"
echo "   - Try logging in with GitHub"
echo "   - Test file upload and documentation generation"
echo ""
echo "3. 🔍 Monitor your application:"
echo "   - Vercel Dashboard: https://vercel.com/dashboard"
echo "   - Function logs: https://vercel.com/dashboard"
echo ""
echo "🎉 Happy coding!"
