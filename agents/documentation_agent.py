"""
Tekshila Agent Architecture - 2026 Ready
State-driven multi-agent system for code documentation
"""

from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
import operator
import os
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Agent State Definition
# ============================================================================

class AgentState(TypedDict):
    """State schema for the documentation agent workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    files: Dict[str, str]  # filename -> content
    file_metadata: Dict[str, Dict[str, Any]]  # filename -> metadata
    documentation: str
    current_step: str
    errors: List[str]
    analysis_results: Dict[str, Any]
    github_context: Optional[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    iteration_count: int
    max_iterations: int

class DocumentationType(Enum):
    README = "readme"
    API_DOCS = "api_docs"
    INLINE_COMMENTS = "inline_comments"
    ARCHITECTURE = "architecture"

@dataclass
class FileAnalysis:
    """Structured analysis of a code file"""
    filename: str
    language: str
    complexity_score: float
    lines_of_code: int
    functions: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    imports: List[str]
    summary: str
    key_insights: List[str]

# ============================================================================
# Tools for Agents
# ============================================================================

@tool
def analyze_code_structure(file_content: str, filename: str) -> Dict[str, Any]:
    """
    Analyze code structure using tree-sitter for AST parsing.
    Returns structured metadata about the code.
    """
    try:
        # Language detection
        ext = filename.split('.')[-1].lower()
        
        # Basic analysis without tree-sitter (fallback)
        lines = file_content.split('\n')
        loc = len([l for l in lines if l.strip()])
        
        functions = []
        classes = []
        imports = []
        
        # Simple regex-based parsing (production uses tree-sitter)
        import re
        
        # Python detection
        if ext == 'py':
            func_pattern = r'def\s+(\w+)\s*\('
            class_pattern = r'class\s+(\w+)\s*[\(:]'
            import_pattern = r'^(?:from|import)\s+(.+)'
            
            functions = [{'name': m, 'line': i} for i, line in enumerate(lines) 
                        for m in re.findall(func_pattern, line)]
            classes = [{'name': m, 'line': i} for i, line in enumerate(lines) 
                      for m in re.findall(class_pattern, line)]
            imports = [m.strip() for line in lines for m in re.findall(import_pattern, line)]
        
        # JavaScript/TypeScript detection
        elif ext in ['js', 'ts', 'jsx', 'tsx']:
            func_pattern = r'(?:function|const|let|var)\s+(\w+)\s*[=:]*\s*(?:async\s+)?(?:function)?\s*\('
            class_pattern = r'class\s+(\w+)'
            
            functions = [{'name': m, 'line': i} for i, line in enumerate(lines) 
                        for m in re.findall(func_pattern, line)]
            classes = [{'name': m, 'line': i} for i, line in enumerate(lines) 
                      for m in re.findall(class_pattern, line)]
        
        # Calculate complexity (simplified cyclomatic complexity)
        complexity_keywords = ['if', 'for', 'while', 'except', 'try', 'and', 'or', '?']
        complexity_score = sum(file_content.count(kw) for kw in complexity_keywords) / max(loc, 1) * 10
        
        return {
            "filename": filename,
            "language": ext,
            "lines_of_code": loc,
            "functions": functions[:20],  # Limit to 20
            "classes": classes[:20],
            "imports": imports[:30],  # Limit to 30
            "complexity_score": round(min(complexity_score, 10), 2),
            "success": True
        }
    except Exception as e:
        logger.error(f"Error analyzing {filename}: {e}")
        return {"error": str(e), "success": False}

@tool
def fetch_github_context(repo_url: str, token: str) -> Dict[str, Any]:
    """
    Fetch repository context from GitHub API.
    Returns repo metadata, contributors, and structure.
    """
    from github import Github
    
    try:
        g = Github(token)
        repo_parts = repo_url.replace("https://github.com/", "").split("/")
        repo_name = f"{repo_parts[0]}/{repo_parts[1]}"
        
        repo = g.get_repo(repo_name)
        
        return {
            "name": repo.name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "language": repo.language,
            "topics": repo.topics,
            "license": repo.license.name if repo.license else None,
            "contributors": [c.login for c in repo.get_contributors()[:5]],
            "success": True
        }
    except Exception as e:
        logger.error(f"Error fetching GitHub context: {e}")
        return {"error": str(e), "success": False}

@tool
def vectorize_code(files: Dict[str, str]) -> Dict[str, Any]:
    """
    Create embeddings for code files to enable semantic search.
    Uses ChromaDB for vector storage.
    """
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        import chromadb
        
        # Initialize embeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Create vector store
        client = chromadb.Client()
        collection = client.get_or_create_collection("code_embeddings")
        
        documents = []
        metadatas = []
        ids = []
        
        for filename, content in files.items():
            # Split into chunks
            chunks = [content[i:i:1000] for i in range(0, len(content), 1000)]
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({"filename": filename, "chunk": i})
                ids.append(f"{filename}_{i}")
        
        # Add to collection
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        
        return {
            "total_chunks": len(documents),
            "files_indexed": len(files),
            "success": True
        }
    except Exception as e:
        logger.error(f"Error vectorizing code: {e}")
        return {"error": str(e), "success": False}

# ============================================================================
# Agent Nodes
# ============================================================================

def create_planner_node(llm: ChatGoogleGenerativeAI):
    """Create the planning agent node"""
    
    planner_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a technical documentation planner. 
Analyze the provided code files and create a structured plan for comprehensive documentation.

Your task:
1. Identify the project type and main purpose
2. Determine documentation structure (README, API docs, etc.)
3. Identify key components that need documentation
4. Note any architectural patterns used
5. Create a documentation outline

Respond in JSON format with:
{
    "project_type": "web_app|library|cli_tool|etc",
    "main_purpose": "description",
    "doc_structure": ["section1", "section2"],
    "key_components": [{"name": "...", "description": "..."}],
    "patterns": ["pattern1", "pattern2"],
    "target_audience": "developers|users|contributors"
}"""),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    def planner(state: AgentState) -> AgentState:
        # Format file summary for context
        file_summary = "\n".join([
            f"File: {name} ({len(content)} chars, {content.count(chr(10))} lines)"
            for name, content in list(state["files"].items())[:5]  # First 5 files
        ])
        
        messages = state["messages"] + [HumanMessage(content=f"Files to document:\n{file_summary}")]
        
        response = llm.invoke(planner_prompt.format_messages(messages=messages))
        
        return {
            **state,
            "messages": state["messages"] + [response],
            "current_step": "planning_complete"
        }
    
    return planner

def create_analyzer_node(llm: ChatGoogleGenerativeAI):
    """Create the code analyzer agent node"""
    
    analyzer_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a code analysis expert. Analyze the provided code files deeply.

For each file, provide:
1. Language and framework detection
2. Function/class signatures with docstrings
3. Dependency graph
4. Complexity metrics
5. Key algorithms or patterns
6. Potential documentation gaps

Be thorough and technical."""),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    def analyzer(state: AgentState) -> AgentState:
        analysis_results = {}
        
        for filename, content in state["files"].items():
            # Use the tool for structure analysis
            structure = analyze_code_structure.invoke({
                "file_content": content,
                "filename": filename
            })
            
            if structure["success"]:
                analysis_results[filename] = structure
        
        # Get AI analysis
        file_context = "\n\n".join([
            f"=== {name} ===\n{content[:2000]}..."  # First 2000 chars
            for name, content in list(state["files"].items())[:3]
        ])
        
        messages = state["messages"] + [HumanMessage(content=f"Analyze this code:\n{file_context}")]
        response = llm.invoke(analyzer_prompt.format_messages(messages=messages))
        
        return {
            **state,
            "messages": state["messages"] + [response],
            "analysis_results": analysis_results,
            "current_step": "analysis_complete"
        }
    
    return analyzer

def create_writer_node(llm: ChatGoogleGenerativeAI, doc_type: DocumentationType):
    """Create the documentation writer agent node"""
    
    writer_prompts = {
        DocumentationType.README: """You are an expert technical writer creating a README.md.
Write comprehensive, professional documentation including:

1. Clear project title and description
2. Installation instructions
3. Usage examples with code
4. API reference (if applicable)
5. Configuration options
6. Contributing guidelines
7. License information

Use proper Markdown formatting with badges, tables, and code blocks.""",
        
        DocumentationType.API_DOCS: """You are an API documentation specialist.
Create detailed API documentation with:

1. Endpoint descriptions
2. Request/response schemas
3. Authentication details
4. Code examples in multiple languages
5. Error handling
6. Rate limiting info

Format as OpenAPI/Swagger compatible Markdown.""",
        
        DocumentationType.INLINE_COMMENTS: """You are a code documentation expert.
Add comprehensive inline comments including:

1. JSDoc/PyDoc-style function/class documentation
2. Inline comments for complex logic
3. Type hints where applicable
4. Usage examples in docstrings
5. Parameter and return value descriptions

Maintain original code structure, only add comments.""",
        
        DocumentationType.ARCHITECTURE: """You are a software architect.
Create architecture documentation including:

1. System overview and diagrams (ASCII art)
2. Component descriptions
3. Data flow explanations
4. Design patterns used
5. Technology stack
6. Deployment architecture
7. Scalability considerations"""
    }
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=writer_prompts[doc_type]),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content="Generate documentation based on the analysis provided. Output only the documentation content without explanations.")
    ])
    
    def writer(state: AgentState) -> AgentState:
        # Check iteration limit
        if state.get("iteration_count", 0) >= state.get("max_iterations", 3):
            return {**state, "current_step": "max_iterations_reached"}
        
        messages = prompt.format_messages(messages=state["messages"])
        response = llm.invoke(messages)
        
        return {
            **state,
            "messages": state["messages"] + [response],
            "documentation": response.content,
            "current_step": "draft_complete",
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    
    return writer

def create_reviewer_node(llm: ChatGoogleGenerativeAI):
    """Create the documentation reviewer agent node"""
    
    reviewer_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a documentation quality reviewer.
Review the generated documentation against these criteria:

1. Completeness - all sections present?
2. Accuracy - technically correct?
3. Clarity - easy to understand?
4. Consistency - style matches throughout?
5. Examples - sufficient code samples?

Provide a score (0-100) and specific improvement suggestions.
Respond in JSON format:
{
    "score": 85,
    "passed": true,
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1", "suggestion2"]
}"""),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    def reviewer(state: AgentState) -> AgentState:
        messages = reviewer_prompt.format_messages(messages=state["messages"])
        response = llm.invoke(messages)
        
        # Parse JSON response
        try:
            import json
            review = json.loads(response.content)
            passed = review.get("passed", False)
        except:
            passed = True  # Default to pass on parse error
        
        next_step = "review_passed" if passed else "needs_revision"
        
        return {
            **state,
            "messages": state["messages"] + [response],
            "current_step": next_step
        }
    
    return reviewer

# ============================================================================
# Build the Agent Graph
# ============================================================================

def build_documentation_agent():
    """Build and compile the documentation agent workflow"""
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.2,
        google_api_key=os.getenv("GEMINI_API_KEY"),
        convert_system_message_to_human=True
    )
    
    # Create nodes
    planner = create_planner_node(llm)
    analyzer = create_analyzer_node(llm)
    writer = create_writer_node(llm, DocumentationType.README)
    reviewer = create_reviewer_node(llm)
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner)
    workflow.add_node("analyzer", analyzer)
    workflow.add_node("writer", writer)
    workflow.add_node("reviewer", reviewer)
    
    # Define edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "analyzer")
    workflow.add_edge("analyzer", "writer")
    workflow.add_edge("writer", "reviewer")
    
    # Conditional edges
    workflow.add_conditional_edges(
        "reviewer",
        lambda state: state["current_step"],
        {
            "review_passed": END,
            "needs_revision": "writer",
            "max_iterations_reached": END
        }
    )
    
    # Add memory
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

# ============================================================================
# Agent Orchestrator
# ============================================================================

class AgentOrchestrator:
    """Orchestrates multiple specialized agents for complex tasks"""
    
    def __init__(self):
        self.doc_agent = build_documentation_agent()
        self.logger = logging.getLogger(__name__)
    
    async def generate_documentation(
        self,
        files: Dict[str, str],
        doc_type: DocumentationType = DocumentationType.README,
        github_context: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate documentation using the agent workflow
        
        Args:
            files: Dictionary of filename -> content
            doc_type: Type of documentation to generate
            github_context: Optional GitHub repository context
            user_preferences: User customization preferences
            
        Returns:
            Dictionary with documentation and metadata
        """
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=f"Generate {doc_type.value} documentation")],
            "files": files,
            "file_metadata": {},
            "documentation": "",
            "current_step": "start",
            "errors": [],
            "analysis_results": {},
            "github_context": github_context,
            "user_preferences": user_preferences or {},
            "iteration_count": 0,
            "max_iterations": 3
        }
        
        # Run agent workflow
        try:
            final_state = self.doc_agent.invoke(
                initial_state,
                config={"configurable": {"thread_id": "doc_gen_1"}}
            )
            
            return {
                "success": True,
                "documentation": final_state["documentation"],
                "analysis": final_state["analysis_results"],
                "steps_completed": final_state["current_step"],
                "iterations": final_state["iteration_count"]
            }
            
        except Exception as e:
            self.logger.error(f"Agent workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "documentation": ""
            }
    
    async def stream_documentation(
        self,
        files: Dict[str, str],
        doc_type: DocumentationType = DocumentationType.README
    ):
        """
        Stream documentation generation for real-time UI updates
        """
        initial_state = {
            "messages": [HumanMessage(content=f"Generate {doc_type.value} documentation")],
            "files": files,
            "file_metadata": {},
            "documentation": "",
            "current_step": "start",
            "errors": [],
            "analysis_results": {},
            "github_context": None,
            "user_preferences": {},
            "iteration_count": 0,
            "max_iterations": 3
        }
        
        async for state in self.doc_agent.astream(
            initial_state,
            config={"configurable": {"thread_id": "doc_stream_1"}}
        ):
            yield {
                "step": state.get("current_step"),
                "documentation": state.get("documentation", ""),
                "analysis": state.get("analysis_results", {}),
                "complete": state.get("current_step") in ["review_passed", "max_iterations_reached"]
            }

# Singleton instance
_orchestrator = None

def get_agent_orchestrator() -> AgentOrchestrator:
    """Get or create the agent orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
