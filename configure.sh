#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Tekshila Configuration Setup${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists. Backing up to .env.backup${NC}"
    cp .env .env.backup
fi

# Copy from example
if [ -f ".env.example" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file from template${NC}"
else
    echo -e "${RED}❌ .env.example file not found${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📝 Please configure the following environment variables in your .env file:${NC}"
echo ""

echo -e "${BLUE}1. GitHub OAuth Configuration:${NC}"
echo "   - Go to https://github.com/settings/applications/new"
echo "   - Create a new OAuth App with:"
echo "     • Application name: Tekshila"
echo "     • Homepage URL: http://localhost:3000 (or your domain)"
echo "     • Authorization callback URL: http://localhost:3000/api/auth/github/callback"
echo "   - Copy the Client ID and Client Secret to your .env file"
echo ""

echo -e "${BLUE}2. API Key Configuration:${NC}"
echo "   - Get a Google Gemini API key from https://makersuite.google.com/app/apikey"
echo "   - OR get an OpenAI API key from https://platform.openai.com/api-keys"
echo "   - Add it to your .env file"
echo ""

echo -e "${BLUE}3. JWT Secret:${NC}"
echo "   - Generate a secure random string (at least 32 characters)"
echo "   - You can use: openssl rand -base64 32"
echo ""

echo -e "${GREEN}🚀 After configuration, run 'npm run dev' in the frontend directory to start the application${NC}"
echo ""

# Generate a random JWT secret
JWT_SECRET=$(openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64)
if [ -n "$JWT_SECRET" ]; then
    # Replace the JWT_SECRET in .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your_super_secret_jwt_key_with_at_least_32_characters_for_security/$JWT_SECRET/" .env
    else
        # Linux
        sed -i "s/your_super_secret_jwt_key_with_at_least_32_characters_for_security/$JWT_SECRET/" .env
    fi
    echo -e "${GREEN}✅ Generated JWT secret automatically${NC}"
fi

echo -e "${YELLOW}💡 Next steps:${NC}"
echo "1. Edit the .env file with your GitHub OAuth credentials"
echo "2. Add your API key (Gemini or OpenAI)"
echo "3. Run the application with 'npm run dev' in the frontend directory"
echo ""
