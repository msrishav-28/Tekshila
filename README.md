# Tekshila - AI-Powered Code Documentation Platform

🧠 **Transform your code into comprehensive documentation with AI-powered analysis and seamless GitHub integration**

## 🌟 Overview

Tekshila is a cutting-edge web application that revolutionizes how developers create and maintain documentation. By leveraging artificial intelligence and providing native GitHub integration, Tekshila transforms the tedious task of documentation into an automated, intelligent workflow.

## ✨ Key Features

### 📝 **Intelligent Documentation Generation**
- **Smart README Creation**: Generate comprehensive, professional README files from your codebase
- **Inline Code Comments**: Add intelligent, context-aware comments to your source code
- **Multi-language Support**: Full support for 20+ programming languages including Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, PHP, Ruby, Swift, and Kotlin
- **Batch Processing**: Upload multiple files or entire projects via ZIP archives
- **Custom Instructions**: Provide additional context to tailor documentation to your needs

### 🔗 **Advanced GitHub Integration**
- **OAuth Authentication**: Secure GitHub authentication with proper OAuth flow
- **Repository Browser**: Interactive interface to browse, search, and filter your repositories
- **Automatic Pull Requests**: Create pull requests with generated documentation automatically
- **Branch Management**: Select target branches and create feature branches for documentation
- **Repository Selection**: Visual repository picker with stats and metadata
- **Real-time Sync**: Stay connected with your GitHub workflow

### 🔍 **AI-Powered Code Quality Analysis**
- **Comprehensive Analysis**: Deep code quality assessment with AI insights
- **Issue Detection**: Identify code smells, security vulnerabilities, and performance issues
- **Best Practice Suggestions**: Receive actionable recommendations for improvement
- **Severity Classification**: Issues categorized by severity (error, warning, info)
- **Metrics Dashboard**: Visual display of quality metrics and scores
- **Detailed Reports**: Comprehensive analysis with line-by-line feedback

### 🎨 **Modern User Experience**
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Dark/Light Themes**: Toggle between themes with persistent preference
- **Real-time Preview**: Live preview of generated documentation with Markdown rendering
- **Drag & Drop Interface**: Intuitive file upload with visual feedback
- **Loading States**: Professional loading indicators and progress feedback
- **Error Handling**: Comprehensive error states with retry functionality
- **Accessibility**: WCAG compliant with keyboard navigation and screen reader support

## 🚀 Getting Started

### Prerequisites

- **Web Browser**: Modern browser with ES2020 support (Chrome 80+, Firefox 74+, Safari 13+, Edge 80+)
- **GitHub Account**: For repository integration and authentication
- **GitHub OAuth App**: Required for secure authentication
- **Development Environment**: Node.js 18+ for local development

### Quick Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/tekshila.git
   cd tekshila
   ```

2. **Configure Environment Variables**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your GitHub OAuth credentials
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   JWT_SECRET=your_jwt_secret
   ```

3. **Install Dependencies**
   ```bash
   npm install
   ```

4. **Start Development Server**
   ```bash
   npm run dev
   ```

## 🏗️ Architecture

### Frontend Architecture
- **Modern Vanilla JavaScript**: Class-based modular architecture with ES6+ features
- **State Management**: Centralized application state with event-driven updates
- **Component System**: Organized managers for different application concerns
- **Responsive CSS**: Mobile-first design with CSS Grid and Flexbox
- **Progressive Enhancement**: Works without JavaScript for basic functionality

### Backend Architecture
- **Serverless Functions**: Vercel-optimized Python serverless functions
- **API Gateway**: RESTful API design with proper error handling
- **OAuth Integration**: Secure GitHub authentication flow
- **Modular Design**: Separation of concerns with dedicated utility modules

### Key Components
```
Application Structure:
├── AuthManager          # GitHub OAuth authentication
├── ThemeManager         # Dark/light theme handling
├── TabManager           # Navigation and tab switching
├── FileUploadManager    # File handling and validation
├── GitHubRepositoryManager  # Repository operations
├── DocumentationManager     # AI documentation generation
├── QualityAnalysisManager  # Code quality assessment
└── Utils               # Shared utility functions
```

## 🚀 Deployment

### Vercel Deployment (Recommended)

1. **Connect Repository**
   ```bash
   # Link to Vercel
   vercel link
   
   # Set environment variables
   vercel env add GITHUB_CLIENT_ID
   vercel env add GITHUB_CLIENT_SECRET
   vercel env add JWT_SECRET
   ```

2. **Deploy**
   ```bash
   # Deploy to production
   vercel --prod
   ```

### Manual Deployment

1. **Build the Application**
   ```bash
   npm run build
   ```

2. **Deploy Static Files**
   - Upload `frontend/` directory to your web server
   - Configure serverless functions for `/api/` endpoints

## 📖 Usage Guide

### 🔧 **Initial Setup**

1. **GitHub OAuth Setup**
   - Create a GitHub OAuth App in your GitHub Developer Settings
   - Set Authorization callback URL to `https://yourdomain.com/auth/callback`
   - Note the Client ID and Client Secret

2. **First Login**
   - Navigate to the application
   - Click "Continue with GitHub"
   - Authorize the application
   - You'll be redirected to the main dashboard

### 📝 **Documentation Generation Workflow**

1. **Upload Code Files**
   - Drag and drop files or click to browse
   - Supports individual files or ZIP archives
   - Real-time file validation and preview

2. **Configure Generation**
   - Choose between README or inline comments
   - Enter project name (required for README)
   - Add custom instructions for specific needs

3. **Generate and Review**
   - Click "Generate Documentation"
   - Review AI-generated content in live preview
   - Copy to clipboard or download as file

### 🔗 **GitHub Integration Workflow**

1. **Repository Selection**
   - Browse your repositories with search and filters
   - Click on any repository to select it
   - View repository statistics and metadata

2. **Pull Request Creation**
   - Ensure documentation is generated first
   - Select target branch from dropdown
   - Fill in PR title, description, and commit message
   - Click "Create Pull Request" to auto-create

### 🔍 **Code Quality Analysis**

1. **Single File Analysis**
   - Navigate to Quality Analysis tab
   - Upload one file for detailed review
   - Click "Analyze Code Quality"

2. **Review Results**
   - View quality metrics in visual dashboard
   - See categorized issues with severity levels
   - Get actionable improvement suggestions

## 🔧 Configuration Options

### Environment Variables
```bash
# Required for GitHub Integration
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret

# Required for JWT tokens
JWT_SECRET=your_jwt_secret_key

# Optional: AI API configurations
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

### Feature Flags
```javascript
// In your environment or config
FEATURES = {
    GITHUB_INTEGRATION: true,
    AI_ANALYSIS: true,
    QUALITY_METRICS: true,
    DARK_MODE: true
}
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/tekshila.git
   cd tekshila
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

3. **Make Changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Submit Pull Request**
   ```bash
   git push origin feature/amazing-new-feature
   # Create PR through GitHub interface
   ```

### Development Guidelines
- **Code Style**: Use ESLint and Prettier configurations
- **Commits**: Follow conventional commit messages
- **Testing**: Add unit tests for new features
- **Documentation**: Update README and inline docs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/tekshila/issues)
- **Documentation**: [Wiki](https://github.com/your-username/tekshila/wiki)
- **Community**: [Discussions](https://github.com/your-username/tekshila/discussions)

## 🙏 Acknowledgments

- **Google Gemini**: AI-powered code analysis
- **GitHub API**: Repository integration
- **Vercel**: Hosting and deployment platform
- **Font Awesome**: Icon library
- **Inter Font**: Typography

---

**Built with ❤️ by the Tekshila Team**
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
- Open an issue on GitHub
- Check the documentation
- Review existing issues and discussions

## Roadmap

- [ ] Support for more programming languages
- [ ] Integration with other version control systems
- [ ] Advanced code metrics and analytics
- [ ] Team collaboration features
- [ ] API for programmatic access

## Acknowledgments

- Google Gemini for AI capabilities
- GitHub for repository integration
- The open-source community for inspiration and tools

---

Made with ❤️ by the Tekshila Team

## 🔧 Troubleshooting

### "Configuration not loaded. Please refresh the page."

This error occurs when the application cannot load the GitHub OAuth configuration. Here's how to fix it:

#### 1. **Check Environment Variables**
Ensure these variables are set in your Vercel deployment:
- `GITHUB_CLIENT_ID` - Your GitHub OAuth app client ID
- `GITHUB_CLIENT_SECRET` - Your GitHub OAuth app client secret

#### 2. **Verify GitHub OAuth App Setup**
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Check your OAuth app configuration:
   - Homepage URL: `https://your-domain.vercel.app`
   - Callback URL: `https://your-domain.vercel.app/api/auth/github/callback`

#### 3. **Test API Endpoints**
Check if your API is working:
- Health Check: `https://your-domain.vercel.app/api/health`
- Configuration: `https://your-domain.vercel.app/api/config`

#### 4. **Run Diagnostics**
Use our diagnostic script:
```bash
./diagnose.sh
```

#### 5. **Force Redeploy**
If environment variables were recently added:
```bash
# Trigger a new deployment
echo "$(date)" > deployment-trigger.txt
git add deployment-trigger.txt
git commit -m "Force redeploy for environment variables"
git push
```

For detailed setup instructions, see [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md).

### Other Common Issues

#### **"Unable to connect to server"**
- Check your internet connection
- Verify the Vercel deployment is active
- Check Vercel function logs for errors

#### **"GitHub OAuth is not configured"**
- Verify `GITHUB_CLIENT_ID` is set in Vercel environment variables
- Ensure the GitHub OAuth app exists and is configured correctly
- Check that the client ID matches between GitHub and Vercel

#### **API requests failing with CORS errors**
- This should be automatically handled by our configuration
- If issues persist, check the browser network tab for specific error details
