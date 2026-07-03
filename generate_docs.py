import os

docs_dir = "docs"
os.makedirs(docs_dir, exist_ok=True)

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# .env.example
write_file(".env.example", """
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/edudeck

# Security
SECRET_KEY=secret
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
PRIMARY_LLM_MODEL=gpt-4o
PRIMARY_EMBEDDING_MODEL=text-embedding-3-small
""")

# RUN_PROJECT.md
write_file("RUN_PROJECT.md", """
# Running EduDeck AI

Follow these steps to set up and run the EduDeck AI backend from a fresh clone.

## 1. Prerequisites
- Python 3.10+ (Verified on 3.14.2)
- Docker & Docker Compose
- Git

## 2. Clone Repository
```bash
git clone https://github.com/DevanshGanatra/EduDeck-AI.git
cd EduDeck-AI
```

## 3. Create Virtual Environment
**Windows:**
```powershell
python -m venv venv
.\\venv\\Scripts\\activate
```
**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

## 5. Environment Variables
Copy `.env.example` to `.env` and fill in your OpenAI API Key.
```bash
cp .env.example .env
```

## 6. Start Infrastructure (Docker)
Start PostgreSQL and ChromaDB in the background:
```bash
docker compose up -d
```
*(Postgres runs on port 5432, ChromaDB runs on port 8000)*

## 7. Run Migrations (Alembic)
Ensure tables are created:
```bash
alembic upgrade head
```
*(If no alembic setup exists for MVP, tables will auto-create via SQLAlchemy on startup if configured)*

## 8. Start FastAPI Backend
Because ChromaDB occupies port 8000, we run FastAPI on port 8080:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## 9. Verify and Test
- **Swagger UI**: Visit `http://localhost:8080/docs`
- **Health Check**: `GET http://localhost:8080/api/v1/health`

## 10. Sample Workflow
1. Use `/api/v1/auth/register` to create a user.
2. Use `/api/v1/auth/login` to get a JWT token.
3. Click "Authorize" in Swagger to attach the token.
4. Create a project at `POST /api/v1/projects`.
5. Upload a PDF at `POST /api/v1/documents/upload`.
6. Vectorize at `POST /api/v1/retrieval/project/{id}/vectorize`.
7. Generate PPT at `POST /api/v1/generation/generate`.
""")

# README.md
write_file("README.md", """
# EduDeck AI

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-00a393)
![LangGraph](https://img.shields.io/badge/LangGraph-AI-orange)

EduDeck AI is an Agentic RAG-powered presentation generator. It ingests textbooks, extracts knowledge, chunks and vectorizes text, and uses LangGraph agents to orchestrate the planning and generation of cited, structured PowerPoint presentations.

## Features
- **Knowledge Ingestion**: Upload PDFs, chunk text semantically, and track quality metrics.
- **RAG Pipeline**: Vectorization using OpenAI and ChromaDB.
- **AI Agents**: LangGraph orchestrated Planner and Generator nodes.
- **Structured PPTX Export**: Native PowerPoint creation with speaker notes and citations.
- **Clean Architecture**: Strictly separated Service, Repository, and API layers.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy 2.0 (Async)
- **Database**: PostgreSQL (Relational), ChromaDB (Vector)
- **AI**: LangChain, LangGraph, OpenAI (gpt-4o, text-embedding-3-small)
- **Processing**: PyPDF, python-pptx

## Documentation
- [Run Project](RUN_PROJECT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Workflow](docs/WORKFLOW.md)
- [API Reference](docs/API_REFERENCE.md)
- [Database Details](docs/DATABASE.md)
- [AI Pipeline](docs/AI_PIPELINE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)

## License
MIT License
""")

# docs/ARCHITECTURE.md
write_file("docs/ARCHITECTURE.md", """
# Architecture

EduDeck AI follows **Clean Architecture** principles, decoupling business logic from HTTP transport and database layers.

## Layered Design
1. **API Router**: Validates Pydantic schemas and passes requests.
2. **Service Layer**: Pure Python logic containing business rules, LangGraph execution, and task orchestration.
3. **Repository Layer**: The only layer aware of SQLAlchemy sessions or ChromaDB clients.
4. **Database Models**: Declarative mapping for PostgreSQL.

## Mermaid Diagram
```mermaid
graph TD;
    Client-->Router;
    Router-->AuthService;
    Router-->ProjectService;
    Router-->DocumentService;
    Router-->GenerationService;
    
    GenerationService-->LangGraph;
    LangGraph-->RetrievalService;
    RetrievalService-->ChromaDBRepo;
    
    DocumentService-->DocumentRepo;
    DocumentService-->ChunkPersistenceService;
```
""")

# docs/WORKFLOW.md
write_file("docs/WORKFLOW.md", """
# Application Workflow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant DB
    participant Chroma
    participant OpenAI
    
    User->>API: Upload PDF
    API->>DB: Save Document (Validating)
    API-->>User: OK
    
    Note right of API: Background Task
    API->>API: Extract Text (PyPDF)
    API->>API: Chunk (Langchain)
    API->>DB: Save Chunks (Ready)
    
    User->>API: Vectorize
    API->>DB: Get Chunks
    API->>OpenAI: Embed (text-embedding-3-small)
    API->>Chroma: Save Vectors
    
    User->>API: Generate PPT
    API->>OpenAI: Planner Agent (gpt-4o)
    API->>Chroma: Retrieve Context (per slide)
    API->>OpenAI: Generator Agent (gpt-4o)
    API->>API: python-pptx Export
    API-->>User: Download URL
```
""")

# docs/TECH_STACK.md
write_file("docs/TECH_STACK.md", """
# Tech Stack

- **FastAPI**: High performance async web framework.
- **SQLAlchemy 2.0 (Async)**: ORM pattern mapping Python objects to Postgres tables.
- **PostgreSQL**: Relational storage for users, projects, documents, and chunks.
- **ChromaDB**: Local vector database for embedding storage and similarity search.
- **LangGraph**: Stateful multi-actor orchestration for our Planner -> Retriever -> Generator flow.
- **LangChain**: Tools for RecursiveCharacterTextSplitter and ChatPromptTemplate.
- **OpenAI SDK**: Provides access to GPT-4o and Text Embeddings.
- **python-pptx**: Generates actual binary PPTX files from Python objects without needing MS Office installed.
- **PyPDF**: Pure Python PDF parser used for knowledge extraction.
- **Passlib/Bcrypt/PyJWT**: Stateless JWT authentication handling.
""")

# docs/API_REFERENCE.md
write_file("docs/API_REFERENCE.md", """
# API Reference

*Note: Access complete Swagger documentation at `http://localhost:8080/docs`.*

### Authentication (`/api/v1/auth`)
- `POST /register`: Create new user.
- `POST /login`: OAuth2 Password Bearer login, returns JWT token.
- `GET /me`: Returns current user.

### Projects (`/api/v1/projects`)
- `POST /`: Create AI Workspace.
- `GET /`: List paginated projects.
- `GET /{id}`: Project dashboard metrics.
- `PATCH /{id}`: Update defaults.
- `POST /{id}/archive`: Soft delete/archive.

### Documents (`/api/v1/documents`)
- `POST /upload`: Multipart upload (PDF).
- `GET /{id}/progress`: Poll background extraction status.
- `GET /{id}/chunks`: Paginated knowledge viewing.
- `GET /{id}/chunks/search?q=`: Native ILIKE database text search.

### Retrieval (`/api/v1/retrieval`)
- `POST /project/{id}/vectorize`: Batch embed all chunks into ChromaDB.
- `POST /project/{id}/playground`: Top-K semantic similarity test.

### Generation (`/api/v1/generation`)
- `POST /generate`: Triggers end-to-end LangGraph pipeline. Returns PPTX download URL.
""")

# docs/DATABASE.md
write_file("docs/DATABASE.md", """
# Database Schema

## Core Entities
- **User**: Authentication layer.
- **Project**: Represents a workspace. Holds default AI settings (language, slide count, templates). Cascades delete to all children.
- **Document**: Represents an uploaded PDF. Holds extensive telemetry (total_pages, reading_time, processing durations, validation statuses).
- **DocumentChunk**: The granular text block. Stores `vector_reference` linking it to ChromaDB, alongside snippet indexes, page numbers, and text density quality metrics.
- **GenerationJob & Session**: Tracks AI usage and cost metrics.
- **Presentation & Slide**: Maps immutable exports for history.
""")

# docs/AI_PIPELINE.md
write_file("docs/AI_PIPELINE.md", """
# AI Pipeline (Agentic RAG)

## The Generation Loop
Instead of generating a monolithic presentation in a single prompt (which leads to context loss and hallucination), EduDeck AI utilizes a multi-step Graph:

1. **Planner Node**: Takes the user prompt and generates a strict JSON `PresentationOutline` containing Slide Titles and Topics.
2. **Contextual Retrieval**: We loop over the outline. For each slide topic, we query ChromaDB for the Top-3 nearest semantic chunks.
3. **Generator Node**: We supply the specific topic and specific retrieved context into GPT-4o, outputting a strict JSON `SlideContent` (Title, Bullets, Notes, References).
4. **Formatting**: If ChromaDB yields no context, a deterministic placeholder is injected to prevent the LLM from hallucinating facts not present in the Knowledge Base.
""")

# PROJECT_COMPLETION_REPORT.md
write_file("PROJECT_COMPLETION_REPORT.md", """
# Project Completion Report

## Status: Backend MVP Complete
The backend of EduDeck AI is finalized, heavily documented, and ready for open-source deployment and frontend integration.

## Features Completed
1. **JWT Authentication**: Secured middleware.
2. **Project Workspaces**: CRUD with soft-deletes and AI defaults.
3. **Knowledge Ingestion**: Async PDF parsing, LangChain recursive chunking, and Postgres metadata tracking.
4. **Knowledge Retrieval**: OpenAI vectorization, ChromaDB similarity search, and tenant isolation.
5. **Agentic Pipeline**: LangGraph orchestrated slide-by-slide generation.
6. **PPTX Export**: Dynamic assembly of slide elements including speaker notes and citations.

## Known Limitations
- The LangGraph pipeline currently runs synchronously within the HTTP request, which may cause timeouts on cloud balancers if generation exceeds 30s.
- OpenAI rate limits may be hit during massive textbook vectorization; batching logic requires delay mechanisms.

## Next Steps
- Implement frontend UI in React/Next.js.
- Migrate BackgroundTasks to Celery/RabbitMQ for production async scalability.
""")
