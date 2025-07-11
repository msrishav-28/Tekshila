#!/bin/bash

# Tekshila Quick Setup Script
# This script prepares the project for deployment

echo "🚀 Tekshila Quick Setup"
echo "======================"

# 1. Clean up duplicate files
echo ""
echo "🧹 Cleaning up duplicate files..."
rm -f index.html login.html styles.css theme-test.html
rm -rf backend/
rm -rf .devcontainer/
rm -f frontend/theme-test.html
echo "✅ Cleanup complete"

# 2. Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

# 3. Check for .env file
echo ""
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your API keys."
else
    echo "✅ .env file exists"
fi

# 4. Verify Python dependencies
echo ""
echo "🐍 Python dependencies:"
cat requirements.txt

# 5. Show next steps
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. Edit .env file with your API keys:"
echo "   - GITHUB_CLIENT_ID"
echo "   - GITHUB_CLIENT_SECRET"
echo "   - JWT_SECRET (32+ characters)"
echo "   - GEMINI_API_KEY (for AI features)"
echo ""
echo "2. Create a GitHub OAuth App:"
echo "   - Go to: https://github.com/settings/developers"
echo "   - Click 'New OAuth App'"
echo "   - Set Homepage URL to: https://your-app-name.vercel.app"
echo "   - Set Authorization callback URL to: https://your-app-name.vercel.app/api/auth/github/callback"
echo ""
echo "3. Deploy to Vercel:"
echo "   npm run deploy"
echo ""
echo "4. Update GitHub OAuth App URLs with your Vercel URL"
echo ""
echo "Happy coding! 🎉"
