# Tekshila

Tekshila is an AI-powered application that generates technical documentation (like README files) and adds contextual comments to source code. It features a modern web frontend built with Vite and a FastAPI backend, with GitHub integration for creating pull requests and AI-driven code quality analysis.

## Features

- **README Generator**: Automatically generate detailed README files from your codebase.
- **Code Commenting**: Add helpful and contextual comments to source code.
- **Code Quality Analysis**: Identify code smells, security issues, performance bottlenecks, and best practices.
- **GitHub Integration**: Create pull requests directly with your documentation or annotated code.
- **Modern Web Interface**: Clean, responsive frontend built with Vite.
- **FastAPI Backend**: High-performance REST API backend.
- Powered by **Gemini API** for intelligent and language-aware code processing.

## Architecture

- **Frontend**: Modern web interface (Vite + Vanilla JS)
- **Backend**: FastAPI REST API server
- **AI Engine**: Google Gemini API for code analysis and generation
- **Version Control**: GitHub API integration

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/tekshila.git
   cd tekshila
   ```

2. **Install Python dependencies**:
   Make sure you have Python 3.8+ installed, then:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

4. **Configure environment variables**:
   Create a `.env` file with the following:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
   GEMINI_API_MODEL=gemini-2.0-flash
   GITHUB_TOKEN=your_github_token_here
   STREAMLIT_PORT=8501
   VITE_PORT=3000
   API_PORT=8000
   API_BASE_URL=http://localhost:8000
   ```

## Usage

### Option 1: Run Both Servers Together
```bash
npm start
```
This will start both the FastAPI backend (port 8000) and Vite frontend (port 3000) simultaneously.

### Option 2: Run Servers Separately

**Start the FastAPI backend**:
```bash
python api_bridge.py
```

**Start the Vite frontend** (in another terminal):
```bash
npm run dev
```

### Option 3: Production Mode
```bash
npm run build
npm run start:prod
```

## Access Points

- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## Main Features:

1. **Generate Documentation**:
   - Upload one or more code files (or a ZIP).
   - Choose whether to generate a README or add comments.
   - Provide a project name and optional instructions.
   - Download results or push directly to GitHub.

2. **GitHub Integration**:
   - Authenticate with your GitHub token.
   - Select a repository and branch.
   - Create a PR with the newly generated documentation.

3. **Code Quality Analysis**:
   - Upload a file to receive detailed analysis and improvement suggestions from the AI.

## Gemini API Integration

The app uses Gemini's large language model to analyze and understand code. Ensure you set up your API key and endpoint in the `.env` file.

## GitHub Integration

- Tekshila uses [PyGithub](https://pygithub.readthedocs.io/) for GitHub operations.
- Your personal access token should have `repo` scope to allow for PR creation.

## Project Structure

```bash
.
├── api_bridge.py           # FastAPI backend server
├── main.py                 # Legacy Streamlit UI (can be removed)
├── core.py                 # Code processing and Gemini interaction
├── code_quality.py         # AI-driven code quality analysis
├── github_integration.py   # GitHub API integration
├── index.html              # Main frontend HTML
├── script.js               # Frontend JavaScript logic
├── styles.css              # Frontend styling
├── vite.config.js          # Vite configuration
├── package.json            # Node.js dependencies and scripts
├── requirements.txt        # Python dependencies
├── .env                    # API credentials (not committed)
├── .gitignore
└── LICENSE
```

## API Endpoints

### Documentation
- `POST /api/generate-docs` - Generate documentation from code files
- `POST /api/generate-docs-advanced` - Enhanced documentation generation
- `POST /api/upload-files` - Upload and process code files

### GitHub Integration
- `POST /api/github/connect` - Connect to GitHub with token
- `POST /api/github/validate-token` - Validate GitHub token
- `GET /api/github/repos?session_id=` - Get user repositories
- `GET /api/github/branches?session_id=&repo=` - Get repository branches
- `POST /api/github/create-pr` - Create pull request

### Code Quality
- `POST /api/analyze-quality` - Analyze code quality with AI

### Utilities
- `GET /health` - Health check
- `GET /api/supported-files` - Get supported file types
- `GET /docs` - API documentation (Swagger UI)

## Development

To extend the application:

1. **Backend**: Modify `api_bridge.py` to add new endpoints
2. **Frontend**: Edit `script.js` and `styles.css` for UI changes
3. **AI Logic**: Update `core.py` and `code_quality.py` for AI functionality
4. **GitHub Features**: Extend `github_integration.py` for more GitHub operations

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
