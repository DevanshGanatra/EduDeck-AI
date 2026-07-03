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
