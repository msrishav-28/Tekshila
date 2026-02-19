"""
Tekshila API - 2026 Ready
Modern FastAPI with agent architecture, streaming, and real-time capabilities
"""

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import os
import asyncio
import json
import structlog
from contextlib import asynccontextmanager

# Internal imports
from db.connection import get_db, init_db, close_db
from db.models import (
    User, Project, ProjectFile, DocumentationJob, 
    AgentTask, Integration, DocStatus, UserRole
)
from auth.security import (
    verify_token, exchange_github_code, create_access_token, 
    create_refresh_token, refresh_github_token, Token, TokenData
)
from agents.documentation_agent import (
    get_agent_orchestrator, DocumentationType
)
from github_integration import GitHubIntegration

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Security
security = HTTPBearer(auto_error=False)

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Tekshila API", version="3.0.0")
    await init_db()
    yield
    # Shutdown
    logger.info("👋 Shutting down Tekshila API")
    await close_db()

app = FastAPI(
    title="Tekshila API",
    description="AI-Powered Code Documentation with Agent Architecture",
    version="3.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ============================================================================
# Authentication Dependencies
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = verify_token(credentials.credentials)
    if not token_data or not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

# ============================================================================
# Health & Status
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/status")
async def api_status(current_user: User = Depends(get_current_user)):
    """Detailed API status for authenticated users"""
    return {
        "status": "operational",
        "user": {
            "id": str(current_user.id),
            "username": current_user.username,
            "role": current_user.role.value
        },
        "features": {
            "agent_architecture": True,
            "streaming": True,
            "github_integration": bool(current_user.github_token),
            "vector_search": True
        }
    }

# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/auth/github/callback")
async def github_auth_callback(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    GitHub OAuth callback
    Exchange code for tokens and create/update user
    """
    try:
        # Exchange code for GitHub tokens and user info
        github_data = await exchange_github_code(code)
        
        # Check if user exists
        result = await db.execute(
            select(User).where(User.github_id == github_data["github_id"])
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Update existing user
            user.github_token = github_data["access_token"]
            user.github_refresh_token = github_data.get("refresh_token")
            user.last_login = datetime.utcnow()
            user.email = github_data.get("email") or user.email
            user.avatar_url = github_data.get("avatar_url")
        else:
            # Create new user
            from uuid import uuid4
            user = User(
                id=uuid4(),
                email=github_data.get("email") or f"{github_data['login']}@github.com",
                username=github_data["login"],
                display_name=github_data.get("name"),
                avatar_url=github_data.get("avatar_url"),
                github_id=github_data["github_id"],
                github_token=github_data["access_token"],
                github_refresh_token=github_data.get("refresh_token"),
                last_login=datetime.utcnow(),
                is_verified=True
            )
            db.add(user)
        
        await db.commit()
        
        # Create JWT tokens
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "github_id": user.github_id
            }
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("GitHub auth error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@app.post("/auth/refresh")
async def refresh_token_endpoint(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    token_data = verify_token(refresh_token, token_type="refresh")
    
    if not token_data or not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    new_access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "github_id": user.github_id
        }
    )
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": 1800
    }

# ============================================================================
# User Endpoints
# ============================================================================

@app.get("/api/user/me")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "avatar_url": current_user.avatar_url,
        "role": current_user.role.value,
        "preferences": current_user.preferences,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@app.patch("/api/user/preferences")
async def update_user_preferences(
    preferences: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    current_user.preferences = {**current_user.preferences, **preferences}
    await db.commit()
    
    return {"success": True, "preferences": current_user.preferences}

# ============================================================================
# Project Endpoints
# ============================================================================

@app.get("/api/projects")
async def list_projects(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's projects"""
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == current_user.id)
        .order_by(desc(Project.updated_at))
    )
    projects = result.scalars().all()
    
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "primary_language": p.primary_language,
            "github_repo_url": p.github_repo_url,
            "total_files": p.total_files,
            "total_lines": p.total_lines,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None
        }
        for p in projects
    ]

@app.post("/api/projects")
async def create_project(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    from uuid import uuid4
    
    project = Project(
        id=uuid4(),
        owner_id=current_user.id,
        name=name,
        description=description
    )
    
    db.add(project)
    await db.commit()
    
    return {
        "id": str(project.id),
        "name": project.name,
        "message": "Project created successfully"
    }

# ============================================================================
# GitHub Integration Endpoints
# ============================================================================

@app.get("/api/github/repos")
async def list_github_repos(
    current_user: User = Depends(get_current_active_user)
):
    """List GitHub repositories for authenticated user"""
    if not current_user.github_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub not connected"
        )
    
    try:
        github = GitHubIntegration(current_user.github_token)
        repos = github.get_repositories()
        
        return {"repositories": repos}
    except Exception as e:
        logger.error("GitHub repos error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch repositories"
        )

@app.post("/api/github/sync/{project_id}")
async def sync_github_repo(
    project_id: str,
    repo_name: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync GitHub repository to project"""
    # Get project
    from uuid import UUID
    
    result = await db.execute(
        select(Project).where(
            Project.id == UUID(project_id),
            Project.owner_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update GitHub info
    project.github_repo_name = repo_name
    project.github_repo_url = f"https://github.com/{repo_name}"
    project.last_synced = datetime.utcnow()
    
    await db.commit()
    
    return {"success": True, "message": "Repository linked"}

# ============================================================================
# Documentation Generation (Agent Architecture)
# ============================================================================

@app.post("/api/documentation/generate")
async def generate_documentation(
    files: Dict[str, str],  # filename -> content
    doc_type: str = "readme",
    project_id: Optional[str] = None,
    stream: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate documentation using agent architecture
    """
    # Validate doc_type
    try:
        doc_type_enum = DocumentationType(doc_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid doc_type. Choose from: {[t.value for t in DocumentationType]}"
        )
    
    # Create documentation job
    from uuid import uuid4
    
    job = DocumentationJob(
        id=uuid4(),
        user_id=current_user.id,
        project_id=uuid.UUID(project_id) if project_id else None,
        doc_type=doc_type,
        status=DocStatus.PROCESSING,
        file_paths=list(files.keys()),
        started_at=datetime.utcnow()
    )
    db.add(job)
    await db.commit()
    
    if stream:
        return StreamingResponse(
            stream_documentation_generation(files, doc_type_enum, job.id, db),
            media_type="text/event-stream"
        )
    
    # Non-streaming: run agent workflow
    try:
        orchestrator = get_agent_orchestrator()
        
        result = await orchestrator.generate_documentation(
            files=files,
            doc_type=doc_type_enum,
            user_preferences=current_user.preferences
        )
        
        if result["success"]:
            job.status = DocStatus.COMPLETED
            job.generated_content = result["documentation"]
            job.quality_score = result.get("quality_score")
            job.completed_at = datetime.utcnow()
        else:
            job.status = DocStatus.FAILED
            job.error_message = result.get("error")
        
        await db.commit()
        
        return {
            "job_id": str(job.id),
            "status": job.status.value,
            "documentation": result.get("documentation"),
            "analysis": result.get("analysis")
        }
        
    except Exception as e:
        logger.error("Documentation generation error", error=str(e))
        job.status = DocStatus.FAILED
        job.error_message = str(e)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Documentation generation failed"
        )

async def stream_documentation_generation(
    files: Dict[str, str],
    doc_type: DocumentationType,
    job_id: Any,
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    """Stream documentation generation updates"""
    try:
        orchestrator = get_agent_orchestrator()
        
        async for update in orchestrator.stream_documentation(files, doc_type):
            data = {
                "step": update["step"],
                "content": update["documentation"],
                "complete": update["complete"]
            }
            yield f"data: {json.dumps(data)}\n\n"
            
            # Small delay to prevent overwhelming the client
            await asyncio.sleep(0.05)
        
        # Final update
        yield f"data: {json.dumps({'complete': True})}\n\n"
        
    except Exception as e:
        logger.error("Stream error", error=str(e))
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.get("/api/documentation/jobs")
async def list_documentation_jobs(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List documentation generation jobs"""
    result = await db.execute(
        select(DocumentationJob)
        .where(DocumentationJob.user_id == current_user.id)
        .order_by(desc(DocumentationJob.created_at))
        .limit(limit)
    )
    jobs = result.scalars().all()
    
    return [
        {
            "id": str(j.id),
            "doc_type": j.doc_type,
            "status": j.status.value,
            "file_count": len(j.file_paths),
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            "pr_created": j.pr_created,
            "pr_url": j.pr_url
        }
        for j in jobs
    ]

@app.get("/api/documentation/{job_id}")
async def get_documentation(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get generated documentation by job ID"""
    from uuid import UUID
    
    result = await db.execute(
        select(DocumentationJob).where(
            DocumentationJob.id == UUID(job_id),
            DocumentationJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documentation job not found"
        )
    
    return {
        "id": str(job.id),
        "doc_type": job.doc_type,
        "status": job.status.value,
        "documentation": job.generated_content,
        "analysis": job.agent_steps,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    }

# ============================================================================
# File Upload Endpoints
# ============================================================================

@app.post("/api/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload code files for processing"""
    uploaded = {}
    errors = []
    
    SUPPORTED_EXTENSIONS = {
        'py', 'js', 'ts', 'jsx', 'tsx', 'java', 'c', 'cpp', 'cs', 
        'go', 'rs', 'php', 'rb', 'swift', 'kt', 'scala', 'r', 'm', 'mm'
    }
    
    for file in files:
        ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if ext not in SUPPORTED_EXTENSIONS:
            errors.append(f"{file.filename}: Unsupported file type")
            continue
        
        try:
            content = await file.read()
            text_content = content.decode('utf-8', errors='ignore')
            
            # Size limit: 1MB
            if len(content) > 1024 * 1024:
                errors.append(f"{file.filename}: File too large (max 1MB)")
                continue
            
            uploaded[file.filename] = text_content
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
        finally:
            await file.close()
    
    return {
        "success": len(uploaded) > 0,
        "files": uploaded,
        "file_count": len(uploaded),
        "errors": errors if errors else None
    }

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
