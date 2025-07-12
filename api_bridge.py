"""
API Bridge for Tekshila - Connects Frontend to Backend Services
Provides REST API endpoints for the modern frontend to interact with Streamlit backend logic
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import tempfile
import asyncio
import io
import zipfile
from pathlib import Path

# Import core functionality
from core import process_file_content, process_zip_file, call_gemini, SUPPORTED_FILES
from github_integration import GitHubIntegration
from code_quality import CodeQualityAnalyzer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Tekshila API",
    description="AI-Powered Code Documentation and Analysis API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
github_integrations = {}  # Store GitHub integrations by session

# Pydantic models
class DocumentationRequest(BaseModel):
    project_name: str
    purpose: str  # "readme" or "comments"
    custom_instructions: Optional[str] = ""
    files: Dict[str, str]  # filename: content

class GitHubConnectRequest(BaseModel):
    token: str

class GitHubRepoRequest(BaseModel):
    token: str

class GitHubBranchRequest(BaseModel):
    token: str
    repo: str

class GitHubPRRequest(BaseModel):
    token: str
    repo: str
    branch: str
    title: str
    description: str
    commit_message: str
    files: Dict[str, str]  # filename: content

class QualityAnalysisRequest(BaseModel):
    filename: str
    content: str

class FileUploadResponse(BaseModel):
    success: bool
    files: Dict[str, str]
    message: str

class GitHubConnectRequest(BaseModel):
    token: str

class GitHubPRRequest(BaseModel):
    token: str
    repo: str
    branch: str
    title: str
    description: str
    commit_message: str
    content: str
    filename: str

class QualityAnalysisRequest(BaseModel):
    filename: str
    content: str

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Tekshila API"}

# Documentation generation endpoint
@app.post("/api/generate-docs")
async def generate_documentation(request: DocumentationRequest):
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        if not request.files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Process files
        all_content = ""
        file_info = []
        supported_extensions = list(SUPPORTED_FILES.keys())
        
        for filename, content in request.files.items():
            # Get file extension
            file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
            
            # Check if file extension is supported
            if file_ext in supported_extensions:
                all_content += f"\n\n--- {filename} ---\n{content}"
                file_info.append({
                    "name": filename,
                    "size": len(content),
                    "type": SUPPORTED_FILES.get(file_ext, "unknown")
                })
        
        if not all_content:
            raise HTTPException(status_code=400, detail="No supported files found")
        
        # Call Gemini API
        if request.purpose.lower() == "readme":
            generated_content = await asyncio.to_thread(
                call_gemini, 
                request.files,  # Pass files dict for multiple files
                "readme", 
                True,  # is_multiple_files
                request.project_name, 
                request.custom_instructions, 
                GEMINI_API_KEY, 
                os.getenv("GEMINI_API_URL")
            )
        else:
            # For comments, handle multiple files properly
            if len(request.files) == 1:
                # Single file
                filename = list(request.files.keys())[0]
                file_content = request.files[filename]
                generated_content = await asyncio.to_thread(
                    call_gemini, 
                    file_content, 
                    "comment", 
                    False, 
                    filename, 
                    request.custom_instructions, 
                    GEMINI_API_KEY, 
                    os.getenv("GEMINI_API_URL")
                )
            else:
                # Multiple files - process each file separately and combine
                commented_files = {}
                for filename, file_content in request.files.items():
                    try:
                        commented_content = await asyncio.to_thread(
                            call_gemini, 
                            file_content, 
                            "comment", 
                            False, 
                            filename, 
                            request.custom_instructions, 
                            GEMINI_API_KEY, 
                            os.getenv("GEMINI_API_URL")
                        )
                        commented_files[filename] = commented_content
                    except Exception as e:
                        # If individual file fails, include original with error note
                        commented_files[filename] = f"// Error adding comments to {filename}: {str(e)}\n\n{file_content}"
                
                # Combine all commented files
                generated_content = ""
                for filename, content in commented_files.items():
                    generated_content += f"// ========== {filename} ==========\n\n{content}\n\n"
        
        return {
            "success": True,
            "content": generated_content,
            "files_processed": file_info,
            "purpose": request.purpose,
            "project_name": request.project_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate documentation: {str(e)}")

# File upload endpoint
@app.post("/api/upload-files")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        uploaded_files = {}
        supported_extensions = list(SUPPORTED_FILES.keys())
        
        for file in files:
            # Read file content
            content = await file.read()
            
            # Handle different file types
            if file.filename.endswith('.zip'):
                # Process zip file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                    temp_file.write(content)
                    temp_file_path = temp_file.name
                
                try:
                    zip_content = process_zip_file(temp_file_path)
                    uploaded_files.update(zip_content)
                finally:
                    os.unlink(temp_file_path)
            else:
                # Check if individual file has supported extension
                file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
                
                if file_ext in supported_extensions:
                    # Regular file
                    try:
                        file_content = content.decode('utf-8')
                        uploaded_files[file.filename] = file_content
                    except UnicodeDecodeError:
                        # Handle binary files
                        uploaded_files[file.filename] = f"[Binary file: {file.filename}]"
        
        if not uploaded_files:
            raise HTTPException(status_code=400, detail="No supported files found in upload")
        
        return {
            "success": True,
            "files": uploaded_files,
            "count": len(uploaded_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {str(e)}")

# GitHub integration endpoints
@app.post("/api/github/connect")
async def connect_github(request: GitHubConnectRequest):
    try:
        github = GitHubIntegration(request.token)
        
        if github.validate_token():
            # Store integration (in production, use proper session management)
            import uuid
            # Use a more reliable session ID generation
            session_id = str(uuid.uuid4().hex)[:16]  # Generate a 16-char hex string
            github_integrations[session_id] = github
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Successfully connected to GitHub"
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid GitHub token")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to GitHub: {str(e)}")

@app.get("/api/github/repos")
async def get_repositories(session_id: str):
    try:
        print(f"Looking for session_id: {session_id}")
        print(f"Available sessions: {list(github_integrations.keys())}")
        
        if session_id not in github_integrations:
            raise HTTPException(status_code=401, detail="GitHub not connected")
        
        github = github_integrations[session_id]
        print(f"Found GitHub integration for session {session_id}")
        
        repos = github.get_repositories()
        print(f"Retrieved {len(repos)} repositories")
        
        return {
            "success": True,
            "repositories": repos
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get repositories: {str(e)}")

@app.get("/api/github/branches")
async def get_branches(session_id: str, repo: str):
    try:
        if session_id not in github_integrations:
            raise HTTPException(status_code=401, detail="GitHub not connected")
        
        github = github_integrations[session_id]
        branches = github.get_branches(repo)
        
        return {
            "success": True,
            "branches": branches
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get branches: {str(e)}")

@app.post("/api/github/create-pr")
async def create_pull_request(request: GitHubPRRequest):
    try:
        github = GitHubIntegration(request.token)
        
        # Create the pull request with multiple files support
        pr_result = github.create_pull_request(
            repo=request.repo,
            branch=request.branch,
            content_map=request.files,  # Pass files dict instead of single content
            commit_message=request.commit_message,
            pr_title=request.title,
            pr_body=request.description
        )
        
        if pr_result.get("success"):
            return {
                "success": True,
                "pr_url": pr_result.get("pr_url"),
                "message": "Pull request created successfully"
            }
        else:
            raise HTTPException(status_code=400, detail=pr_result.get("error", "Failed to create PR"))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create pull request: {str(e)}")

# Code quality analysis endpoint
@app.post("/api/analyze-quality")
async def analyze_code_quality(request: QualityAnalysisRequest):
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        # Initialize code analyzer
        analyzer = CodeQualityAnalyzer(gemini_api_key=GEMINI_API_KEY)
        
        # Analyze the code using AI
        analysis_result = await asyncio.to_thread(
            analyzer.analyze_with_ai, 
            request.content, 
            request.filename
        )
        
        return {
            "success": True,
            "analysis": analysis_result,
            "filename": request.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze code: {str(e)}")

# File download endpoints
@app.get("/api/download/{file_type}")
async def download_file(file_type: str, content: str, filename: str = "download.txt"):
    """Download generated content as file"""
    try:
        if file_type == "single":
            # Single file download
            return StreamingResponse(
                io.StringIO(content),
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        elif file_type == "zip":
            # Multiple files as zip
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Parse content as JSON for multiple files
                import json
                files_data = json.loads(content)
                for fname, fcontent in files_data.items():
                    zip_file.writestr(fname, fcontent)
            
            zip_buffer.seek(0)
            return StreamingResponse(
                io.BytesIO(zip_buffer.getvalue()),
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

@app.post("/api/generate-docs-advanced")
async def generate_documentation_advanced(request: DocumentationRequest):
    """Enhanced documentation generation with better handling of multiple files"""
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        if not request.files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Determine if we're working with multiple files
        is_multiple = len(request.files) > 1
        
        if request.purpose.lower() == "readme":
            # Generate single README for all files
            generated_content = await asyncio.to_thread(
                call_gemini,
                request.files,
                "readme",
                is_multiple,
                request.project_name,
                request.custom_instructions,
                GEMINI_API_KEY,
                os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent")
            )
            
            return {
                "success": True,
                "content": generated_content,
                "filename": "README.md",
                "type": "single",
                "purpose": request.purpose
            }
            
        else:  # Comments
            # Generate comments for each file separately
            commented_files = {}
            for filename, content in request.files.items():
                commented_content = await asyncio.to_thread(
                    call_gemini,
                    {filename: content},
                    "comment",
                    False,
                    filename,
                    request.custom_instructions,
                    GEMINI_API_KEY,
                    os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent")
                )
                commented_files[filename] = commented_content
            
            return {
                "success": True,
                "content": commented_files,
                "type": "multiple",
                "purpose": request.purpose
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate documentation: {str(e)}")

@app.get("/api/supported-files")
async def get_supported_files():
    """Get list of supported file extensions"""
    return {
        "success": True,
        "supported_files": list(SUPPORTED_FILES.keys()),
        "file_types": SUPPORTED_FILES
    }

@app.post("/api/github/validate-token")
async def validate_github_token(request: GitHubConnectRequest):
    """Validate GitHub token without storing it"""
    try:
        github = GitHubIntegration(request.token)
        is_valid = github.validate_token()
        
        return {
            "success": True,
            "valid": is_valid,
            "message": "Token is valid" if is_valid else "Token is invalid"
        }
        
    except Exception as e:
        return {
            "success": False,
            "valid": False,
            "message": f"Failed to validate token: {str(e)}"
        }

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "api_bridge:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
