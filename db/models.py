"""
Database Models - 2026 Ready
SQLAlchemy 2.0 async models for PostgreSQL
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    String, Integer, Text, DateTime, Boolean, 
    ForeignKey, JSON, Enum, Float, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import uuid
import enum

class Base(DeclarativeBase):
    """Base class for all models"""
    pass

# ============================================================================
# Enums
# ============================================================================

class UserRole(enum.Enum):
    USER = "user"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"

class DocStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"

class IntegrationType(enum.Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    AZURE_DEVOPS = "azure_devops"

class AgentTaskStatus(enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# ============================================================================
# User Models
# ============================================================================

class User(Base):
    """User account with GitHub OAuth support"""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # OAuth
    github_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    github_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Encrypted
    github_token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    github_refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Encrypted
    
    # Account
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Preferences
    preferences: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship(back_populates="owner", lazy="selectin")
    documentation_jobs: Mapped[List["DocumentationJob"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    agent_tasks: Mapped[List["AgentTask"]] = relationship(back_populates="user", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<User {self.username}>"

# ============================================================================
# Project Models
# ============================================================================

class Project(Base):
    """Code project with metadata"""
    __tablename__ = "projects"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # GitHub Integration
    github_repo_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    github_repo_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    github_repo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    
    # Stats
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    total_lines: Mapped[int] = mapped_column(Integer, default=0)
    complexity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Settings
    settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    # Timestamps
    last_synced: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    owner: Mapped["User"] = relationship(back_populates="projects")
    files: Mapped[List["ProjectFile"]] = relationship(back_populates="project", lazy="selectin")
    documentation: Mapped[List["DocumentationJob"]] = relationship(
        back_populates="project", lazy="selectin"
    )
    
    __table_args__ = (
        Index('idx_project_owner', 'owner_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Project {self.name}>"

class ProjectFile(Base):
    """Individual file in a project"""
    __tablename__ = "project_files"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(20), nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Content (stored in object storage, reference here)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    content_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)  # S3/MinIO key
    
    # Analysis
    ast_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    complexity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lines_of_code: Mapped[int] = mapped_column(Integer, default=0)
    function_count: Mapped[int] = mapped_column(Integer, default=0)
    class_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Embeddings (for semantic search)
    embedding_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="files")
    
    __table_args__ = (
        Index('idx_file_project', 'project_id', 'path'),
        Index('idx_file_language', 'language'),
    )

# ============================================================================
# Documentation Models
# ============================================================================

class DocumentationJob(Base):
    """Documentation generation job"""
    __tablename__ = "documentation_jobs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )
    
    # Job config
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)  # readme, api, etc.
    status: Mapped[DocStatus] = mapped_column(Enum(DocStatus), default=DocStatus.PENDING)
    
    # Files included
    file_paths: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    
    # Input/Output
    input_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_format: Mapped[str] = mapped_column(String(20), default="markdown")
    
    # Quality metrics
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    generation_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Agent workflow tracking
    agent_workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    agent_steps: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # PR Integration
    pr_created: Mapped[bool] = mapped_column(Boolean, default=False)
    pr_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="documentation_jobs")
    project: Mapped[Optional["Project"]] = relationship(back_populates="documentation")
    
    __table_args__ = (
        Index('idx_doc_user_status', 'user_id', 'status'),
        Index('idx_doc_project', 'project_id'),
    )

# ============================================================================
# Agent Task Models
# ============================================================================

class AgentTask(Base):
    """Individual agent task for tracking and debugging"""
    __tablename__ = "agent_tasks"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[AgentTaskStatus] = mapped_column(
        Enum(AgentTaskStatus), default=AgentTaskStatus.QUEUED
    )
    
    # Input/Output
    input_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # LangGraph state
    graph_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    current_node: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Metrics
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Error
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="agent_tasks")

# ============================================================================
# Integration Models
# ============================================================================

class Integration(Base):
    """Third-party service integrations"""
    __tablename__ = "integrations"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    
    integration_type: Mapped[IntegrationType] = mapped_column(Enum(IntegrationType), nullable=False)
    
    # OAuth tokens (encrypted)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # External IDs
    external_user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_username: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Org/Team info
    organizations: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    
    # Settings
    settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_integration_user', 'user_id', 'integration_type'),
    )

class UsageLog(Base):
    """Track API usage for billing and analytics"""
    __tablename__ = "usage_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Usage metrics
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    tokens_total: Mapped[int] = mapped_column(Integer, default=0)
    
    # Performance
    response_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    status_code: Mapped[int] = mapped_column(Integer, default=200)
    
    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_usage_user', 'user_id', 'created_at'),
        Index('idx_usage_endpoint', 'endpoint', 'created_at'),
    )
